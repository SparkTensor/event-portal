# apps/events/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.utils.dateparse import parse_datetime
from .models import Event, Session, Speaker

# --- Security Mixin
class OrganizerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        # We also check for the staff flag, which is good practice for "backend" access
        return self.request.user.is_organizer and self.request.user.is_staff

    def handle_no_permission(self):
        messages.error(self.request, "You are not authorized to perform this action.")
        return redirect('home') # Redirect to a safe page, like the homepage

# Event Management Views
class EventCreateView(OrganizerRequiredMixin, View):
    template_name = 'event/event_form.html'

    def get(self, request, *args, **kwargs):
        # The GET request just shows the empty form
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # The POST request handles the form submission
        title = request.POST.get('title')
        start_datetime_str = request.POST.get('start_datetime')
        end_datetime_str = request.POST.get('end_datetime')
        venue = request.POST.get('venue')
        description = request.POST.get('description')

        # --- Manual Validation ---
        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        if not start_datetime_str:
            errors['start_datetime'] = 'Start date and time are required.'
        if not end_datetime_str:
            errors['end_datetime'] = 'End date and time are required.'
        
        # If there are any validation errors, re-render the form with the errors
        if errors:
            messages.error(request, "Please correct the errors below.")
            context = {
                'errors': errors,
                'values': request.POST # Send back the submitted values to re-populate the form
            }
            return render(request, self.template_name, context)

        # --- Create the Event Object ---
        Event.objects.create(
            title=title,
            start_datetime=parse_datetime(start_datetime_str),
            end_datetime=parse_datetime(end_datetime_str),
            venue=venue,
            description=description,
            organizer=request.user # Automatically assign the organizer
        )

        messages.success(request, f"Event '{title}' was created successfully!")
        # For MVP, let's redirect to a general dashboard. You can change this later.
        return redirect('organizer:dashboard') # Assumes you have a URL named 'dashboard'

class EventUpdateView(OrganizerRequiredMixin, View):
    template_name = 'organizer/event_form.html'

    def get(self, request, pk, *args, **kwargs):
        # Get the event and ensure the current user is the owner
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user:
            raise Http404

        context = {'event': event}
        return render(request, self.template_name, context)

    def post(self, request, pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=pk)
        if event.organizer != request.user:
            raise Http404

        # Extract data from the form
        title = request.POST.get('title')
        start_datetime_str = request.POST.get('start_datetime')
        # ... (extract all other fields like in CreateView)

        # --- Manual Validation (same as create) ---
        errors = {}
        if not title:
            errors['title'] = 'Title is required.'
        # ... (add all other validation checks)

        if errors:
            messages.error(request, "Please correct the errors below.")
            context = {
                'errors': errors,
                'values': request.POST, # The user's new, unsaved values
                'event': event # The original event object
            }
            return render(request, self.template_name, context)

        # --- Update the Event Object ---
        event.title = title
        event.start_datetime = parse_datetime(start_datetime_str)
        event.end_datetime = parse_datetime(request.POST.get('end_datetime'))
        event.venue = request.POST.get('venue')
        event.description = request.POST.get('description')
        event.save()

        messages.success(request, f"Event '{event.title}' was updated successfully!")
        return redirect(reverse('organizer:event-manage', kwargs={'pk': event.pk}))

# --- The Manage and Delete views can remain mostly the same ---

from django.views.generic import DeleteView, DetailView

class EventManageView(OrganizerRequiredMixin, DetailView):
    model = Event
    template_name = 'organizer/event_manage.html'
    context_object_name = 'event'

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sessions'] = self.object.sessions.all().order_by('start_time')
        # We can also add speakers for convenience
        context['speakers'] = Speaker.objects.filter(session__event=self.object).distinct()
        return context

class EventDeleteView(OrganizerRequiredMixin, DeleteView):
    model = Event
    template_name = 'organizer/event_confirm_delete.html'
    success_url = reverse_lazy('organizer:dashboard')

    def get_queryset(self):
        return Event.objects.filter(organizer=self.request.user)

# =========================================================
# == SESSION & SPEAKER MANAGEMENT VIEWS (MANUAL)
# =========================================================

class SessionCreateView(OrganizerRequiredMixin, View):
    template_name = 'organizer/session_form.html'

    def get(self, request, event_pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=event_pk, organizer=request.user)
        # Pass speakers to the template so you can populate a <select> dropdown
        context = {
            'event': event,
            'speakers': Speaker.objects.all() # Or filter as needed
        }
        return render(request, self.template_name, context)

    def post(self, request, event_pk, *args, **kwargs):
        event = get_object_or_404(Event, pk=event_pk, organizer=request.user)
        
        # Extract data
        title = request.POST.get('title')
        description = request.POST.get('description')
        speaker_id = request.POST.get('speaker') # This will be the speaker's ID
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        # --- Manual Validation ---
        errors = {}
        if not title:
            errors['title'] = 'Session title is required.'
        # ... add more validation as needed ...

        if errors:
            messages.error(request, "Please correct the errors below.")
            context = {
                'event': event,
                'speakers': Speaker.objects.all(),
                'errors': errors,
                'values': request.POST,
            }
            return render(request, self.template_name, context)

        # Find the speaker object if an ID was provided
        speaker = None
        if speaker_id:
            try:
                speaker = Speaker.objects.get(pk=speaker_id)
            except Speaker.DoesNotExist:
                # Handle case where an invalid speaker ID is sent
                pass 

        # --- Create Session Object ---
        Session.objects.create(
            event=event,
            title=title,
            description=description,
            speaker=speaker,
            start_time=parse_datetime(start_time_str),
            end_time=parse_datetime(end_time_str),
        )

        messages.success(request, f"Session '{title}' was added to {event.title}.")
        return redirect(reverse('organizer:event-manage', kwargs={'pk': event.pk}))