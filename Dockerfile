FROM python:3

WORKDIR /usr/src/polititweet

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY polititweet .

RUN SECRET_KEY=secretsecretsecret python manage.py collectstatic

EXPOSE 8080

CMD [ "./launch.sh" ]