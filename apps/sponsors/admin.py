from django.contrib import admin
# --- FIX: Import both Sponsor and SponsorTier ---
from apps.sponsors.models import Sponsor, SponsorTier


@admin.register(SponsorTier)
class SponsorTierAdmin(admin.ModelAdmin):
    """
    --- NEW: This is required to manage Sponsorship Tiers ---
    This admin class allows you to create, edit, and delete the 
    sponsorship levels themselves (e.g., Gold, Silver, Community Partner)
    from the Django admin interface.
    """
    list_display = ('name', 'order')
    search_fields = ('name',)


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Sponsor model, which links a company
    to a specific event at a specific tier.
    """
    # --- FIX: Added 'event' to the display to provide essential context ---
    list_display = ('name', 'event', 'tier', 'link')
    
    # --- ENHANCEMENT: It's very useful to search by the event title too ---
    search_fields = ('name', 'event__title')
    
    # --- ENHANCEMENT: Also allow filtering by event, not just by tier ---
    list_filter = ('event', 'tier')

    # --- ENHANCEMENT: This is a major usability improvement ---
    # Replaces the slow, long dropdown menus for 'event' and 'tier'
    # with fast, searchable input boxes.
    autocomplete_fields = ['event', 'tier']