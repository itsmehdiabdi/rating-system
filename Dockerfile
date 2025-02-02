FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port 8000 for Django
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "python manage.py migrate && gunicorn bp.wsgi:application --bind 0.0.0.0:8000"]
