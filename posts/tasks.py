from celery import shared_task

from posts.models import Post


@shared_task
def update_smoothed_ratings():
    alpha = 0.1  # smoothing factor: adjust as needed (0 < alpha <= 1)
    posts = Post.objects.all()
    for post in posts:
        average_rating = post.average_rating
        if average_rating is None:
            continue  # no ratings yet
        if post.smoothed_rating is None:
            # Initialize smoothed_rating to the current arithmetic average.
            post.smoothed_rating = average_rating
        else:
            # Update using the exponential moving average formula.
            post.smoothed_rating = alpha * average_rating + (1 - alpha) * float(
                post.smoothed_rating
            )
        post.save(update_fields=["smoothed_rating"])

    return "Smoothed ratings updated successfully."
