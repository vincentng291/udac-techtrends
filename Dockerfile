FROM python:3.8

LABEL maintainer="Teerapat Prommarak"

COPY ./techtrends /app

WORKDIR /app

RUN pip install -r requirements.txt

RUN python ./init_db.py

EXPOSE 3111

CMD [ "python3", "app.py" ]