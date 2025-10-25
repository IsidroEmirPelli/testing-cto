#!/bin/bash
set -e

echo "🚀 Starting News Scraping System..."

# Wait for database
echo "⏳ Waiting for database..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✅ Database is ready!"

# Run migrations
echo "📊 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist (only in dev)
if [ "$DEBUG" = "True" ]; then
    echo "👤 Creating default superuser (if not exists)..."
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
END
fi

echo "✨ Starting application server..."
exec "$@"
