## run proejct
for local setup:
```
python manage.py collectstatic
python manage.py migrate
python manage.py runserver
```
for docker setup:
```
mkdir postgres_data
sudo chown -R $USER:$USER postgres_data
sudo chmod -R 755 postgres_data
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

