from django.urls import path
from . import views

urlpatterns = [
    path('', views.annotator_select, name='annotator_select'),  # This comes first!
     path('export/events/csv/', views.export_events_csv, name='export_events_csv'),
    path('export/posts/csv/', views.export_posts_csv, name='export_posts_csv'),
    path('export/user_features/csv/', views.export_user_features_csv, name='export_user_features_csv'),
    path('export/comments/csv/', views.export_comments_csv, name='export_comments_csv'),
    path('calculate_kappa/', views.calculate_kappa_scores, name='calculate_kappa_scores'),
    path('event', views.events_list, name='events'),
    path('event/<str:event_id>/', views.event_posts, name='eventposts'),
    path('event/<str:event_id>/post_editor/', views.post_editor, name='post_editor'),
    path('postcomments/<int:post_id>/<str:event_id>/', views.post_comments_view, name='postcomments'),  # Modified
    path('comment_editor/<int:post_id>/<str:event_id>/<int:comment_index>/', views.comment_editor, name='comment_editor'),
]
