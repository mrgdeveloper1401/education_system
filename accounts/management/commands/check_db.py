from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Checks the database'

    def handle(self, *args, **options):
        db_conn = connections['default']
        try:
            db_conn.coursor()
            self.stdout.write(self.style.SUCCESS('Successfully connected to database'))
        except OperationalError:
            self.stdout.write(self.style.ERROR('Database connection failed'))
