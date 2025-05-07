from django import forms, template
from django.shortcuts import render, get_object_or_404, redirect
from .models import Events, PostFeatures, Comments, UserFeatures
from django.urls import reverse
from django.http import HttpResponseBadRequest, HttpResponse
from django.db import models
import csv
from django.http import JsonResponse
from collections import Counter
from django.db.models import Q
from django.db import connection
from .forms import CommentsForm, PostFeaturesForm
from django.db import transaction

def compute_fleiss_kappa(matrix):
    n = sum(matrix[0])  # Number of raters per item
    N = len(matrix)     # Number of items
    k = len(matrix[0])  # Number of categories

    # Proportion of ratings in each category
    pj = [sum(row[j] for row in matrix) / (N * n) for j in range(k)]

    # Agreement for each item
    Pi = []
    for row in matrix:
        row_sum = sum(row)
        agreement = sum([count * (count - 1) for count in row])
        Pi.append(agreement / (row_sum * (row_sum - 1)))

    P_bar = sum(Pi) / N
    P_e_bar = sum([p**2 for p in pj])

    if P_e_bar == 1:
        return 1.0
    return (P_bar - P_e_bar) / (1 - P_e_bar)

def compute_cohen_kappa(labels1, labels2):
    assert len(labels1) == len(labels2), "Label lists must be same length"

    total = len(labels1)
    labels = set(labels1) | set(labels2)
    
    # Count label agreements and distributions
    observed_agreement = sum([1 for a, b in zip(labels1, labels2) if a == b]) / total

    label_counts_1 = Counter(labels1)
    label_counts_2 = Counter(labels2)

    expected_agreement = sum(
        (label_counts_1[label] / total) * (label_counts_2[label] / total)
        for label in labels
    )

    if expected_agreement == 1:
        return 1.0  # Avoid division by zero
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)

def compute_fleiss_kappa(matrix):
    n = sum(matrix[0])  # Number of raters per item
    N = len(matrix)     # Number of items
    k = len(matrix[0])  # Number of categories

    # Proportion of ratings in each category
    pj = [sum(row[j] for row in matrix) / (N * n) for j in range(k)]

    # Agreement for each item
    Pi = []
    for row in matrix:
        row_sum = sum(row)
        agreement = sum([count * (count - 1) for count in row])
        Pi.append(agreement / (row_sum * (row_sum - 1)))

    P_bar = sum(Pi) / N
    P_e_bar = sum([p**2 for p in pj])

    if P_e_bar == 1:
        return 1.0
    return (P_bar - P_e_bar) / (1 - P_e_bar)

def compute_cohen_kappa(labels1, labels2):
    assert len(labels1) == len(labels2), "Label lists must be same length"

    total = len(labels1)
    labels = set(labels1) | set(labels2)
    
    # Count label agreements and distributions
    observed_agreement = sum([1 for a, b in zip(labels1, labels2) if a == b]) / total

    label_counts_1 = Counter(labels1)
    label_counts_2 = Counter(labels2)

    expected_agreement = sum(
        (label_counts_1[label] / total) * (label_counts_2[label] / total)
        for label in labels
    )

    if expected_agreement == 1:
        return 1.0  # Avoid division by zero
    return (observed_agreement - expected_agreement) / (1 - expected_agreement)

def calculate_kappa_scores(request):
    comments = Comments.objects.filter(
        ~Q(annotatorOne_comment_label=None),
        ~Q(annotatorTwo_comment_label=None),
        ~Q(annotatorThree_comment_label=None)
    )

    annotator1 = []
    annotator2 = []
    annotator3 = []

    label_set = set()
    matrix = []

    for c in comments:
        l1 = c.annotatorOne_comment_label
        l2 = c.annotatorTwo_comment_label
        l3 = c.annotatorThree_comment_label

        labels = [l1, l2, l3]
        annotator1.append(l1)
        annotator2.append(l2)
        annotator3.append(l3)

        label_set.update(labels)
    
    label_list = sorted(label_set)
    label_index = {label: idx for idx, label in enumerate(label_list)}

    for c in comments:
        labels = [c.annotatorOne_comment_label, c.annotatorTwo_comment_label, c.annotatorThree_comment_label]
        row = [0] * len(label_list)
        for label in labels:
            row[label_index[label]] += 1
        matrix.append(row)

    fleiss = compute_fleiss_kappa(matrix)
    kappa_1_2 = compute_cohen_kappa(annotator1, annotator2)
    kappa_1_3 = compute_cohen_kappa(annotator1, annotator3)
    kappa_2_3 = compute_cohen_kappa(annotator2, annotator3)

    return JsonResponse({
        'kappa_annotator1_vs_annotator2': round(kappa_1_2, 4),
        'kappa_annotator1_vs_annotator3': round(kappa_1_3, 4),
        'kappa_annotator2_vs_annotator3': round(kappa_2_3, 4),
        'fleiss_kappa': round(fleiss, 4),
    })



def export_posts_csv(request):
    posts = PostFeatures.objects.all()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="post_features.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'Event ID', 'Post ID', 'Post URL', 'Platform', 'Post Title', 'Post Label',
        'Media Type (0-img,1-vid,2)', 'Likes Count', 'Timestamp', 'Comments Count',
        'Views', 'Shares', 'Reposts',
        'Annotator 1 Post Label', 'Annotator 2 Post Label', 'Annotator 3 Post Label'
    ])

    for post in posts:
        writer.writerow([
            post.event_id,
            post.post_id,
            post.post_url,
            post.platform,
            post.post_title,
            post.post_label,
            post.image_image_0_video_1_if_no_image_video_2_field,
            post.likescount,
            post.timestamp,
            post.commentscount,
            post.views,
            post.shares,
            post.reposts,
            post.annotatorOne_post_label,
            post.annotatorTwo_post_label,
            post.annotatorThree_post_label
        ])
    return response

def export_events_csv(request):
    events = Events.objects.all()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="events.csv"'
    response.write('\ufeff')  # UTF-8 BOM for Excel support

    writer = csv.writer(response)
    writer.writerow([
        'Student ID', 'Student Name', 'Event ID', 'Event Name', 'Claim', 'Claim URL',
        'Post URL', 'Label', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10',
        'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13'
    ])

    for event in events:
        writer.writerow([
            event.student_id,
            event.student_name,
            event.event_id,
            event.event_name,
            event.claim,
            event.claim_url,
            event.posturl,
            event.label,
            event.unnamed_8,
            event.unnamed_9,
            event.unnamed_10,
            event.unnamed_11,
            event.unnamed_12,
            event.unnamed_13
        ])
    return response


def export_user_features_csv(request):
    user_features = UserFeatures.objects.all()
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="user_features.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        'Post ID', 'Username', 'Followers', 'Followings', 'User Verified (0/1)',
        'Profile Pic URL', 'Posts Count', 'Joining Date'
    ])

    for user in user_features:
        writer.writerow([
            user.post_id,
            user.username,
            user.followers,
            user.followings,
            user.is_user_verified_0_verified_1_unverified_field,
            user.profile_pic_url,
            user.posts_count,
            user.joining_date
        ])
    return response


def export_comments_csv(request):
    comments = Comments.objects.all()

    # Use UTF-8 with BOM to support Urdu and other Unicode text
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="comments.csv"'
    response.write('\ufeff')  # Write BOM at beginning

    writer = csv.writer(response)
    writer.writerow([
        'Comment ID', 'Post ID', 'Comment Text', 'Commenter Name',
        'Likes Count', 'Comment Label', 'Annotator 1 Label',
        'Annotator 2 Label', 'Annotator 3 Label', 'Label'
    ])

    for comment in comments:
        label1 = comment.annotatorOne_comment_label
        label2 = comment.annotatorTwo_comment_label
        label3 = comment.annotatorThree_comment_label

        if label1 == label2 and label1:
            final_label = label1
        elif label1 == label3 and label1:
            final_label = label1
        elif label2 == label3 and label2:
            final_label = label2
        else:
            final_label = ''

        writer.writerow([
            comment.comment_id,
            comment.post_id,
            comment.commenttext,
            comment.commenter_name,
            comment.likescount_on_comment,
            comment.comment_label,
            label1,
            label2,
            label3,
            final_label
        ])

    return response



def dashboard(request):
    if request.method == 'POST':
        annotator = request.POST.get('annotator')
        if annotator:
            request.session['annotator'] = annotator
            return redirect('events')

    # Total counts
    total_posts = PostFeatures.objects.count()
    total_comments = Comments.objects.count()

    # Avoid division by zero
    total_posts = total_posts if total_posts > 0 else 1
    total_comments = total_comments if total_comments > 0 else 1

    # Posts labeled per annotator
    post_counts = {
        'annotatorOne': PostFeatures.objects.exclude(annotatorOne_post_label__isnull=True).exclude(annotatorOne_post_label='').exclude(annotatorOne_post_label='None').count(),
        'annotatorTwo': PostFeatures.objects.exclude(annotatorTwo_post_label__isnull=True).exclude(annotatorTwo_post_label='').exclude(annotatorOne_post_label='None').count(),
        'annotatorThree': PostFeatures.objects.exclude(annotatorThree_post_label__isnull=True).exclude(annotatorThree_post_label='').exclude(annotatorOne_post_label='None').count(),
    }

    # Comments labeled per annotator
    comment_counts = {
        'annotatorOne': Comments.objects.exclude(annotatorOne_comment_label__isnull=True).exclude(annotatorOne_comment_label='').exclude(annotatorTwo_comment_label='None').count(),
        'annotatorTwo': Comments.objects.exclude(annotatorTwo_comment_label__isnull=True).exclude(annotatorTwo_comment_label='').exclude(annotatorTwo_comment_label='None').count(),
        'annotatorThree': Comments.objects.exclude(annotatorThree_comment_label__isnull=True).exclude(annotatorThree_comment_label='').exclude(annotatorTwo_comment_label='None').count(),
    }

    # Calculate percentages
    post_progress = {k: round((v / total_posts) * 100, 2) for k, v in post_counts.items()}
    comment_progress = {k: round((v / total_comments) * 100, 2) for k, v in comment_counts.items()}

    context = {
        'post_progress': post_progress,
        'comment_progress': comment_progress,
        'total_posts' : total_posts,
        'total_comments' : total_comments
    }

    return render(request, 'core/dashboard.html', context)

def events_list(request):
    
    # if no annotator is selected, go back to main page
    if 'annotator' not in  request.session:
            return redirect('/')
    
    events = Events.objects.all().prefetch_related('posts')

    return render(request, 'core/all_events.html', {
        'events': events
        })

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

    annotator_map = {
        'annotatorone' : 'annotatorOne_post_label',
        'annotatortwo' : 'annotatorTwo_post_label',
        'annotatorthree' : 'annotatorThree_post_label'
    }

    return render(request, 'core/all_posts.html', {'event': event, 'posts': posts, 'annotator': annotator_map[request.session['annotator']] })


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
    
    annotator_map = {
        'annotatorone' : 'annotatorOne_comment_label',
        'annotatortwo' : 'annotatorTwo_comment_label',
        'annotatorthree' : 'annotatorThree_comment_label'
    }

    context = {
        'event': event,
        'post_id': post_id,
        'event_id': event_id,  # Pass event_id to the context
        'comments': comments,
        'annotator': annotator_map[request.session['annotator']]
    }
    return render(request, 'core/all_comments.html', context)
    
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


def edit_post(request, post_id):
    post = get_object_or_404(PostFeatures, pk=post_id)
    event_id = post.event_id
    event = get_object_or_404(Events, pk=event_id)

    if request.method == 'POST':
        form = PostFeaturesForm(request.POST, instance=post)
        form.fields['platform'].widget = forms.HiddenInput()
        
        if form.is_valid():
            form.save()
            return redirect('eventposts', post.event_id)  # Redirect after saving
    else:
        form = PostFeaturesForm(instance=post)
        form.fields['platform'].widget = forms.HiddenInput()
        form.fields['post_url'].widget = forms.HiddenInput()
        
        if request.session['annotator'] == 'annotatorone':
            form.fields['annotatorOne_post_label'].required = True
            del form.fields['annotatorTwo_post_label']
            del form.fields['annotatorThree_post_label']
        elif request.session['annotator'] == 'annotatortwo':
            form.fields['annotatorTwo_post_label'].required = True
            del form.fields['annotatorOne_post_label']
            del form.fields['annotatorThree_post_label']
        elif request.session['annotator'] == 'annotatorthree':
            form.fields['annotatorThree_post_label'].required = True
            del form.fields['annotatorTwo_post_label']
            del form.fields['annotatorOne_post_label']
    
    return render(request, 'core/edit_post.html', {
        'event' : event,
        'form': form
        })

def get_query(request, post_id):
    
    annotator = 'annotatorOne_comment_label'

    if request.session['annotator'] == 'annotatortwo':
        annotator = 'annotatorTwo_comment_label'
    elif request.session['annotator'] == 'annotatorthree':
        annotator = 'annotatorThree_comment_label'

    query = f'''
    SELECT comment_id
    FROM comments
    WHERE "post-id"= {post_id} AND ({annotator} IS NULL OR {annotator} = 'None')
    ORDER BY comment_id ASC
    LIMIT 1;
    '''

    return query

def edit_comment(request, post_id, comment_id):
    
    comment = get_object_or_404(Comments, pk=comment_id)
    post = get_object_or_404(PostFeatures, pk=post_id)
    
    if request.method == 'POST':
        form = CommentsForm(request.POST, instance=comment)
        
        if form.is_valid():
            form.save()
            
            action = request.POST.get('action')
            
            if action == 'next':

                with connection.cursor() as cursor:
                    cursor.execute(get_query(request, post.post_id))
                    row = cursor.fetchone()
                    value = row[0] if row else None
                    print(value)
                if value is not None:
                    return redirect('edit_comment', post.post_id, value)
            
            return redirect('postcomments', post.post_id, post.event_id)
            
    else:
        form = CommentsForm(instance=comment)
        
        if request.session['annotator'] == 'annotatorone':
            form.fields['annotatorOne_comment_label'].required = True
            del form.fields['annotatorTwo_comment_label']
            del form.fields['annotatorThree_comment_label']
        elif request.session['annotator'] == 'annotatortwo':
            form.fields['annotatorTwo_comment_label'].required = True
            del form.fields['annotatorOne_comment_label']
            del form.fields['annotatorThree_comment_label']
        elif request.session['annotator'] == 'annotatorthree':
            form.fields['annotatorThree_comment_label'].required = True
            del form.fields['annotatorTwo_comment_label']
            del form.fields['annotatorOne_comment_label']

    return render(request, 'core/edit_comment.html', {
            'post' : post,
            'form': form
        })