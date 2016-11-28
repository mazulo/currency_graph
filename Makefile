setup:
	pip install -r requirements.txt
	bower install --allow-root
	./manage.py migrate
