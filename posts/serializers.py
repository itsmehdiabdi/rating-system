from rest_framework import serializers
from .models import Post


class PostSerializer(serializers.ModelSerializer):
    # Compute the average rating using the denormalized fields
    average_rating = serializers.SerializerMethodField()
    # Expose the cached rating_count
    rating_count = serializers.IntegerField(read_only=True)
    # Include the rating given by the current user (if any)
    user_rating = serializers.SerializerMethodField()
    smoothed_rating = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'rating_count',
                  'average_rating', 'user_rating', 'smoothed_rating']

    def get_average_rating(self, obj):
        if obj.rating_count:
            return obj.rating_sum / obj.rating_count
        return None

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Try to get the rating given by the current user for this post.
            rating_obj = obj.ratings.filter(user=request.user).first()
            if rating_obj:
                return rating_obj.rating
        return None

    def get_smoothed_rating(self, obj):
        return obj.smoothed_rating


class RatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=0, max_value=5)
