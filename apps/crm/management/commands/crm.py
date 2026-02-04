import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.area.models import Area
from apps.crm.models import Customer


class Command(BaseCommand):
    help = "Read JSON file from raw_data folder"

    def add_arguments(self, parser):
        parser.add_argument(
            "filename",
            type=str,
            help="Name of the JSON file (with or without .json extension)",
        )

    def handle(self, *args, **options):
        """Read JSON file from raw_data folder"""
        # Get all Area information from Area model

        filename = options["filename"]

        # Add .json extension if not present
        if not filename.endswith(".json"):
            filename = f"{filename}.json"

        # Get the base directory (project root)
        base_dir = settings.BASE_DIR
        file_path = os.path.join(base_dir, "raw_data", filename)

        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        # Read and parse JSON file
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Analytics tracking
            total_records = len(data)
            customers_created = 0
            customers_updated = 0
            invalid_outlet_codes = 0
            missing_area = 0
            missing_data = 0
            errors = 0

            self.stdout.write(
                self.style.SUCCESS(f"\n=== Starting Import ===")
            )
            self.stdout.write(
                self.style.SUCCESS(f"Total records to process: {total_records}\n")
            )

            # Extract variables from each record
            for index, record in enumerate(data, 1):
                try:
                    outlet_code_str = record.get("Outlet Code", "")
                    # Handle scientific notation, remove commas, get last 5 digits, convert to integer
                    if outlet_code_str:
                        # Remove commas first
                        cleaned_code = str(outlet_code_str).replace(",", "")
                        # Convert to float first to handle scientific notation (e.g., '2E+11')
                        try:
                            numeric_code = int(float(cleaned_code))
                            # Get last 5 digits as string, then convert to integer
                            outlet_code = int(str(numeric_code)[-5:])
                        except (ValueError, OverflowError):
                            outlet_code = 0
                            invalid_outlet_codes += 1
                    else:
                        outlet_code = 0
                        invalid_outlet_codes += 1
                    
                    outlet_name_bangla = record.get("Outlet Name (Bangla)", "")
                    outlet_df = record.get("Outlet DF", "")
                    address = record.get("Address", "")
                    owner_name = record.get("Owner Name", "")
                    area_name = record.get("Area", "")
                    owner_mobile_no_str = record.get("Owner Mobile No.", "")
                    
                    # Check for missing critical data
                    if not area_name or not owner_name or not outlet_name_bangla:
                        missing_data += 1
                    
                    # Remove commas and convert to string
                    owner_mobile_no = (
                        str(owner_mobile_no_str).replace(",", "")
                        if owner_mobile_no_str
                        else ""
                    )
                    
                    # Get Area object from database using area name
                    try:
                        area = Area.objects.get(name=area_name)
                    except Area.DoesNotExist:
                        missing_area += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"Record {index}: Area '{area_name}' not found. Skipping..."
                            )
                        )
                        continue

                    # Create or update customer
                    customer, created = Customer.objects.get_or_create(
                        customer_id=outlet_code,
                        defaults={
                            "name": owner_name,
                            "shop_name": outlet_name_bangla,
                            "contact_number": owner_mobile_no,
                            "address": address,
                            "area": area,
                            "fridge_type": "PDF" if outlet_df == 'PDF' else "ODF",
                        },
                    )
                    
                    if created:
                        customers_created += 1
                    else:
                        customers_updated += 1
                        # Update existing customer if needed
                        customer.name = owner_name
                        customer.shop_name = outlet_name_bangla
                        customer.contact_number = owner_mobile_no
                        customer.address = address
                        customer.area = area
                        if outlet_df:
                            customer.fridge_type = outlet_df
                        customer.save()

                    # Progress indicator
                    if index % 100 == 0:
                        self.stdout.write(
                            self.style.SUCCESS(f"Processed {index}/{total_records} records...")
                        )

                except Exception as e:
                    errors += 1
                    self.stdout.write(
                        self.style.ERROR(f"Record {index}: Error processing - {str(e)}")
                    )
                    continue

            # Display analytics summary
            self.stdout.write(
                self.style.SUCCESS(f"\n=== Import Complete ===\n")
            )
            self.stdout.write(
                self.style.SUCCESS(f"Total Records Processed: {total_records}")
            )
            self.stdout.write(
                self.style.SUCCESS(f"Customers Created: {customers_created}")
            )
            self.stdout.write(
                self.style.SUCCESS(f"Customers Updated: {customers_updated}")
            )
            self.stdout.write(
                self.style.WARNING(f"Invalid Outlet Codes: {invalid_outlet_codes}")
            )
            self.stdout.write(
                self.style.WARNING(f"Missing Area: {missing_area}")
            )
            self.stdout.write(
                self.style.WARNING(f"Missing Critical Data: {missing_data}")
            )
            self.stdout.write(
                self.style.ERROR(f"Errors: {errors}")
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccess Rate: {((total_records - errors - missing_area) / total_records * 100):.2f}%"
                )
            )

        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Error parsing JSON: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error reading file: {e}"))
