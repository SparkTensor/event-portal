# Models For The Users app
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_organizer = models.BooleanField(default=False)
    is_attendee = models.BooleanField(default=True)

    def __str__(self):
        return self.username

