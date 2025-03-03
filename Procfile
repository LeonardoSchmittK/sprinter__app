Procfile

web: gunicorn sprinter.wsgi --log-file - 
#or works good with external database
web: python manage.py migrate && gunicorn sprinter.wsgi
