FROM python:3.7.6-slim-buster

RUN pip install -r requirements.txt

EXPOSE 4656

CMD ["./scripts/entrypoint.sh"]