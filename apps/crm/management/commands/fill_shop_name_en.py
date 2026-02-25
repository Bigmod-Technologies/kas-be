import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.crm.models import Customer


class Command(BaseCommand):
    help = "Fill shop_name_en for existing Customer records from JSON file (Outlet Name field)"

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            type=str,
            help="Name of the JSON file (with or without .json extension)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without saving",
        )

    def handle(self, *args, **options):
        filename = options["filename"]
        dry_run = options["dry_run"]

        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        base_dir = settings.BASE_DIR
        file_path = os.path.join(base_dir, "raw_data", filename)

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            total_records = len(data)
            updated = 0
            not_found = 0
            skipped_empty = 0
            errors = 0

            self.stdout.write(
                self.style.SUCCESS(f"\n=== Fill shop_name_en ===")
            )
            if dry_run:
                self.stdout.write(self.style.WARNING("DRY RUN - no changes will be saved\n"))
            self.stdout.write(
                self.style.SUCCESS(f"Total records to process: {total_records}\n")
            )

            for index, record in enumerate(data, 1):
                try:
                    outlet_code_str = record.get("Outlet Code", "")
                    if outlet_code_str:
                        cleaned_code = str(outlet_code_str).replace(",", "")
                        try:
                            numeric_code = int(float(cleaned_code))
                            outlet_code = str(numeric_code)[-5:]
                        except (ValueError, OverflowError):
                            errors += 1
                            continue
                    else:
                        errors += 1
                        continue

                    shop_name_en = (record.get("Outlet Name") or "").strip()
                    if not shop_name_en:
                        skipped_empty += 1
                        continue

                    try:
                        customer = Customer.objects.get(customer_id=outlet_code)
                    except Customer.DoesNotExist:
                        not_found += 1
                        continue

                    if customer.shop_name_en != shop_name_en:
                        if not dry_run:
                            customer.shop_name_en = shop_name_en
                            if customer.contact_number and not customer.contact_number.strip().startswith("0"):
                                customer.contact_number = f"0{customer.contact_number}"
                            customer.save()
                        updated += 1

                    if index % 100 == 0:
                        self.stdout.write(
                            self.style.SUCCESS(f"Processed {index}/{total_records} records...")
                        )

                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f"Record {index}: Error - {str(e)}")
                    )
                    continue

            self.stdout.write(
                self.style.SUCCESS(f"\n=== Complete ===\n")
            )
            self.stdout.write(
                self.style.SUCCESS(f"Customers updated (shop_name_en): {updated}")
            )
            self.stdout.write(
                self.style.WARNING(f"Outlet code not found in DB: {not_found}")
            )
            self.stdout.write(
                self.style.WARNING(f"Skipped (empty Outlet Name): {skipped_empty}")
            )
            self.stdout.write(
                self.style.ERROR(f"Errors: {errors}")
            )
            if dry_run and updated:
                self.stdout.write(
                    self.style.WARNING("Run without --dry-run to apply changes.")
                )

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Error parsing JSON: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file: {e}"))
