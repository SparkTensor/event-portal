from django.db import models
from django.conf import settings

# Original Speaker model is fine if you're keeping it
class Speaker(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='speaker_profile'
    )

    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.CharField(max_length=255)
    
    # CHANGE 1: 'date' and 'time' fields are replaced with 'start_datetime'.
    # I've also added 'end_datetime' as it's almost always needed.
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    
    venue = models.CharField(max_length=255)
    description = models.TextField()
    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='organized_events'
    )

    def __str__(self):
        return self.title


class Session(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    speaker = models.ForeignKey(
        'events.Speaker', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sessions')

    # CHANGE 2: Also added start and end datetimes here for consistency
    # and to properly schedule sessions within an event.
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.title} - {self.event.title}"