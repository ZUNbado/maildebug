FROM python:2-onbuild
EXPOSE 8000
CMD ["uwsgi", "--http", "0.0.0.0:8000", "--module", "main:app", "--processes", "1", "--threads", "8"]
