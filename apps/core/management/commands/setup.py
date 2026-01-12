from django.core.management.base import BaseCommand
from apps.area.models import WorkingDay


class Command(BaseCommand):
    help = 'Set up default data including 7 days of the week in WorkingDay model'

    def handle(self, *args, **options):
        """Set up 7 days of the week in WorkingDay model"""
        days_of_week = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'
        ]
        
        created_count = 0
        existing_count = 0
        
        for day_name in days_of_week:
            working_day, created = WorkingDay.objects.get_or_create(name=day_name)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {day_name}')
                )
            else:
                existing_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ Already exists: {day_name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSetup complete! Created {created_count} new working days, '
                f'{existing_count} already existed.'
            )
        )

