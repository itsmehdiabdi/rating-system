from django.urls import path
from .views import PostListAPIView, PostRatingAPIView, PostDetailAPIView

urlpatterns = [
    path('posts/', PostListAPIView.as_view(), name='post-list'),
    path('posts/<int:pk>/rate/', PostRatingAPIView.as_view(), name='post-rate'),
    path('posts/<int:pk>/', PostDetailAPIView.as_view(), name='post-detail-api'),
]
