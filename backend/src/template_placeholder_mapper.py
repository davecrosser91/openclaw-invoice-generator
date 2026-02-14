"""
Template Placeholder Mapper
Maps invoice data to Strapi template placeholders

This module provides a comprehensive mapping between invoice JSON data
and the placeholder format used in Strapi templates.
"""

import random
import re
from datetime import datetime
from typing import Dict, Any


class TemplatePlaceholderMapper:
    """Maps invoice data to template placeholders"""

    # Different article number format types
    ARTICLE_FORMATS = [
        'ART',      # ART-001, ART-002
        'SKU',      # SKU-78432
        'PRD',      # PRD-2024-001
        'NUM',      # 001, 002, 003
        'ALPHA',    # A-12345, B-23456
        'CODE',     # P78432X
    ]

    def __init__(self, invoice_data: Dict[str, Any]):
        """
        Initialize mapper with invoice data

        Args:
            invoice_data: Invoice data dictionary with seller, buyer, products, etc.
        """
        self.invoice = invoice_data
        # Select a random article format for this invoice (consistent within invoice)
        self.article_format = random.choice(self.ARTICLE_FORMATS)
        # Generate base random numbers for article codes
        self._article_base = random.randint(10000, 99999)

    def generate_random_number(self, pattern: str) -> str:
        """Generate random number from pattern like '8&10_n'"""
        match = re.search(r'(\d+)&', pattern)
        if match:
            length = int(match.group(1))
            return ''.join([str(random.randint(0, 9)) for _ in range(length)])
        return '12345678'

    def extract_tax_rate_number(self, tax_rate_str: str) -> str:
        """Extract number from '19%' -> '19'"""
        match = re.search(r'(\d+)', str(tax_rate_str))
        return match.group(1) if match else '19'

    def truncate_text(self, text: str, max_length: int = 40) -> str:
        """Truncate text to avoid column overlaps in tables."""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + '...'

    def generate_article_number(self, index: int) -> str:
        """
        Generate article number based on the selected format for this invoice.

        Args:
            index: Product index (1-based)

        Returns:
            Formatted article number string
        """
        if self.article_format == 'ART':
            # Classic: ART-001, ART-002
            return f"ART-{index:03d}"
        elif self.article_format == 'SKU':
            # SKU with random digits: SKU-78432, SKU-78433
            return f"SKU-{self._article_base + index}"
        elif self.article_format == 'PRD':
            # Year-based: PRD-2024-001
            year = datetime.now().year
            return f"PRD-{year}-{index:03d}"
        elif self.article_format == 'NUM':
            # Simple numbers: 001, 002, 003
            return f"{index:03d}"
        elif self.article_format == 'ALPHA':
            # Letter prefix: A-12345, B-23456
            letter = chr(64 + index)  # A, B, C, ...
            return f"{letter}-{self._article_base + index * 111}"
        elif self.article_format == 'CODE':
            # Alphanumeric code: P78432X, P78433Y
            suffix = chr(87 + index)  # X, Y, Z, ...
            return f"P{self._article_base + index}{suffix}"
        else:
            return f"ART-{index:03d}"

    def format_date(self, date_str: str, output_format: str = "de") -> str:
        """
        Format ISO date string to readable format.

        Args:
            date_str: Date string in ISO format (e.g., "2023-05-14T21:33:02")
            output_format: "de" for German (14.05.2023), "en" for English (May 14, 2023)

        Returns:
            Formatted date string
        """
        if not date_str:
            return ""

        try:
            # Parse ISO format
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, "%Y-%m-%d")

            if output_format == "de":
                return dt.strftime("%d.%m.%Y")
            else:
                return dt.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            # Return original if parsing fails
            return date_str

    def get_all_placeholders(self) -> Dict[str, str]:
        """
        Generate ALL placeholders for the invoice

        Returns:
            Dictionary mapping placeholder names to values
        """
        placeholders = {}

        # ============================================
        # SELLER INFORMATION
        # ============================================
        seller = self.invoice.get('seller', {})
        placeholders['{seller_name}'] = seller.get('name', '')
        placeholders['{seller_street}'] = seller.get('street', '')
        placeholders['{seller_city}'] = seller.get('city', '')
        placeholders['{seller_postalcode}'] = seller.get('postalcode', '')
        placeholders['{seller_citywplc}'] = f"{seller.get('postalcode', '')} {seller.get('city', '')}"
        placeholders['{seller_taxidentifier}'] = seller.get('taxidentifier', '')
        placeholders['{seller_phone}'] = seller.get('phone', '')
        placeholders['{seller_email}'] = seller.get('email', '')
        placeholders['{seller_website}'] = seller.get('website', 'www.example.de')
        placeholders['{seller_iban}'] = seller.get('iban', '')
        placeholders['{seller_bic}'] = seller.get('bic', '')
        placeholders['{seller_employee}'] = seller.get('employee', seller.get('name', ''))

        # ============================================
        # BUYER INFORMATION
        # ============================================
        buyer = self.invoice.get('buyer', {})
        placeholders['{buyer_name}'] = buyer.get('name', '')
        placeholders['{buyer_street}'] = buyer.get('street', '')
        placeholders['{buyer_city}'] = buyer.get('city', '')
        placeholders['{buyer_postalcode}'] = buyer.get('postalcode', '')
        placeholders['{buyer_citywplc}'] = f"{buyer.get('postalcode', '')} {buyer.get('city', '')}"
        placeholders['{buyer_customerid}'] = buyer.get('customerid', '')
        placeholders['{buyer_employee}'] = buyer.get('employee', buyer.get('name', ''))
        placeholders['{buyer_phone}'] = buyer.get('phone', '')

        # ============================================
        # INVOICE META
        # ============================================
        placeholders['{invoicenumber}'] = self.invoice.get('invoicenumber', '')

        # Format dates to German format (DD.MM.YYYY)
        date_of_invoice = self.invoice.get('dateofinvoice', '')
        date_of_delivery = self.invoice.get('dateofdeliveryorservice', date_of_invoice)
        placeholders['{dateofinvoice}'] = self.format_date(date_of_invoice)
        placeholders['{dateofdeliveryorservice}'] = self.format_date(date_of_delivery)

        # Contract number derived from invoice number
        invoice_num = str(self.invoice.get('invoicenumber', '')).replace('-', '').replace('/', '')
        placeholders['{contract_number}'] = f'K-{invoice_num}'

        # ============================================
        # TOTALS
        # ============================================
        placeholders['{subtotal}'] = f"{self.invoice.get('subtotal', 0):.2f}"
        placeholders['{taxes}'] = f"{self.invoice.get('taxes', 0):.2f}"
        placeholders['{total}'] = f"{self.invoice.get('total', 0):.2f}"

        # ============================================
        # PRODUCTS (1-10)
        # ============================================
        products = self.invoice.get('products', [])

        for i in range(1, 11):
            if i <= len(products):
                product = products[i-1]

                # Basic product info
                placeholders[f'{{product_pos_{i}}}'] = str(i)
                placeholders[f'{{product_num_{i}}}'] = self.generate_article_number(i)
                # Truncate long product names to prevent column overlap
                placeholders[f'{{product_name_{i}}}'] = self.truncate_text(product.get('name', ''), 40)
                placeholders[f'{{product_quantity_{i}}}'] = str(int(product.get('quantity', 0)))
                placeholders[f'{{product_unity_{i}}}'] = product.get('unity', '')
                placeholders[f'{{product_price_{i}}}'] = f"{product.get('price', 0):.2f}"

                # Tax rate (extract number from "19%")
                tax_rate_str = product.get('taxrate', '19%')
                tax_rate_num = self.extract_tax_rate_number(tax_rate_str)
                placeholders[f'{{product_sales_tax_percent_{i}}}'] = tax_rate_num

                # Subtotal (already calculated)
                subtotal = product.get('subtotal', 0)
                placeholders[f'{{product_subtotal_{i}}}'] = f"{subtotal:.2f}"

                # Cost WITHOUT tax (for Apple2 template)
                # This is: quantity * price (before tax)
                cost_wo_tax = product.get('quantity', 0) * product.get('price', 0)
                placeholders[f'{{product_cost_wo_tax_{i}}}'] = f"{cost_wo_tax:.2f}"

                # Cost WITH tax (for Balolo template)
                # This is: subtotal (which already includes calculation)
                cost_w_tax = subtotal
                placeholders[f'{{product_cost_w_tax_{i}}}'] = f"{cost_w_tax:.2f}"

                # Sales tax cost (tax amount for this product line)
                # Format: "19" or "19%" depending on template
                tax_amount = product.get('tax', 0)
                placeholders[f'{{product_sales_tax_cost_{i}}}'] = f"{tax_amount:.2f}"

            else:
                # Empty placeholders for unused product slots
                placeholders[f'{{product_pos_{i}}}'] = ''
                placeholders[f'{{product_num_{i}}}'] = ''
                placeholders[f'{{product_name_{i}}}'] = ''
                placeholders[f'{{product_quantity_{i}}}'] = ''
                placeholders[f'{{product_unity_{i}}}'] = ''
                placeholders[f'{{product_price_{i}}}'] = ''
                placeholders[f'{{product_sales_tax_percent_{i}}}'] = ''
                placeholders[f'{{product_subtotal_{i}}}'] = ''
                placeholders[f'{{product_cost_wo_tax_{i}}}'] = ''
                placeholders[f'{{product_cost_w_tax_{i}}}'] = ''
                placeholders[f'{{product_sales_tax_cost_{i}}}'] = ''

        # ============================================
        # RANDOM NUMBERS
        # ============================================
        # Generate random numbers for all common patterns used across templates
        # Patterns follow format: {random_number_X_Y&Z_n} where Y is the length
        all_random_patterns = [
            # Common patterns found across various templates
            ('1', '8&10_n'), ('1', '8&12_n'), ('1', '6&8_n'),
            ('2', '7&12_n'), ('2', '3&5_n'), ('2', '8&10_n'),
            ('3', '8&8_n'), ('3', '8&12_n'), ('3', '6&8_n'),
            ('4', '3&3_n'), ('4', '6&8_n'), ('4', '8&10_n'),
            ('5', '3&3_n'), ('5', '5&5_n'), ('5', '6&8_n'),
            ('6', '5&5_n'), ('6', '6&8_n'), ('6', '8&10_n'),
        ]

        for num, pattern in all_random_patterns:
            placeholder_key = f'{{random_number_{num}_{pattern}}}'
            placeholders[placeholder_key] = self.generate_random_number(pattern)

        return placeholders

    def fill_template(self, template_html: str) -> str:
        """
        Fill all placeholders in template HTML

        Args:
            template_html: HTML template string with placeholders

        Returns:
            HTML with all placeholders filled
        """
        filled_html = template_html
        placeholders = self.get_all_placeholders()

        # First pass: fill known placeholders
        for placeholder, value in placeholders.items():
            filled_html = filled_html.replace(placeholder, str(value))

        # Second pass: generate values for any remaining random_number placeholders
        filled_html = self._fill_remaining_random_numbers(filled_html)

        # Third pass: clean up empty product rows
        filled_html = self._clean_empty_rows(filled_html)

        # Fourth pass: remove any remaining unfilled placeholders
        filled_html = self._remove_unfilled_placeholders(filled_html)

        # Fifth pass: fix overlapping elements
        filled_html = self._fix_overlapping_elements(filled_html)

        return filled_html

    def _fill_remaining_random_numbers(self, html: str) -> str:
        """Fill any remaining random_number placeholders dynamically."""
        # Find all random_number placeholders still in the HTML
        # Match various patterns: {random_number_X_Y&Z_n}, {random_number_X_Y&Z_suffix}, etc.
        pattern = r'\{random_number_(\d+)_(\d+)&(\d+)_([a-z_]+)\}'
        matches = re.findall(pattern, html)

        for match in matches:
            num, length, max_len, suffix = match
            placeholder = f'{{random_number_{num}_{length}&{max_len}_{suffix}}}'
            value = self.generate_random_number(f'{length}&{max_len}')
            html = html.replace(placeholder, value)

        return html

    def _remove_unfilled_placeholders(self, html: str) -> str:
        """Remove any remaining unfilled placeholders to clean up the output."""
        # Remove placeholders that look like {something_something}
        # but preserve CSS {} blocks by only matching word characters and underscores
        # Also handle malformed placeholders with missing closing brace

        # Standard placeholders: {placeholder_name}
        html = re.sub(r'\{[a-z][a-z0-9_]*\}', '', html)

        # Malformed placeholders missing closing brace: {placeholder_name (at end of content)
        # This catches cases like {product_name_9 without closing }
        html = re.sub(r'\{[a-z][a-z0-9_]*(?=<|$|\s*$)', '', html)

        # Also catch placeholders with numbers at different positions
        html = re.sub(r'\{[a-z_]*\d+[a-z_]*\}?', '', html)

        return html

    def _fix_overlapping_elements(self, html: str) -> str:
        """
        Detect and fix overlapping text elements by adjusting positions.

        Key insights:
        1. Elements at SAME or VERY CLOSE positions (within 5px) are table columns
        2. Table data elements (mb-1/mb-2) have different height calculation
        3. Multiple passes needed for cascading fixes
        """
        # Run multiple passes to handle cascading overlaps
        for _ in range(3):
            html = self._fix_overlapping_elements_pass(html)
        return html

    def _fix_overlapping_elements_pass(self, html: str) -> str:
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

            # Determine if this is a table data element (has mb-1/mb-2)
            is_table_data = 'mb-1' in content or 'mb-2' in content

            # Calculate height based on element type
            if is_table_data:
                # Table data: count <pre> tags, each row ~(font_size + 6)px
                pre_count = len(re.findall(r'<pre[^>]*>', content))
                pre_count = max(pre_count, 1)
                height = pre_count * (font_size + 6)
            else:
                # Regular element: count text lines
                text_content = re.sub(r'<[^>]+>', '', content)
                lines = len([l for l in text_content.split('\n') if l.strip()])
                lines = max(lines, 1)
                height = lines * (font_size + 4)

            text_content = re.sub(r'<[^>]+>', '', content)

            elements.append({
                'bottom': bottom,
                'top': bottom + height,
                'left': left,
                'right': right,
                'height': height,
                'original_bottom': bottom,
                'h_pos': left if left is not None else (595 - right if right is not None else 0),
                'is_table_data': is_table_data,
                'text': text_content[:50],
            })

        if len(elements) < 2:
            return html

        # Exclude table data rows from fixing (they're handled separately)
        non_table_elements = [e for e in elements if not e['is_table_data']]

        if len(non_table_elements) < 2:
            return html

        adjustments = {}

        # Sort elements by bottom (highest first = top of page)
        sorted_elements = sorted(non_table_elements, key=lambda x: x['bottom'], reverse=True)

        for i, e1 in enumerate(sorted_elements):
            for e2 in sorted_elements[i+1:]:
                # Elements within 5px vertical are "same row" - not overlaps
                if abs(e1['bottom'] - e2['bottom']) <= 5:
                    continue

                # Check if horizontally close (within 100px)
                if abs(e1['h_pos'] - e2['h_pos']) >= 100:
                    continue

                # Check if vertically overlapping
                if e1['bottom'] >= e2['top'] or e2['bottom'] >= e1['top']:
                    continue

                # Calculate overlap amount
                overlap = min(e1['top'], e2['top']) - max(e1['bottom'], e2['bottom'])

                if overlap > 3:  # Only fix overlaps > 3px
                    # Move the LOWER element (smaller bottom) down
                    lower_elem = e2 if e2['bottom'] < e1['bottom'] else e1
                    higher_elem = e1 if e2['bottom'] < e1['bottom'] else e2

                    # Calculate new position: just below the higher element
                    padding = 5
                    new_bottom = higher_elem['bottom'] - lower_elem['height'] - padding

                    # Don't push elements too low (keep some footer margin)
                    if new_bottom < 80:
                        continue

                    old_bottom = lower_elem['original_bottom']

                    # Only adjust if we haven't already adjusted this element
                    if old_bottom not in adjustments and abs(old_bottom - new_bottom) > 3:
                        adjustments[old_bottom] = new_bottom
                        # Update the element's position for cascading checks
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

    def _clean_empty_rows(self, html: str) -> str:
        """
        Clean up empty product rows in table-based templates.

        Strategy: Trim any div with more pre tags than products.
        Handles templates with:
        - mb-1, mb-2, mb-4, mb-5 classes (different invoice templates)
        - Multi-line product descriptions (3 lines per product)
        """
        product_count = len(self.invoice.get('products', []))
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
            """Trim excess rows from a table column div."""
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

        # Clean up whitespace
        html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)

        return html


# Example usage
if __name__ == "__main__":
    import json

    # Load invoice data
    with open('gen_data/invoice_1.json', 'r') as f:
        invoice_data = json.load(f)

    # Create mapper
    mapper = TemplatePlaceholderMapper(invoice_data)

    # Get all placeholders
    placeholders = mapper.get_all_placeholders()

    print(f"Generated {len(placeholders)} placeholders")
    print("\nExample placeholders:")
    for key, value in list(placeholders.items())[:10]:
        print(f"  {key}: {value}")
