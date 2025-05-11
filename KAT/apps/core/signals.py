# core/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

@receiver(post_migrate)
def remove_unwanted_contenttypes(sender, **kwargs):
    """
    Removes specific models from contenttypes table after migration.
    """
    unwanted_models = [
        ('core', 'userfeatures'),
        ('core', 'postfeatures'),
        ('core', 'comments'),
        ('core', 'events'),
    ]
    for app_label, model in unwanted_models:
        ContentType.objects.filter(app_label=app_label, model=model).delete()
