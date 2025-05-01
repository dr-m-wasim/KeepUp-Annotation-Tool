from django.urls import path
from . import views

urlpatterns = [
    path('', views.annotator_select, name='annotator_select'),  # This comes first!
    path('event', views.events_list, name='events'),
    path('event/<str:event_id>/', views.event_posts, name='eventposts'),
    path('event/<str:event_id>/post_editor/', views.post_editor, name='post_editor'),
    path('postcomments/<int:post_id>/', views.post_comments_view, name='postcomments'),
    path('postcomments/<int:post_id>/save/', views.save_comment, name='save_comment'),
    # path('comment_editor/<int:event_id>/<int:post_id>/', views.comment_editor, name='comment_editor'),
        
    path('comment_editor/<int:post_id>/', views.comment_editor, name='comment_editor'),
]
