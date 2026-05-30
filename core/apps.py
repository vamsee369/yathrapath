from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.signals  # noqa: F401 – connect signals
from django.apps import AppConfig

class CoreConfig(AppConfig):
    name = 'core'

    def ready(self):
        from .models import Temple

        # Store original status so signal can detect changes
        original_init = Temple.__init__

        def new_init(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self._original_status = self.status

        Temple.__init__ = new_init