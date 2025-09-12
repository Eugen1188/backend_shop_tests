from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This signal function is triggered every time a User object is saved.
    
    `sender`: The model class that sent the signal (in this case, the User model).
    `instance`: The actual instance of the model that was saved.
    `created`: A boolean; True if a new record was created, False otherwise.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    This signal function ensures that the UserProfile is saved
    whenever the User is saved.
    """
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # If the UserProfile doesn't exist (e.g., for a superuser created
        # before the signal was set up), this prevents an error.
        pass
