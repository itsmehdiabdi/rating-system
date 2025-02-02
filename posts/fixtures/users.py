# Run in Django shell: python manage.py shell
from django.contrib.auth import get_user_model

User = get_user_model()
NUM_USERS = 1000
for i in range(1, NUM_USERS + 1):
    username = f"testuser_{i}"
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password="password")
    else:
        print(f"User {username} already exists")
