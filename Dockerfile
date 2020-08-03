FROM python:3.7.6-slim-buster

EXPOSE 4656

COPY . .

RUN pip install -r requirements.txt

CMD ["./scripts/entrypoint.sh"]