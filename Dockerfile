FROM python:3.8

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install nose2 mock coverage

ADD satella /app/satella
ADD tests /app/tests

WORKDIR /app

CMD ["coverage", "run", "-m", "nose2", "-vv"]
