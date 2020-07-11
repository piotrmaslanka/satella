FROM python:3.8

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN pip install nose2 mock coverage

ADD satella /app/satella
ADD tests /app/tests

ADD tests/test_docker.sh /test_docker.sh
RUN chmod ugo+x /test_docker.sh

WORKDIR /app

CMD ["/test_docker.sh"]
