FROM python:3.8-slim-buster

RUN pip install pipenv==2020.6.2 

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system

WORKDIR /fog-rollouts

COPY fog-rollouts .
# CMD [ "python", "watcher.py" ]