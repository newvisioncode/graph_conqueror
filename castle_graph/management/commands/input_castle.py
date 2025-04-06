import json

from django.core.management.base import BaseCommand, CommandError

from castle_graph.models import Castle
from question.models import Question


class Command(BaseCommand):
    help = "Inputs the castle information from  json to the database"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        filename: str = options['filename']
        if not filename.endswith('.json'):
            raise CommandError("Filename must end with .json")
        with open(filename, encoding='utf8') as jsonfile:
            js = json.load(jsonfile)

            questions = {}
            # question: {
            #   1: [
            #       ...
            #   ],
            #   2: [
            #       ...
            #   ],
            #
            #   ...
            # }
            for q in Question.objects.filter(castle__isnull=True):
                if q.level in questions.keys():
                    questions[q.level].append(q)
                else:
                    questions[q.level] = [q]

            castles = {
                i['Name']: (
                    Castle.objects.create(castle_name=i['Name'],
                                          score=len(i['Neighbors']),
                                          question=questions[len(i['Neighbors'])].pop(0)),
                    i
                )
                for i in js  # todo identifier
            }

            for name, (castle, castle_json) in castles.items():
                castle: Castle
                for neighbor in castle_json['Neighbors']:
                    castle.neighbors.append(castles[neighbor][0].id)
                castle.save(update_fields=['neighbors'])
