migrate:
	docker exec django-coding-challenge_license-server_1 python manage.py migrate

migrations:
	docker exec django-coding-challenge_license-server_1 python manage.py makemigrations

test:
	docker exec django-coding-challenge_license-server_1 python manage.py test

user:
	docker exec -it django-coding-challenge_license-server_1 python manage.py createsuperuser

bash:
	docker exec -it django-coding-challenge_license-server_1 /bin/bash
