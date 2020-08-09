FROM python:3

WORKDIR /usr/src/polititweet

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./

RUN pipenv install --system --deploy

COPY polititweet .

RUN SECRET_KEY=secretsecretsecret python manage.py collectstatic

EXPOSE 8080

CMD [ "./launch.sh" ]