from django.core.management.base import BaseCommand

from infra.providers import launch_providers


class Command(BaseCommand):
    help = 'Launch the Sensor Provider Threads'

    def add_arguments(self, parser):
        parser.add_argument('environment', nargs=1, type=str)

    def handle(self, *args, **options):
        environment = options['environment'][0]
        launch_providers(environment)
