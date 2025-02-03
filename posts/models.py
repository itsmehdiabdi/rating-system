# posts/models.py
from django.db import models
from django.conf import settings


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    rating_count = models.PositiveIntegerField(default=0)
    rating_sum = models.PositiveIntegerField(default=0)
    smoothed_rating = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    @property
    def average_rating(self):
        return self.rating_sum / self.rating_count if self.rating_count else None

    def __str__(self):
        return self.title


class Rating(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='ratings',
                             db_index=True)
    rating = models.PositiveSmallIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user} rated {self.post} as {self.rating}"
