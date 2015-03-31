import logging
from django.core.management.base import BaseCommand, CommandError
from auto_translation.tasks import TranslationNavigator

logger = logging.getLogger('commands')


class Command(BaseCommand):

    def handle(self, *args, **options):
        print 'Beginning translation ....'
        TranslationNavigator.do_translate()
        print 'Finish'