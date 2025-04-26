from django.urls import path
from . import views

urlpatterns = [
    path('', views.events_list, name='events'),
    path('eventposts/<str:event_id>/', views.eventposts, name='eventposts'),
]
