FROM python:3.13

COPY requirements.txt ./requirements.txt
RUN pip install -r /requirements.txt

COPY main.py ./main.py
COPY configuration.py ./configuration.py
COPY models.py ./models.py


ENTRYPOINT [ "python", "main.py" ]