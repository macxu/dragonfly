FROM python

RUN mkdir /web
WORKDIR /web

RUN mkdir /web/app

ADD ./app /web/app/

EXPOSE 5000

WORKDIR /web/app

RUN ["pip", "install", "-r", "requirements.txt"]

# PYTHONPATH is required, otherwise Python complains about module not found
ENV PYTHONPATH /web

CMD ["python", "/web/app/run.py"]