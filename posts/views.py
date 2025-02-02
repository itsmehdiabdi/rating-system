from .forms import RatingForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from django.db.models import F
from .models import Post, Rating
from .serializers import PostSerializer, RatingSerializer
import json  # Add this at the top of the file
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login


class PostListAPIView(generics.ListAPIView):
    """
    GET /posts/
    Returns the list of posts with:
      - title and content,
      - number of ratings (rating_count),
      - average rating (computed from rating_sum and rating_count),
      - and the current user's rating (if available).
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    # Optionally, you could optimize the queryset further
    # (e.g. using select_related or prefetch_related) if needed.


class PostRatingAPIView(generics.GenericAPIView):
    """
    POST /posts/<post_id>/rate/
    Accepts a rating (integer from 0 to 5) for the specified post.
    If the user has already rated the post, the existing rating is updated.
    """
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'detail': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_rating_value = serializer.validated_data['rating']
        user = request.user

        # Use an atomic transaction to avoid race conditions
        with transaction.atomic():
            # Lock the post record to ensure consistent update of aggregated fields
            post = Post.objects.select_for_update().get(pk=post.pk)
            rating_obj, created = Rating.objects.select_for_update().get_or_create(
                post=post,
                user=user,
                defaults={'rating': new_rating_value}
            )
            if not created:
                if rating_obj.rating != new_rating_value:
                    old_rating = rating_obj.rating
                    rating_obj.rating = new_rating_value
                    rating_obj.save(update_fields=['rating', 'updated_at'])
                    # Adjust the aggregated sum without changing the count
                    post.rating_sum = F('rating_sum') - \
                        old_rating + new_rating_value
                    post.save(update_fields=['rating_sum'])
                # If the rating is the same, no action is needed.
            else:
                # New rating: increase both count and sum
                post.rating_count = F('rating_count') + 1
                post.rating_sum = F('rating_sum') + new_rating_value
                post.save(update_fields=['rating_count', 'rating_sum'])

        return Response({'detail': 'Rating saved successfully'}, status=status.HTTP_200_OK)


# posts/views.py (UI Views)

def signup(request):
    """Display the signup form and process user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # creates the user
            auth_login(request, user)  # logs the user in
            return redirect('post-list')  # redirect to the post list after signup
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


def post_list(request):
    """Render a page that lists all posts."""
    posts = Post.objects.all()
    return render(request, "posts/post_list.html", {"posts": posts})


@login_required
def rate_post(request, pk):
    """Handle the rating submission."""
    post = get_object_or_404(Post, id=pk)
    if request.method == "POST":
        try:
            # Parse JSON data from request body
            data = json.loads(request.body)
            rating_value = data.get('rating')
            
            if rating_value is not None:
                if 0 <= rating_value <= 5:  # Validate rating range
                    user = request.user
                    # Use a transaction and select_for_update() to ensure consistency
                    with transaction.atomic():
                        post = Post.objects.select_for_update().get(pk=post.pk)
                        rating_obj, created = Rating.objects.select_for_update().get_or_create(
                            post=post, user=user, defaults={
                                "rating": rating_value}
                        )
                        if not created:
                            if rating_obj.rating != rating_value:
                                old_rating = rating_obj.rating
                                rating_obj.rating = rating_value
                                rating_obj.save(update_fields=["rating"])
                                post.rating_sum = F(
                                    'rating_sum') - old_rating + rating_value
                                post.save(update_fields=["rating_sum"])
                        else:
                            post.rating_count = F('rating_count') + 1
                            post.rating_sum = F(
                                'rating_sum') + rating_value
                            post.save(update_fields=[
                                      "rating_count", "rating_sum"])
                    return redirect("post-list")
        except ValueError:
            pass  # Invalid number provided

    # If we get here, either it's a GET request or the rating submission failed
    form = RatingForm()
    return render(request, "posts/post_list.html", {"form": form, "posts": Post.objects.all()})


class PostDetailAPIView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
