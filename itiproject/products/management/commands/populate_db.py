from django.core.management.base import BaseCommand
from products.populate_database import DatabasePopulator

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        populator = DatabasePopulator()
        populator.run()

# use the command python manage.py populate_db to start the populate file 