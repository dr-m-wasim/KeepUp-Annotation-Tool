from django.shortcuts import render, get_object_or_404, redirect
from .models import Events, PostFeatures, Comments
from django.urls import reverse
from django.http import HttpResponseBadRequest
from django.db import models

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

    # Create a dictionary of comment counts keyed by post_id
    comment_counts = (
        Comments.objects
        .filter(post_id__in=[post.post_id for post in posts])
        .values('post_id')
        .annotate(count=models.Count('comment_id'))
    )
    # Convert to a dictionary for quick lookup
    comment_count_dict = {item['post_id']: item['count'] for item in comment_counts}

    # Attach comment count to each post
    for post in posts:
        post.comment_count = comment_count_dict.get(post.post_id, 0)

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


def post_comments_view(request, post_id, event_id):
    event = get_object_or_404(Events, event_id=event_id)
    comments = Comments.objects.filter(post_id=post_id)
    context = {
        'event': event,
        'post_id': post_id,
        'event_id': event_id,  # Pass event_id to the context
        'comments': comments,
    }
    return render(request, 'postcommenthub.html', context)
    
def save_comment(request, post_id):
    if request.method == 'POST':
        annotator = request.session.get('annotator', None)
        comment_text = request.POST.get('comment', '').strip()

        if not annotator:
            return redirect('annotator_select')

        if not comment_text:
            return HttpResponseBadRequest("Comment cannot be empty.")

        # Check if comment exists from this annotator
        comment_obj, created = Comments.objects.get_or_create(
            post_id=post_id,
            annotator=annotator,
            defaults={'comment': comment_text}
        )

        if not created:
            comment_obj.comment = comment_text
            comment_obj.save()

        return redirect('postcomments', post_id=post_id)

    return HttpResponseBadRequest("Invalid request method.")


def comment_editor(request, post_id, event_id, comment_index):
    post = get_object_or_404(PostFeatures, post_id=post_id)
    event = get_object_or_404(Events, event_id=event_id)
    comments = list(Comments.objects.filter(post_id=post_id))

    annotator = request.session.get('annotator', None)
    if not annotator:
        return redirect('annotator_select')

    if comment_index < 0:
        comment_index = 0
    if comment_index >= len(comments):
        comment_index = len(comments) - 1

    current_comment = comments[comment_index]

    selected_label = ""
    if annotator == 'annotatorone':
        selected_label = current_comment.annotatorOne_comment_label
    elif annotator == 'annotatortwo':
        selected_label = current_comment.annotatorTwo_comment_label
    elif annotator == 'annotatorthree':
        selected_label = current_comment.annotatorThree_comment_label

    if request.method == 'POST':
        selected_label = request.POST.get('comment_label')
        if selected_label:
            if annotator == 'annotatorone':
                current_comment.annotatorOne_comment_label = selected_label
            elif annotator == 'annotatortwo':
                current_comment.annotatorTwo_comment_label = selected_label
            elif annotator == 'annotatorthree':
                current_comment.annotatorThree_comment_label = selected_label
            current_comment.save()

        next_index = comment_index + 1
        if next_index >= len(comments):
            next_index = comment_index
        return redirect('comment_editor', post_id=post_id, event_id=event_id, comment_index=next_index)

    return render(request, 'comment_editor.html', {
        'post': post,
        'event': event,
        'comments': comments,
        'current_comment': current_comment,
        'comment_index': comment_index,
        'selected_label': selected_label,
        'annotator': annotator,
    })
