migrate:
	docker exec django-coding-challenge_license-server_1 python manage.py migrate

test:
	docker exec django-coding-challenge_license-server_1 python manage.py test
