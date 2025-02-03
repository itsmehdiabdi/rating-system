## run proejct
for local setup:
```
python manage.py collectstatic
python manage.py migrate
python manage.py runserver
```
for docker setup:
```
docker compose up --build
```

## load fixture
```
python manage.py loaddata posts/fixtures/posts.json
python manage.py shell < posts/fixtures/users.py
```
note that in docker setup you must enter docker container first.

## load test
```
pip install -r requirements-dev.txt
locust --worker &
locust --master --expect-workers=4
```

## periodic task
You must add periodic task using django admin
