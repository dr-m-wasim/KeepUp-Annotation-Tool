from django.shortcuts import render, get_object_or_404
from .models import Events

def events_list(request):
    events = Events.objects.all()
    return render(request, 'events.html', {'events': events})

def eventposts(request, event_id):
    event = get_object_or_404(Events, event_id=event_id)
    return render(request, 'eventposts.html', {'event': event})
