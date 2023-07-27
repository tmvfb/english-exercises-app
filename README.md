# english-exercises-app

[![Website https://english-exercises-app-production.up.railway.app/](https://img.shields.io/website-up-down-green-red/https/english-exercises-app-production.up.railway.app.svg)](https://english-exercises-app-production.up.railway.app/)
[![Github Actions Status](https://github.com/tmvfb/english-exercises-app/workflows/Python%20CI/badge.svg)](https://github.com/tmvfb/english-exercises-app/actions)

## Description
Python package to generate English practice exercises from an uploaded text. Web backend (module **english_exercises_app**) is written in Django. Module **text_processing** is responsible for data processing and exercise generation using *gensim* and *spacy* libraries. Web app includes authentication system to remember user and exercise generation parameters, as well as to store user stats.

**Key features:**
* User registration and authentication, user answer stats
* 4 types of exercises (type text, select correct answer, complete sentence, drag and drop)
* Light/dark mode implementation with Bootstrap 5.3.0
* 2 languages support (English, Russian)

## Prerequisites (for local deploy, Linux)
* Python >=3.8.1
* pip >=22.0
* poetry >=1.4.0
* GNU make
* Configured PostgreSQL database


## Local installation (WSL/Linux)
```
$ git clone https://github.com/tmvfb/english-exercises-app.git
$ cd english-exercises-app.git 
$ make install
```
Then configure environment variables below.  
Apply migrations via `python3 manage.py migrate`.
Run `make dev` to start dev server.

## Environment variables
Add following variables to the .env file:
```
SECRET_KEY=  # should be random
DATABASE_URL=  # PostgreSQL database URL
```

## Todo list
* Full CRUD for users
* New exercise types and adding more variability to old ones 
* Better design for drag and drop exercises 
* Write some tests?