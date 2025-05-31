from django.core.management.base import BaseCommand
from products.populate_database import Command as PopulateCommand

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **options):
        populator = PopulateCommand()
        populator.handle(*args, **options)

# use the command python manage.py populate_db to start the populate file 