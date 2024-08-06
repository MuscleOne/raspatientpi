from django.core.management.base import BaseCommand, CommandError

from raspatientpi.config import OPENAI_API_KEY
from patient import RaspatientPi

class Command(BaseCommand):
    help = "Creates an Assistant on the OpenAI platform"

    def handle(self, *args, **options):
        if OPENAI_API_KEY is None or len(OPENAI_API_KEY) == 0:
            raise CommandError("OPENAI_API_KEY is not set")
        
        pp = RaspatientPi(OPENAI_API_KEY, None)
        assistant_id = pp.create_assistant()

        self.stdout.write(assistant_id)
