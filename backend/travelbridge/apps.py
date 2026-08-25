from django.apps import AppConfig

class TravelbridgeConfig(AppConfig):
    name = 'travelbridge'

    def ready(self):
        from .firebase_config import initialize_firebase
        initialize_firebase()
