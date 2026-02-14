#!/usr/bin/env python3
"""
Convert absolute-positioned invoice templates to hybrid templates.

This script converts templates from using absolute positioning for everything
to using HTML tables for product rows while keeping headers/footers absolute.
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
from bs4 import BeautifulSoup
import copy


@dataclass
class TableColumn:
    """Represents a column in the product table."""
    position: int  # left-[X] or right-[X] value
    is_right_aligned: bool  # True if right-[X], False if left-[X]
    header_text: str = ""
    header_bottom: int = 0
    data_items: list = field(default_factory=list)  # List of text values
    width_px: int = 0


@dataclass
class TableElement:
    """Represents an absolutely positioned element that's part of a table."""
    bottom: int
    left: Optional[int]
    right: Optional[int]
    content: str
    is_header: bool
    is_table_data: bool
    element: object  # BeautifulSoup element
    font_size: int = 8


def parse_position(element) -> tuple:
    """Extract bottom, left, right positions from element classes."""
    classes = element.get('class', [])
    class_str = ' '.join(classes) if isinstance(classes, list) else classes

    bottom_match = re.search(r'bottom-\[(\d+)px\]', class_str)
    left_match = re.search(r'left-\[(\d+)px\]', class_str)
    right_match = re.search(r'right-\[(\d+)px\]', class_str)

    bottom = int(bottom_match.group(1)) if bottom_match else None
    left = int(left_match.group(1)) if left_match else None
    right = int(right_match.group(1)) if right_match else None

    return bottom, left, right


def is_table_data_element(element) -> bool:
    """Check if element contains table data (has mb-* classes in pre tags)."""
    content = str(element)
    return bool(re.search(r'm[by]-[0-9]', content))


def extract_pre_contents(element) -> list:
    """Extract text from all pre tags in element."""
    pre_tags = element.find_all('pre')
    contents = []
    for pre in pre_tags:
        text = pre.get_text(strip=True)
        if text:
            contents.append(text)
    return contents


def get_font_size(element) -> int:
    """Extract font size from element content."""
    content = str(element)
    match = re.search(r'text-\[(\d+)px\]', content)
    return int(match.group(1)) if match else 8


def analyze_template(soup) -> dict:
    """Analyze template structure and identify table components."""
    body = soup.find('body')
    if not body:
        return None

    textboxes = body.find_all('div', class_=lambda c: c and 'textbox' in c)

    # Separate table data elements from others
    table_data_elements = []
    other_elements = []

    for elem in textboxes:
        bottom, left, right = parse_position(elem)
        if bottom is None:
            other_elements.append(elem)
            continue

        if is_table_data_element(elem):
            table_data_elements.append(TableElement(
                bottom=bottom,
                left=left,
                right=right,
                content=str(elem),
                is_header=False,
                is_table_data=True,
                element=elem,
                font_size=get_font_size(elem)
            ))
        else:
            other_elements.append(elem)

    if not table_data_elements:
        return None

    # Find the table data area (all should be at same bottom position)
    table_bottoms = set(e.bottom for e in table_data_elements)
    main_table_bottom = max(table_bottoms)  # Usually all at same position

    # Group table data by horizontal position
    columns = {}
    for elem in table_data_elements:
        if elem.bottom != main_table_bottom:
            continue
        pos_key = ('left', elem.left) if elem.left is not None else ('right', elem.right)
        if pos_key not in columns:
            columns[pos_key] = TableColumn(
                position=pos_key[1],
                is_right_aligned=(pos_key[0] == 'right'),
                data_items=extract_pre_contents(elem.element)
            )
        else:
            columns[pos_key].data_items.extend(extract_pre_contents(elem.element))

    # Find potential headers (elements above table data)
    # Headers are typically at a consistent bottom position and have short text
    header_candidates = []
    for elem in other_elements:
        bottom, left, right = parse_position(elem)
        if bottom is None:
            continue
        # Headers are above table data (higher bottom value) and within 100px
        if bottom > main_table_bottom and bottom < main_table_bottom + 100:
            text = elem.get_text(strip=True)
            # Skip long text (likely notes, not headers) - headers are usually < 50 chars
            if len(text) > 50:
                continue
            header_candidates.append({
                'element': elem,
                'bottom': bottom,
                'left': left,
                'right': right,
                'text': text,
                'font_size': get_font_size(elem)
            })

    # Group headers by bottom position to find the main header row
    if header_candidates:
        bottom_counts = {}
        for h in header_candidates:
            b = h['bottom']
            # Group within 10px
            key = (b // 10) * 10
            bottom_counts[key] = bottom_counts.get(key, 0) + 1

        # Find the most common bottom position (that's the header row)
        main_header_bottom = max(bottom_counts.keys(), key=lambda k: bottom_counts[k])
        # Filter to only headers at that position (within 10px)
        header_candidates = [h for h in header_candidates
                           if abs(h['bottom'] - main_header_bottom) <= 15]

    # Match headers to columns by position
    for pos_key, col in columns.items():
        best_header = None
        best_distance = float('inf')

        for h in header_candidates:
            if col.is_right_aligned and h['right'] is not None:
                dist = abs(h['right'] - col.position)
                if dist < best_distance and dist < 30:
                    best_distance = dist
                    best_header = h
            elif not col.is_right_aligned and h['left'] is not None:
                dist = abs(h['left'] - col.position)
                if dist < best_distance and dist < 30:
                    best_distance = dist
                    best_header = h

        if best_header:
            col.header_text = best_header['text']
            col.header_bottom = best_header['bottom']

    # Sort columns by position (left to right)
    sorted_columns = sorted(columns.values(),
                           key=lambda c: c.position if not c.is_right_aligned else (1000 - c.position))

    # Calculate column widths based on positions
    calculate_column_widths(sorted_columns)

    return {
        'columns': sorted_columns,
        'table_bottom': main_table_bottom,
        'table_data_elements': table_data_elements,
        'header_candidates': header_candidates,
        'header_bottom': max(h['bottom'] for h in header_candidates) if header_candidates else main_table_bottom + 30
    }


def calculate_column_widths(columns: list):
    """Calculate approximate column widths."""
    if not columns:
        return

    # Simple heuristic: divide 483px (table width) among columns
    total_width = 483
    num_cols = len(columns)

    # Give more space to description columns (usually 3rd column)
    base_width = total_width // num_cols
    for i, col in enumerate(columns):
        if i == 2:  # Description column usually
            col.width_px = base_width + 40
        elif i < 2:  # Position, SKU columns
            col.width_px = base_width - 10
        else:
            col.width_px = base_width


def generate_table_html(analysis: dict, num_products: int) -> str:
    """Generate HTML table from analysis."""
    columns = analysis['columns']

    if not columns:
        return ""

    # Start table
    html = ['<table class="invoice-table">']

    # Generate thead
    html.append('  <thead>')
    html.append('    <tr>')
    for col in columns:
        align_class = ' class="text-right"' if col.is_right_aligned else ''
        header = col.header_text.replace('\n', '<br>') if col.header_text else '&nbsp;'
        html.append(f'      <th style="width: {col.width_px}px;"{align_class}>{header}</th>')
    html.append('    </tr>')
    html.append('  </thead>')

    # Generate tbody
    html.append('  <tbody>')
    for row_idx in range(num_products):
        html.append('    <tr>')
        for col in columns:
            align_class = ' class="text-right"' if col.is_right_aligned else ''
            value = col.data_items[row_idx] if row_idx < len(col.data_items) else ''
            html.append(f'      <td{align_class}>{value}</td>')
        html.append('    </tr>')
    html.append('  </tbody>')

    html.append('</table>')

    return '\n'.join(html)


def get_table_css() -> str:
    """Return CSS for the invoice table."""
    return """
    .table-container {
      position: absolute;
      left: 60px;
      width: 483px;
    }
    .invoice-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 8px;
    }
    .invoice-table th {
      font-size: 7px;
      font-weight: bold;
      padding: 4px 2px;
      border: 1px solid black;
      vertical-align: bottom;
      text-align: left;
    }
    .invoice-table th.text-right {
      text-align: right;
    }
    .invoice-table td {
      padding: 3px 2px;
      vertical-align: top;
      border-left: 1px solid black;
      border-right: 1px solid black;
    }
    .invoice-table td.text-right {
      text-align: right;
    }
    .invoice-table tbody tr:last-child td {
      border-bottom: 1px solid black;
    }
"""


def convert_template(html_content: str, num_products: int) -> str:
    """Convert a template from absolute to hybrid positioning."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Analyze the template
    analysis = analyze_template(soup)
    if not analysis:
        return html_content  # Return unchanged if no table found

    # Add table CSS to style section
    style = soup.find('style')
    if style:
        existing_css = style.string or ""
        if '.invoice-table' not in existing_css:
            style.string = existing_css + get_table_css()

    # Calculate table position (convert from bottom to top)
    page_height = 842
    table_top = page_height - analysis['header_bottom'] - 30

    # Generate the new table
    table_html = generate_table_html(analysis, num_products)

    # Create table container
    table_container = soup.new_tag('div')
    table_container['class'] = 'table-container'
    table_container['style'] = f'top: {table_top}px;'

    # Parse and insert table HTML
    table_soup = BeautifulSoup(table_html, 'html.parser')
    table_container.append(table_soup)

    # Remove old table elements (headers and data)
    elements_to_remove = []

    # Remove table data elements
    for elem in analysis['table_data_elements']:
        elements_to_remove.append(elem.element)

    # Remove header elements that were matched
    for h in analysis['header_candidates']:
        if any(h['text'] == col.header_text for col in analysis['columns']):
            elements_to_remove.append(h['element'])

    # Remove line elements in the table area (borders)
    for line in soup.find_all('div', class_='line'):
        bottom, _, _ = parse_position(line)
        if bottom and analysis['table_bottom'] - 50 < bottom < analysis['header_bottom'] + 50:
            elements_to_remove.append(line)

    # Remove elements
    for elem in elements_to_remove:
        if elem and elem.parent:
            elem.decompose()

    # Insert table container
    body = soup.find('body')
    if body:
        # Find a good insertion point (after header elements, before footer)
        body.append(table_container)

    return str(soup.prettify())


def convert_file(html_path: Path, json_path: Path, output_path: Path) -> bool:
    """Convert a single template file."""
    import json

    try:
        # Load HTML
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Load JSON to get product count
        with open(json_path, 'r', encoding='utf-8') as f:
            invoice_data = json.load(f)
        num_products = len(invoice_data.get('products', []))

        # Convert
        converted = convert_template(html_content, num_products)

        # Save
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(converted)

        return True
    except Exception as e:
        print(f"Error converting {html_path.name}: {e}")
        return False


def main():
    """Convert all templates."""
    from tqdm import tqdm

    base_dir = Path("gen_data/invoices_141_fixed_v4")
    html_dir = base_dir / "html"
    json_dir = base_dir / "json"
    output_dir = base_dir / "html_hybrid"
    output_dir.mkdir(exist_ok=True)

    html_files = sorted(html_dir.glob("*.html"), key=lambda p: int(p.stem.split('_')[1]))

    # Filter out already converted hybrid files
    html_files = [f for f in html_files if 'hybrid' not in f.name]

    print(f"Found {len(html_files)} HTML files to convert")
    print(f"Output directory: {output_dir}")
    print("=" * 60)

    successful = 0
    failed = []

    for html_path in tqdm(html_files, desc="Converting templates"):
        json_path = json_dir / html_path.name.replace('.html', '.json')
        output_path = output_dir / html_path.name

        if not json_path.exists():
            print(f"Warning: No JSON for {html_path.name}")
            failed.append(html_path.name)
            continue

        if convert_file(html_path, json_path, output_path):
            successful += 1
        else:
            failed.append(html_path.name)

    print("\n" + "=" * 60)
    print(f"Done! Converted: {successful}, Failed: {len(failed)}")

    if failed:
        print(f"\nFailed files:")
        for f in failed[:10]:
            print(f"  - {f}")
        if len(failed) > 10:
            print(f"  ... and {len(failed) - 10} more")


if __name__ == "__main__":
    main()
