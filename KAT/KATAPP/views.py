from django.shortcuts import render, get_object_or_404, redirect
from .models import Events, PostFeatures
from django.urls import reverse

def annotator_select(request):
    if request.method == 'POST':
        annotator = request.POST.get('annotator')
        if annotator:
            request.session['annotator'] = annotator  # Save annotator in session
            return redirect('events')  # Redirect to events page after selection
    return render(request, 'annotator_selector.html')

def events_list(request):
    events = Events.objects.all()
    return render(request, 'events.html', {'events': events})

def event_posts(request, event_id):
    event = get_object_or_404(Events, event_id=event_id)
    posts = PostFeatures.objects.filter(event_id=event_id)
    return render(request, 'eventpostshub.html', {'event': event, 'posts': posts})


def post_editor(request, event_id):
    event = get_object_or_404(Events, event_id=event_id)
    posts = PostFeatures.objects.filter(event_id=event_id)
    
    annotator = request.session.get('annotator', None)
    if not annotator:
        return redirect('annotator_select')

    # Get index from GET or POST
    if request.method == 'POST':
        post_index = int(request.POST.get('post_index', 0))
    else:
        post_index = int(request.GET.get('index', 0))
    
    # Handle if posts list is empty
    if not posts.exists():
        return render(request, 'post_editor.html', {
            'event': event,
            'posts': [],
            'current_post': None,
            'post_index': 0,
            'annotator': annotator,
        })
    
    # Ensure index is within range
    if post_index < 0:
        post_index = 0
    if post_index >= len(posts):
        post_index = len(posts) - 1
    
    current_post = posts[post_index]

     # Set selected label for pre-selecting in form
    selected_label = ""
    if annotator == 'annotatorone':
        selected_label = current_post.annotatorOne_post_label
    elif annotator == 'annotatortwo':
        selected_label = current_post.annotatorTwo_post_label
    elif annotator == 'annotatorthree':
        selected_label = current_post.annotatorThree_post_label

    if request.method == 'POST':
        selected_label = request.POST.get('post_label')
        if selected_label and current_post:
            if annotator == 'annotatorone':
                current_post.annotatorOne_post_label = selected_label
            elif annotator == 'annotatortwo':
                current_post.annotatorTwo_post_label = selected_label
            elif annotator == 'annotatorthree':
                current_post.annotatorThree_post_label = selected_label
            current_post.save()

        # After saving, move to the next post
        next_index = post_index + 1
        if next_index >= len(posts):
            next_index = post_index  # Stay at last post
        return redirect(f'/event/{event_id}/post_editor/?index={next_index}')
    
    
    return render(request, 'post_editor.html', {
        'event': event,
        'posts': posts,
        'current_post': current_post,
        'post_index': post_index,
        'annotator': annotator,
        'selected_label': selected_label,  # <-- Add this here
    })
