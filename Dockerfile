FROM python:3.13

COPY authentication/requirements.txt ./requirements.txt
RUN pip install -r /requirements.txt

COPY authentication/migrate.py ./migrate.py
COPY authentication/configuration.py ./configuration.py
COPY authentication/models.py ./models.py


ENTRYPOINT [ "python", "migrate.py" ]