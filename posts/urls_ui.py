# posts/urls_ui.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post-list'),
    path('posts/<int:pk>/rate/', views.rate_post, name='rate-post'),
]
