from django.contrib import admin
from django.contrib.admin.filters import DateFieldListFilter
from .models import Event, Session, Speaker

class SessionInline(admin.TabularInline):
    """
    --- ENHANCEMENT (Highly Recommended) ---
    This allows you to add and edit Sessions directly on the Event creation page.
    This is much more intuitive than creating an Event, saving, then going to
    the Session page to add sessions.
    """
    model = Session
    extra = 1  # Show one empty form for a new session by default
    fields = ('title', 'speaker', 'start_time', 'end_time', 'description')
    autocomplete_fields = ['speaker']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin configuration for the Event model."""
    
    # --- FIX ---
    # Replaced 'date' and 'time' with the new 'start_datetime' and 'end_datetime' fields.
    list_display = ('title', 'start_datetime', 'end_datetime', 'venue', 'organizer')
    
    # --- ENHANCEMENT ---
    # Added organizer's email to the search for easier lookup.
    search_fields = ('title', 'venue', 'organizer__username', 'organizer__email')
    
    # --- FIX & ENHANCEMENT ---
    # Replaced 'date' with a more specific filter for the 'start_datetime' field.
    # Added 'organizer' as a filter option.
    list_filter = (
        ('start_datetime', DateFieldListFilter), # Provides friendly options like 'Today', 'Past 7 days', etc.
        'organizer'
    )

    # --- ENHANCEMENT ---
    # Use autocomplete for the organizer to handle many users efficiently.
    autocomplete_fields = ['organizer']

    # --- ENHANCEMENT ---
    # This adds the Session manager directly onto the Event page.
    inlines = [SessionInline]


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """Admin configuration for the Session model."""

    # --- ENHANCEMENT ---
    # Added start and end times to the list display for better context.
    list_display = ('title', 'event', 'speaker', 'start_time', 'end_time')
    
    # No fix needed here, but added filtering by speaker which is useful.
    list_filter = ('event', 'speaker')

    search_fields = ('title', 'event__title', 'speaker__name')
    
    # --- ENHANCEMENT ---
    # Autocomplete fields are crucial here for a good user experience.
    autocomplete_fields = ['event', 'speaker']


@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    """Admin configuration for the Speaker model."""
    
    # --- ENHANCEMENT ---
    # Added a helper method to display the linked user's email address.
    list_display = ('name', 'user', 'get_user_email')
    
    # --- ENHANCEMENT ---
    # Allow searching by the linked user's email.
    search_fields = ('name', 'user__username', 'user__email')
    
    # --- ENHANCEMENT ---
    # Autocomplete for the user field is essential.
    autocomplete_fields = ['user']

    @admin.display(description="User's Email", ordering='user__email')
    def get_user_email(self, obj):
        if obj.user:
            return obj.user.email
        return "No linked user"