FROM python:3.8-slim-buster

RUN pip install pipenv==2020.6.2 

COPY Pipfile .
COPY Pipfile.lock .
RUN pipenv install --system --sequential


WORKDIR /app

COPY api.py .
COPY k8s.py .
COPY models.py .

ENV IN_CLUSTER True
EXPOSE 8000

CMD ["uvicorn", "api:app"]