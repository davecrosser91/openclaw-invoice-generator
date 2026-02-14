#!/usr/bin/env python3
"""
Fix existing HTML files by applying the empty rows cleanup.

This script loads each HTML file and its corresponding JSON,
then applies the cleanup logic from TemplatePlaceholderMapper.
"""

import json
import re
from pathlib import Path
from tqdm import tqdm


def clean_empty_rows(html: str, product_count: int) -> str:
    """
    Clean up empty product rows in table-based templates.
    Handles templates with mb-1 through mb-5 classes and multi-line descriptions.
    """
    if product_count >= 10:
        return html

    # Remove obvious empty pre tags first
    html = re.sub(r'<pre[^>]*>\s*€\s*</pre>\s*', '', html)
    html = re.sub(r'<pre[^>]*>\s*<span[^>]*>\s*\(\s*\)\s*</span>\s*</pre>\s*', '', html)
    html = re.sub(r'<pre[^>]*>\s*</pre>\s*', '', html)
    html = re.sub(r'<pre[^>]*>\s*&nbsp;\s*</pre>\s*', '', html)

    # Find all divs and trim those with more pre tags than products
    div_pattern = r'(<div[^>]*class="textbox[^"]*"[^>]*>)([\s\S]*?)(</div>)'

    def trim_table_column(match):
        div_start = match.group(1)
        div_content = match.group(2)
        div_end = match.group(3)

        # Match pre tags with any margin class (mb-1 through mb-5, my-1 through my-5)
        pre_pattern_with_margin = r'<pre[^>]*class="[^"]*m[by]-[0-9.]+[^"]*"[^>]*>[\s\S]*?</pre>'
        pre_tags = list(re.finditer(pre_pattern_with_margin, div_content))

        # If found pre tags with mb class, trim to product_count
        if len(pre_tags) > product_count:
            new_content = div_content[:pre_tags[0].start()]
            for i, pre_match in enumerate(pre_tags[:product_count]):
                if i > 0:
                    new_content += '\n    '
                new_content += pre_match.group(0)
            new_content += '\n    '
            return div_start + new_content + div_end

        # Also check for pre tags without mb class (description columns)
        # These often have multiple lines per product (name, article-nr, serial)
        pre_pattern_no_mb = r'<pre[^>]*class="text-\[\d+px\]"[^>]*>[\s\S]*?</pre>'
        pre_tags_no_mb = list(re.finditer(pre_pattern_no_mb, div_content))

        # If this looks like a multi-line product description (30 tags = 10 products * 3 lines)
        if len(pre_tags_no_mb) >= 15:  # At least 5 products * 3 lines
            lines_per_product = 3  # name, article-nr, serial number
            expected_tags = product_count * lines_per_product
            if len(pre_tags_no_mb) > expected_tags:
                new_content = div_content[:pre_tags_no_mb[0].start()]
                for i, pre_match in enumerate(pre_tags_no_mb[:expected_tags]):
                    if i > 0:
                        new_content += '\n    '
                    new_content += pre_match.group(0)
                return div_start + new_content + div_end

        return match.group(0)

    html = re.sub(div_pattern, trim_table_column, html)
    html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)

    return html


def remove_unfilled_placeholders(html: str) -> str:
    """Remove any remaining unfilled placeholders."""
    # Standard placeholders: {placeholder_name}
    html = re.sub(r'\{[a-z][a-z0-9_]*\}', '', html)
    # Malformed placeholders missing closing brace
    html = re.sub(r'\{[a-z][a-z0-9_]*(?=<|$|\s*$)', '', html)
    # Placeholders with numbers at different positions
    html = re.sub(r'\{[a-z_]*\d+[a-z_]*\}?', '', html)
    return html


def fix_overlapping_elements(html: str) -> str:
    """
    Detect and fix overlapping text elements by adjusting positions.
    """
    # Run multiple passes to handle cascading overlaps
    for _ in range(3):
        html = fix_overlapping_elements_pass(html)
    return html


def fix_overlapping_elements_pass(html: str) -> str:
    """Single pass of overlap detection and fixing."""
    # Parse all positioned elements
    elements = []
    div_pattern = r'<div[^>]*class="textbox\s+bottom-\[(\d+)px\]\s+(left-\[(\d+)px\]|right-\[(\d+)px\])[^"]*"[^>]*>(.*?)</div>'

    for match in re.finditer(div_pattern, html, re.DOTALL):
        bottom = int(match.group(1))
        left = int(match.group(3)) if match.group(3) else None
        right = int(match.group(4)) if match.group(4) else None
        content = match.group(5).strip()

        # Extract font size from content
        font_match = re.search(r'text-\[(\d+)px\]', content)
        font_size = int(font_match.group(1)) if font_match else 10

        # Determine if this is a table data element (has mb-1/mb-2/my-*)
        is_table_data = bool(re.search(r'm[by]-[0-9]', content))

        # Calculate height based on element type
        if is_table_data:
            pre_count = len(re.findall(r'<pre[^>]*>', content))
            pre_count = max(pre_count, 1)
            height = pre_count * (font_size + 6)
        else:
            text_content = re.sub(r'<[^>]+>', '', content)
            lines = len([l for l in text_content.split('\n') if l.strip()])
            lines = max(lines, 1)
            height = lines * (font_size + 4)

        elements.append({
            'bottom': bottom,
            'top': bottom + height,
            'left': left,
            'right': right,
            'height': height,
            'original_bottom': bottom,
            'h_pos': left if left is not None else (595 - right if right is not None else 0),
            'is_table_data': is_table_data,
        })

    if len(elements) < 2:
        return html

    # Separate table and non-table elements
    table_elements = [e for e in elements if e['is_table_data']]
    non_table_elements = [e for e in elements if not e['is_table_data']]

    if not non_table_elements:
        return html

    adjustments = {}
    min_clearance = 20  # Minimum pixels between elements

    # NOTE: We no longer try to move non-table elements away from table data
    # because it often causes more problems (moving into header areas).
    # The original template positioning should be preserved for table-related elements.

    # Only check overlaps between non-table elements
    sorted_elements = sorted(non_table_elements, key=lambda x: x['bottom'], reverse=True)

    for i, e1 in enumerate(sorted_elements):
        for e2 in sorted_elements[i+1:]:
            # Elements within 5px vertical are "same row" - not overlaps
            if abs(e1['bottom'] - e2['bottom']) <= 5:
                continue

            # Check if horizontally close (within 100px)
            if abs(e1['h_pos'] - e2['h_pos']) >= 100:
                continue

            # Check if vertically overlapping or too close
            gap = e1['bottom'] - e2['top'] if e1['bottom'] > e2['bottom'] else e2['bottom'] - e1['top']

            if gap < min_clearance:
                # Move the LOWER element (smaller bottom) down
                lower_elem = e2 if e2['bottom'] < e1['bottom'] else e1
                higher_elem = e1 if e2['bottom'] < e1['bottom'] else e2

                # Calculate new position: just below the higher element with clearance
                new_bottom = higher_elem['bottom'] - lower_elem['height'] - min_clearance

                # Don't push elements too low
                if new_bottom < 80:
                    continue

                old_bottom = lower_elem['original_bottom']

                if old_bottom not in adjustments and abs(old_bottom - new_bottom) > 3:
                    adjustments[old_bottom] = new_bottom
                    lower_elem['bottom'] = new_bottom
                    lower_elem['top'] = new_bottom + lower_elem['height']

    # Apply adjustments to HTML
    for old_bottom, new_bottom in adjustments.items():
        html = re.sub(
            rf'(class="textbox bottom-\[){old_bottom}(px\])',
            rf'\g<1>{new_bottom}\g<2>',
            html
        )

    return html


def fix_html_file(html_path: Path, json_path: Path) -> bool:
    """Fix a single HTML file."""
    try:
        # Load JSON to get product count
        with open(json_path, 'r', encoding='utf-8') as f:
            invoice_data = json.load(f)

        product_count = len(invoice_data.get('products', []))

        # Load HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # Apply fixes
        fixed_html = clean_empty_rows(html, product_count)
        fixed_html = remove_unfilled_placeholders(fixed_html)
        fixed_html = fix_overlapping_elements(fixed_html)

        # Save fixed HTML
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(fixed_html)

        return True
    except Exception as e:
        print(f"Error fixing {html_path.name}: {e}")
        return False


def main():
    """Fix all HTML files in the invoices_141_fixed_v4 directory."""
    base_dir = Path("gen_data/invoices_141_fixed_v4")
    html_dir = base_dir / "html"
    json_dir = base_dir / "json"

    html_files = sorted(html_dir.glob("*.html"), key=lambda p: int(p.stem.split('_')[1]))

    print(f"Found {len(html_files)} HTML files to fix")
    print("=" * 60)

    successful = 0
    failed = []

    for html_path in tqdm(html_files, desc="Fixing HTML files"):
        json_path = json_dir / html_path.name.replace('.html', '.json')

        if not json_path.exists():
            print(f"Warning: No JSON for {html_path.name}")
            failed.append(html_path.name)
            continue

        if fix_html_file(html_path, json_path):
            successful += 1
        else:
            failed.append(html_path.name)

    print("\n" + "=" * 60)
    print(f"Done! Fixed: {successful}, Failed: {len(failed)}")

    if failed:
        print(f"\nFailed files:")
        for f in failed:
            print(f"  - {f}")


if __name__ == "__main__":
    main()
