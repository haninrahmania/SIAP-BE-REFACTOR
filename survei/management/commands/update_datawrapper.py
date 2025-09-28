# survei/management/commands/update_datawrapper.py

from django.core.management.base import BaseCommand
from survei.signals import manual_update_datawrapper_data, rebuild_all_province_counts

class Command(BaseCommand):
    help = 'Update CSV files in GitHub repository for Datawrapper maps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if no changes detected',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output',
        )

    def handle(self, *args, **options):
        if options['verbose']:
            self.stdout.write('Starting Datawrapper CSV update process...')
            
        self.stdout.write('Rebuilding province counts from database...')
        
        try:
            rebuild_all_province_counts()
            
            self.stdout.write(
                self.style.SUCCESS('✓ Successfully updated CSV files in GitHub repository')
            )
            
            if options['verbose']:
                self.stdout.write('Files updated in your repository:')
                self.stdout.write('  - data.csv (all surveys by province)')
                self.stdout.write('  - data-ongoing.csv (ongoing surveys only)')
                
            self.stdout.write(
                self.style.WARNING('Datawrapper maps will update automatically within a few minutes.')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating CSV files: {str(e)}')
            )
            if options['verbose']:
                import traceback
                self.stdout.write(traceback.format_exc())
            return

        self.stdout.write('Update process completed successfully!')