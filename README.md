# english-exercises-app

[![Website https://english-exercises-app-production.up.railway.app/](https://img.shields.io/website-up-down-green-red/https/english-exercises-app-production.up.railway.app.svg)](https://english-exercises-app-production.up.railway.app/)
[![Github Actions Status](https://github.com/tmvfb/english-exercises-app/workflows/Python%20CI/badge.svg)](https://github.com/tmvfb/english-exercises-app/actions)
[![Maintainability](https://api.codeclimate.com/v1/badges/620bb3a35893a3f0e87e/maintainability)](https://codeclimate.com/github/tmvfb/english-exercises-app/maintainability)  

Combining my backend and <s>scarce</s> frontend skills with some deep learning-powered text processing :)  
Find current deployed GitHub version by clicking the "website" icon above.

## Description
This repository contains code and deploy instructions for a web app that generates English practice exercises from an uploaded text. App requires authentication and a *.txt* file in English to start.   
  
Module **english_exercises_app** is written in [django](https://github.com/django/django) and accounts for web backend. Module **text_processing** is responsible for data processing and exercise generation using [*gensim*](https://github.com/RaRe-Technologies/gensim) and [*spaCy*](https://github.com/explosion/spaCy) libraries. Web app includes authentication system to remember user and exercise generation parameters, as well as to store user stats. App is deployed using [Railway](https://railway.app/).
  
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
* Configured PostgreSQL database (app won't work with other database types due to the use of Django ArrayField)
  
**Docker:**  
* Latest releases of Docker and Docker Compose

## Local installation
Clone repository:
```
$ git clone https://github.com/tmvfb/english-exercises-app.git
$ cd english-exercises-app.git 
```
Further steps depend on the platform:
   
**Linux/WSL:**  
First, configure environment variables below. Then:
```
$ make install
# apply migrations
$ python3 manage.py migrate
# run to start dev server
$ make dev
```
Run `deactivate` to exit virtual environment.
  
**Docker:**  
```
docker compose build
docker compose run web python3 manage.py migrate
docker compose up
```
To use a custom PostgreSQL database, django secret key, and API for audio generation, you can also create a .env file and specify the environment variables below before running the first command.  

## Environment variables
Add following variables to the .env file:
```
SECRET_KEY=
DATABASE_URL=  # PostgreSQL database URL in the format postgres://{user}:{password}@{hostname}:{port}/{database-name}
HUGGINGFACE_API_TOKEN=  # api token from huggingface.co. Audio generation works only if a token was provided
```

## Todo list
* [x] Full CRUD for users (partially implemented)  
* [x] New exercise types and adding more variability to old ones (added audio playback)  
* [ ] Better design for drag and drop exercises (wontfix, JS is not fun)  
* [ ] Consider TDD for further development  

## Notes on design flaws
* Drag and drop exercises currently handle only the perfect use case (e. g. without re-dragging or choosing another word).
* Adding new features (e.g. new exercise types) could have been made simpler, but I wanted the Django and text processing modules to be as independent as possible.
* Django may be not the best idea for implementation of such project. There is too much frontend, so something like streamlit would suit better. I chose Django because I wanted to improve my skills in something I had already learned, and also wanted to have stats for users.
* Static files serving in the demonstration project is configured via Whitenoise. Whitenoise can NOT handle media files, and Django also doesn't offer such functionality in production. This is why audio (which is user-generated media) playback is only possible by either configuring web server (telling the web server explicitly where to find media files) or using a cloud for media files storage (like S3). As the former is not viable and the latter is questionable on Railway, the app currently runs in dev mode to demonstrate all the functionality.
