import csv

from django.core.management.base import BaseCommand, CommandError

from castle_graph.models import ContestUser, Payment


class Command(BaseCommand):
    help = "Inputs the payments from a csv to the database"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        filename: str = options['filename']
        if not filename.endswith('.csv'):
            raise CommandError("Filename must end with .csv")
        with open(filename, newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            reader.__iter__()
            reader.__next__()

            for i, row in enumerate(reader):
                c_user = ContestUser.objects.filter(payment_identifier=row[20]).first()
                if c_user is None:
                    print(f"User in line {i} doesn't exist")
                    continue
                Payment.objects.create(user=c_user, tracking_code=row[25], success=True)

