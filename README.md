# english-exercises-app

[![Website https://english-exercises-app-production.up.railway.app/](https://img.shields.io/website-up-down-green-red/https/english-exercises-app-production.up.railway.app.svg)](https://english-exercises-app-production.up.railway.app/)
[![Github Actions Status](https://github.com/tmvfb/english-exercises-app/workflows/Python%20CI/badge.svg)](https://github.com/tmvfb/english-exercises-app/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/620bb3a35893a3f0e87e/maintainability)](https://codeclimate.com/github/tmvfb/english-exercises-app/maintainability)

## Description
Python package to generate English practice exercises from an uploaded text. Requires authentication and *.txt* file in English to start.
  
Web backend (module **english_exercises_app**) is written in [django](https://github.com/django/django). Module **text_processing** is responsible for data processing and exercise generation using [*gensim*](https://github.com/RaRe-Technologies/gensim) and [*spaCy*](https://github.com/explosion/spaCy) libraries. Web app includes authentication system to remember user and exercise generation parameters, as well as to store user stats. App is deployed using [Railway](https://railway.app/).
  
Local deploy is possible using either Linux/WSL or Docker.
  
**Key features:**
* User registration and authentication, user answer stats
* 4 types of exercises (type text, select correct answer, complete sentence, drag and drop)
* Light/dark mode implementation with Bootstrap 5.3.0
* 2 languages support (English, Russian)

## Prerequisites for local deploy
**Linux/WSL:**  
* Python >=3.8.1
* pip >=22.0
* poetry >=1.4.0
* GNU make
* Configured PostgreSQL database (app won't work with other database types due to use of Django ArrayField)
  
**Docker:**  
* Latest releases of Docker and Docker Compose
* Configured PostgreSQL database

## Local installation
Clone repository:
```
$ git clone https://github.com/tmvfb/english-exercises-app.git
$ cd english-exercises-app.git 
```
Then configure environment variables below.  
Further steps depend on the platform:
   
**Linux/WSL:**  
```
$ make install
# apply migrations and configure static files
$ python3 manage.py migrate
$ python3 manage.py collectstatic --noinput
# run to start dev server
$ make dev
```
Run `deactivate` to exit virtual environment.
  
**Docker:**  
```
docker compose build
docker compose run web python3 manage.py migrate
docker compose run web python3 manage.py collectstatic --noinput
docker compose up
```

## Environment variables
Add following variables to the .env file:
```
SECRET_KEY=
DATABASE_URL=  # PostgreSQL database URL in the format postgres://{user}:{password}@{hostname}:{port}/{database-name}
```

## Todo list
1. Full CRUD for users
2. New exercise types and adding more variability to old ones 
3. Better design for drag and drop exercises 
4. Consider TDD for further development
