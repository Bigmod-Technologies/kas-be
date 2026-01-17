from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from apps.area.models import WorkingDay
from apps.inventory.models import StockType


class Command(BaseCommand):
    help = "Set up default data including 7 days of the week in WorkingDay model, user groups, and stock types"

    def handle(self, *args, **options):
        """Set up 7 days of the week in WorkingDay model, user groups, and stock types"""

        # Setup Working Days
        self.stdout.write(self.style.SUCCESS("\n=== Setting up Working Days ==="))
        days_of_week = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        working_days_created = 0
        working_days_existing = 0

        for day_name in days_of_week:
            working_day, created = WorkingDay.objects.get_or_create(name=day_name)
            if created:
                working_days_created += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {day_name}"))
            else:
                working_days_existing += 1
                self.stdout.write(self.style.WARNING(f"→ Already exists: {day_name}"))

        # Setup Groups
        self.stdout.write(self.style.SUCCESS("\n=== Setting up User Groups ==="))
        groups = [
            "Delivery man",
            "Salesman",
            "Manager",
            "Accountant",
            "Director",
        ]

        groups_created = 0
        groups_existing = 0

        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                groups_created += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {group_name}"))
            else:
                groups_existing += 1
                self.stdout.write(self.style.WARNING(f"→ Already exists: {group_name}"))

        # Setup Stock Types
        self.stdout.write(self.style.SUCCESS("\n=== Setting up Stock Types ==="))
        stock_types = [
            "Main Stock",
            "Regular Stock",
            "Free Stock",
            "Damage Stock",
            "Advance Stock",
        ]

        stock_types_created = 0
        stock_types_existing = 0

        for stock_type_name in stock_types:
            stock_type, created = StockType.objects.get_or_create(name=stock_type_name)
            if created:
                stock_types_created += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Created: {stock_type_name}"))
            else:
                stock_types_existing += 1
                self.stdout.write(self.style.WARNING(f"→ Already exists: {stock_type_name}"))

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\n=== Setup Complete ===\n"
                f"Working Days: Created {working_days_created} new, {working_days_existing} already existed.\n"
                f"Groups: Created {groups_created} new, {groups_existing} already existed.\n"
                f"Stock Types: Created {stock_types_created} new, {stock_types_existing} already existed."
            )
        )
