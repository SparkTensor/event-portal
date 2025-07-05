# apps/tickets/models.py

from django.db import models
from django.conf import settings
from apps.events.models import Event

class Ticket(models.Model):
    TICKET_TYPES = (
        ('Free', 'Free'),
        ('Paid', 'Paid'),
    )

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tickets')
    
    # --- THIS IS THE FIX ---
    # Add this 'name' field to your model. It was referenced in the admin but was missing here.
    name = models.CharField(max_length=100, default='Standard Ticket')
    
    type = models.CharField(max_length=10, choices=TICKET_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        # This will now work correctly
        return f"{self.name} for {self.event.title}"

# The Registration model below is correct from our last change, no edits needed here.
class Registration(models.Model):
    attendee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # I noticed this was missing in my last snippet, it's very important to add back
        # to prevent a user from registering for the same ticket type multiple times.
        unique_together = ('attendee', 'ticket')

    def __str__(self):
        return f"{self.attendee.username} registered for {self.ticket.event.title}"