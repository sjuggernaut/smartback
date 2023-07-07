from django.core.management.base import BaseCommand
import os
from infra.providers import launch_providers


class Command(BaseCommand):
    help = 'Launch the Sensor Provider Threads'

    def handle(self, *args, **options):
        environment = os.getenv("ENVIRONMENT", "local")
        print(f"[Environment] = [{environment}]")
        launch_providers(environment)
