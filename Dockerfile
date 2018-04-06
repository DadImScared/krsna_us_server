FROM python:3.5.2-onbuild

RUN pip install gunicorn

EXPOSE 8000

CMD ["/start.sh"]