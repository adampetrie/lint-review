web: gunicorn -c settings.py lintreview.web:app
worker: celery -A lintreview.tasks worker
