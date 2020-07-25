FROM python:3.8

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt && \
    pip install nose2 mock coverage nose2[mp] nose2[coverage_plugin]

ADD satella /app/satella
ADD tests /app/tests
ADD unittest.cfg /app/unittest.cfg
ADD setup.py /app/setup.py
ADD setup.cfg /app/setup.cfg
ADD LICENSE /app/LICENSE
ADD README.md /app/README.md
ADD MANIFEST.in /app/MANIFEST.in

ADD tests/test_docker.sh /test_docker.sh
RUN chmod ugo+x /test_docker.sh

WORKDIR /app

CMD ["/test_docker.sh"]
