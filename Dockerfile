FROM python:3.5.2-onbuild

RUN pip install gunicorn

CMD ["/start.sh"]