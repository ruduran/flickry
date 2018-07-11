import sys

from django.apps import AppConfig


class ImagesbytagsConfig(AppConfig):
    name = 'imagesbytags'

    def ready(self):
        if any(cmd in sys.argv for cmd in ('migrate', 'makemigrations', 'test', 'check', 'shell')):
            return

        from .worker import Worker
        w = Worker()
        w.start()
