
This his how to run the project

create .env file and then fill it with the following keys and appropriate values

* POSTGRES_DB
* POSTGRES_USER
* POSTGRES_PASSWORD
* PSG_HOST
* PSG_PORT
* ES_NAME
* ELASTIC_PASSWORD
* DEBUG
* SECRET_KEY
* EMAIL_USER
* EMAIL_PASS
* CLIENT_URL i.e the front end to redirect to after email confirm

Then

* docker-compose up --build

Then exec into the docker image and run these scripts in order

* ./migrate.sh
* ./scrapy.sh
* ./collectstatic.sh
* ./elasticsearch.sh
