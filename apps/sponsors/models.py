# apps/sponsors/models.py

from django.db import models
from apps.events.models import Event # Make sure this import path is correct for your project

class SponsorTier(models.Model):
    """
    Defines the sponsorship levels for events, e.g., 'Gold', 'Silver', 'Bronze'.
    This allows you to create/edit tiers from the Django Admin.
    """
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0, help_text="Tiers will be displayed in this order (e.g., 0 for Platinum, 1 for Gold).")
    
    # You can add fields for tier benefits here later, like:
    # logo_size = models.CharField(...)
    # can_have_booth = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Sponsor(models.Model):
    """
    Represents a specific company or individual sponsoring a specific event at a given tier.
    """
    # The event this sponsor is associated with.
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sponsors')
    
    # The company/individual's name.
    name = models.CharField(max_length=255)

    # Links to the tier (e.g., Gold) to define their benefits.
    tier = models.ForeignKey(SponsorTier, on_delete=models.PROTECT, related_name='sponsors')
    
    logo = models.ImageField(upload_to='sponsor_logos/')
    link = models.URLField(blank=True, help_text="The sponsor's public website URL.")
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.tier.name}) at {self.event.title}"