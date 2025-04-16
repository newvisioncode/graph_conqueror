import json
import random

from django.core.management.base import BaseCommand, CommandError

from castle_graph.models import Castle
from question.models import Question


class Command(BaseCommand):
    help = "Inputs the castle information from  json to the database"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        QUESTION_NEIGHBOR_OFFSET = 1  # if a castle has x neighbors, question level is x-1

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

            castle_difficulty_count = {}  # {difficulty: count}
            for i in js:
                if len(i['Neighbors']) in castle_difficulty_count.keys():
                    castle_difficulty_count[len(i['Neighbors']) - QUESTION_NEIGHBOR_OFFSET] += 1
                else:
                    castle_difficulty_count[len(i['Neighbors']) - QUESTION_NEIGHBOR_OFFSET] = 1

            print({key: len(value) for key, value in questions.items()})
            print(castle_difficulty_count)

            if {key: len(value) for key, value in questions.items()} != castle_difficulty_count:
                print('There are not enough questions')
                return False

            castles = {
                i['Name']: (
                    Castle.objects.create(castle_name=i['Name'],
                                          score=len(i['Neighbors']),
                                          identifier=random.randint(0, 100000000),
                                          neighbors=[],
                                          x=i['X'],
                                          y=i['Y'],
                                          question=questions[len(i['Neighbors']) - QUESTION_NEIGHBOR_OFFSET].pop(0)),
                    i
                )
                for i in js
            }

            for name, (castle, castle_json) in castles.items():
                castle: Castle
                for neighbor in castle_json['Neighbors']:
                    castle.neighbors.append(castles[neighbor][0].id)
                castle.save(update_fields=['neighbors'])