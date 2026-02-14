#!/usr/bin/env python3
"""
Convert absolute-positioned invoice templates to hybrid templates - V2.

This version preserves the original template design:
- Keeps all original header elements, border lines, styling
- Only converts the product DATA rows to a borderless table
- Original visual elements provide the table appearance
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup
import json


@dataclass
class DataColumn:
    """A column of product data."""
    h_position: int  # left or right value
    is_right: bool  # True if right-[X], False if left-[X]
    bottom: int
    items: List[str] = field(default_factory=list)
    original_element: object = None
    font_size: int = 8
    css_classes: str = ""


def parse_position(element) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """Extract bottom, left, right positions from element classes."""
    classes = element.get('class', [])
    class_str = ' '.join(classes) if isinstance(classes, list) else classes

    bottom = None
    left = None
    right = None

    bottom_match = re.search(r'bottom-\[(\d+)px\]', class_str)
    left_match = re.search(r'left-\[(\d+)px\]', class_str)
    right_match = re.search(r'right-\[(\d+)px\]', class_str)

    if bottom_match:
        bottom = int(bottom_match.group(1))
    if left_match:
        left = int(left_match.group(1))
    if right_match:
        right = int(right_match.group(1))

    return bottom, left, right


def has_table_data_markers(element) -> bool:
    """Check if element has mb-* or my-* classes indicating table rows."""
    content = str(element)
    return bool(re.search(r'm[by]-[0-9]', content))


def extract_pre_items(element) -> List[str]:
    """Extract text from pre tags."""
    items = []
    for pre in element.find_all('pre'):
        text = pre.get_text(strip=True)
        if text:
            items.append(text)
    return items


def get_font_size(element) -> int:
    """Get font size from element."""
    match = re.search(r'text-\[(\d+)px\]', str(element))
    return int(match.group(1)) if match else 8


def get_alignment_class(element) -> str:
    """Get text alignment class."""
    classes = element.get('class', [])
    class_str = ' '.join(classes) if isinstance(classes, list) else classes
    if 'text-right' in class_str:
        return 'text-right'
    if 'text-center' in class_str:
        return 'text-center'
    return ''


def find_data_columns(soup) -> List[DataColumn]:
    """Find all columns of table data."""
    columns = []

    for div in soup.find_all('div', class_=lambda c: c and 'textbox' in c):
        if not has_table_data_markers(div):
            continue

        bottom, left, right = parse_position(div)
        if bottom is None:
            continue

        items = extract_pre_items(div)
        if not items:
            continue

        columns.append(DataColumn(
            h_position=left if left is not None else right,
            is_right=(right is not None),
            bottom=bottom,
            items=items,
            original_element=div,
            font_size=get_font_size(div),
            css_classes=get_alignment_class(div)
        ))

    return columns


def convert_template(html_content: str, num_products: int) -> str:
    """Convert template to hybrid format."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find data columns
    columns = find_data_columns(soup)
    if not columns:
        return html_content  # No table data found

    # All columns should be at the same bottom position
    data_bottom = columns[0].bottom
    columns = [c for c in columns if c.bottom == data_bottom]

    if not columns:
        return html_content

    # Sort columns left to right
    # Left-positioned columns: sort by position ascending
    # Right-positioned columns: sort by position descending (rightmost = last)
    left_cols = sorted([c for c in columns if not c.is_right], key=lambda c: c.h_position)
    right_cols = sorted([c for c in columns if c.is_right], key=lambda c: c.h_position, reverse=True)
    sorted_columns = left_cols + right_cols

    # Calculate table width and position
    page_height = 842
    table_top = page_height - data_bottom - (num_products * 14)  # Approximate

    # Find leftmost and rightmost positions for table width
    left_positions = [c.h_position for c in columns if not c.is_right]
    right_positions = [c.h_position for c in columns if c.is_right]

    table_left = min(left_positions) if left_positions else 60
    table_right = min(right_positions) if right_positions else 60  # right offset from page edge
    table_width = 595 - table_left - table_right

    # Generate table HTML
    font_size = sorted_columns[0].font_size if sorted_columns else 8

    table_lines = [
        f'<div class="data-table-container" style="position: absolute; top: {table_top}px; left: {table_left}px; width: {table_width}px;">',
        f'  <table style="width: 100%; border-collapse: collapse; font-size: {font_size}px;">',
        '    <tbody>'
    ]

    # Generate rows
    for row_idx in range(num_products):
        table_lines.append('      <tr>')
        for col in sorted_columns:
            value = col.items[row_idx] if row_idx < len(col.items) else ''
            align_style = ''
            if col.is_right or 'text-right' in col.css_classes:
                align_style = ' style="text-align: right;"'
            elif 'text-center' in col.css_classes:
                align_style = ' style="text-align: center;"'
            table_lines.append(f'        <td{align_style}>{value}</td>')
        table_lines.append('      </tr>')

    table_lines.extend([
        '    </tbody>',
        '  </table>',
        '</div>'
    ])

    table_html = '\n'.join(table_lines)

    # Remove original data elements
    for col in sorted_columns:
        if col.original_element:
            col.original_element.decompose()

    # Insert table before </body>
    body = soup.find('body')
    if body:
        table_soup = BeautifulSoup(table_html, 'html.parser')
        body.append(table_soup)

    return str(soup.prettify())


def convert_file(html_path: Path, json_path: Path, output_path: Path) -> bool:
    """Convert a single file."""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read()

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        num_products = len(data.get('products', []))

        converted = convert_template(html, num_products)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(converted)

        return True
    except Exception as e:
        print(f"Error converting {html_path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Test on a single file."""
    html_path = Path("gen_data/invoices_141_fixed_v4/html/invoice_1.html")
    json_path = Path("gen_data/invoices_141_fixed_v4/json/invoice_1.json")
    output_path = Path("gen_data/invoices_141_fixed_v4/html_hybrid/invoice_1_v2.html")
    output_path.parent.mkdir(exist_ok=True)

    success = convert_file(html_path, json_path, output_path)
    print(f"Conversion: {'success' if success else 'failed'}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
