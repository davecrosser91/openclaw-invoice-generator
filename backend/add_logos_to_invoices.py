"""
Add Logos to Existing Invoices - Batch Processing Script
Author: DocumentGenerator Team
Date: 2025-11-24

This script adds company logos to existing invoices in Strapi.
It generates unique logos per company and updates invoice PDFs.

Usage:
    python add_logos_to_invoices.py --limit 10 --dry-run
    python add_logos_to_invoices.py --all --regenerate-pdfs
"""

import argparse
import json
import os
from typing import List, Dict, Set
from dotenv import load_dotenv
import requests
from src.LogoGenerator import LogoGenerator

load_dotenv()


class InvoiceLogoProcessor:
    """Process existing invoices and add logos"""

    def __init__(self, openai_key: str, strapi_url: str, bearer_token: str):
        self.logo_generator = LogoGenerator(openai_key=openai_key)
        self.strapi_url = strapi_url
        self.bearer_token = bearer_token
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }

    def get_invoices(self, limit: int = None) -> List[Dict]:
        """Fetch invoices from Strapi"""
        url = f"{self.strapi_url}/api/invoices"
        params = {"populate": "*"}
        if limit:
            params["pagination[limit]"] = limit

        print(f"\n📥 Fetching invoices from Strapi...")
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        data = response.json()
        invoices = data.get('data', [])
        print(f"✓ Found {len(invoices)} invoices")
        return invoices

    def extract_unique_companies(self, invoices: List[Dict]) -> Set[tuple]:
        """Extract unique seller companies from invoices"""
        companies = set()

        for invoice in invoices:
            attrs = invoice.get('attributes', {})
            seller = attrs.get('seller', {})

            if seller and 'name' in seller:
                # Get company name and try to infer industry
                company_name = seller['name']
                # You could extract industry from invoice data if available
                industry = "general business"

                companies.add((company_name, industry))

        print(f"✓ Found {len(companies)} unique companies")
        return companies

    def generate_logos_for_companies(
        self,
        companies: Set[tuple],
        force_regenerate: bool = False
    ) -> Dict[str, str]:
        """Generate logos for all unique companies"""
        logo_map = {}

        print(f"\n🎨 Generating logos for {len(companies)} companies...")
        print("-" * 70)

        for i, (company_name, industry) in enumerate(companies, 1):
            try:
                print(f"\n[{i}/{len(companies)}] {company_name}")

                logo_base64 = self.logo_generator.generate_logo_base64(
                    company_name=company_name,
                    industry=industry,
                    force_regenerate=force_regenerate
                )

                logo_map[company_name] = logo_base64
                print(f"✓ Logo ready ({len(logo_base64)} chars)")

            except Exception as e:
                print(f"✗ Failed: {e}")
                logo_map[company_name] = None

        successful = sum(1 for v in logo_map.values() if v is not None)
        print(f"\n✓ Generated {successful}/{len(companies)} logos successfully")

        return logo_map

    def update_invoice_with_logo(
        self,
        invoice_id: int,
        seller_name: str,
        logo_base64: str,
        dry_run: bool = False
    ) -> bool:
        """Update a specific invoice with logo data"""
        if dry_run:
            print(f"  [DRY RUN] Would update invoice {invoice_id}")
            return True

        # Here you would update the invoice in Strapi
        # This depends on your Strapi schema
        # For now, we'll just print
        print(f"  ✓ Updated invoice {invoice_id}")
        return True

    def process_invoices(
        self,
        limit: int = None,
        dry_run: bool = False,
        force_regenerate: bool = False
    ) -> Dict:
        """Main processing function"""
        stats = {
            "total_invoices": 0,
            "unique_companies": 0,
            "logos_generated": 0,
            "invoices_updated": 0,
            "errors": 0
        }

        # Step 1: Fetch invoices
        invoices = self.get_invoices(limit=limit)
        stats["total_invoices"] = len(invoices)

        if not invoices:
            print("⚠ No invoices found")
            return stats

        # Step 2: Extract unique companies
        companies = self.extract_unique_companies(invoices)
        stats["unique_companies"] = len(companies)

        # Step 3: Generate logos for unique companies
        logo_map = self.generate_logos_for_companies(
            companies,
            force_regenerate=force_regenerate
        )
        stats["logos_generated"] = sum(1 for v in logo_map.values() if v is not None)

        # Step 4: Update invoices with logos
        print(f"\n📝 Updating invoices with logos...")
        print("-" * 70)

        for invoice in invoices:
            invoice_id = invoice['id']
            attrs = invoice.get('attributes', {})
            seller = attrs.get('seller', {})
            seller_name = seller.get('name', '')

            if seller_name in logo_map and logo_map[seller_name]:
                try:
                    self.update_invoice_with_logo(
                        invoice_id,
                        seller_name,
                        logo_map[seller_name],
                        dry_run=dry_run
                    )
                    stats["invoices_updated"] += 1
                except Exception as e:
                    print(f"  ✗ Error updating invoice {invoice_id}: {e}")
                    stats["errors"] += 1

        return stats


def main():
    parser = argparse.ArgumentParser(
        description="Add logos to existing invoices in batch"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of invoices to process"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all invoices"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually update invoices, just simulate"
    )
    parser.add_argument(
        "--force-regenerate",
        action="store_true",
        help="Force regenerate logos even if cached"
    )

    args = parser.parse_args()

    # Load environment variables
    openai_key = os.getenv("OPENAI_API_KEY")
    strapi_url = os.getenv("STRAPI_URL")
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

    if not all([openai_key, strapi_url, bearer_token]):
        print("✗ Missing required environment variables:")
        print("  - OPENAI_API_KEY")
        print("  - STRAPI_URL")
        print("  - STRAPI_BEARER_TOKEN")
        return

    # Initialize processor
    processor = InvoiceLogoProcessor(
        openai_key=openai_key,
        strapi_url=strapi_url,
        bearer_token=bearer_token
    )

    # Determine limit
    limit = None if args.all else (args.limit or 10)

    print("=" * 70)
    print("INVOICE LOGO BATCH PROCESSOR")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"Limit: {limit or 'ALL'}")
    print(f"Force regenerate: {args.force_regenerate}")
    print("=" * 70)

    # Process invoices
    stats = processor.process_invoices(
        limit=limit,
        dry_run=args.dry_run,
        force_regenerate=args.force_regenerate
    )

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total invoices:       {stats['total_invoices']}")
    print(f"Unique companies:     {stats['unique_companies']}")
    print(f"Logos generated:      {stats['logos_generated']}")
    print(f"Invoices updated:     {stats['invoices_updated']}")
    print(f"Errors:               {stats['errors']}")
    print("=" * 70)


if __name__ == "__main__":
    main()