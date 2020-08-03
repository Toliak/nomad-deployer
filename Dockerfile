FROM python:3.7.6-slim-buster

EXPOSE 4656

WORKDIR /app/

VOLUME /opt/data/

COPY /app/ .

RUN pip install -r requirements.txt

CMD ["./scripts/entrypoint.sh"]