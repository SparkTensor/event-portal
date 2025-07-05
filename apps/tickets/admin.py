from django.contrib import admin
from apps.tickets.models import Ticket, Registration

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    # This class is correct and needs no changes.
    list_display = ('name', 'event', 'type', 'price') 
    list_filter = ('event', 'type',)
    search_fields = ('name', 'event__title',)
    autocomplete_fields = ['event']


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    """Admin configuration for the Registration model."""

    # --- FIX for list_display ---
    # We can't use 'event' directly. We create a custom method 'get_event' below.
    list_display = ('attendee', 'get_event', 'ticket', 'registered_at')
    
    # --- FIX for search_fields ---
    # To search by the event's title, we now traverse the relationship:
    # registration -> ticket -> event -> title
    search_fields = ('attendee__username', 'attendee__email', 'ticket__event__title')

    # --- FIX for list_filter ---
    # We tell Django to filter based on the 'event' field of the related 'ticket'.
    list_filter = ('ticket__event', 'ticket__type')

    # --- FIX for autocomplete_fields ---
    # This must refer to a direct ForeignKey on the model. Since 'event' is no longer
    # a direct field, we must remove it from here. We still have autocomplete for attendee and ticket.
    autocomplete_fields = ['attendee', 'ticket']
    
    readonly_fields = ('registered_at',)

    # --- NEW METHOD to get the event for the list_display ---
    @admin.display(description='Event', ordering='ticket__event__title')
    def get_event(self, obj):
        """Returns the title of the event from the related ticket."""
        return obj.ticket.event.title