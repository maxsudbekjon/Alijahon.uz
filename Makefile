mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

compile:
	django-admin compilemessages

dumpdata:
	python3 manage.py dumpdata --indent=2 apps.Category > categories.json

loaddata:
	python3 manage.py loaddata categories