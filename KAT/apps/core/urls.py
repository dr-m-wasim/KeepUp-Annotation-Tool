from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='annotator_select'),
    path('events', views.events_list, name='events'),
    path('event/<str:event_id>', views.event_posts, name='eventposts'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('postcomments/<int:post_id>/<str:event_id>/', views.post_comments_view, name='postcomments'),
    path('post/<int:post_id>/comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    
    # for exporting and calcluating kappa score
    path('export/events/csv/', views.export_events_csv, name='export_events_csv'),
    path('export/posts/csv/', views.export_posts_csv, name='export_posts_csv'),
    path('export/user_features/csv/', views.export_user_features_csv, name='export_user_features_csv'),
    path('export/comments/csv/', views.export_comments_csv, name='export_comments_csv'),
    path('calculate_kappa/', views.calculate_kappa_scores, name='calculate_kappa_scores'),
]
