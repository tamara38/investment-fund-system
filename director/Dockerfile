FROM python:3.13

COPY requirements.txt ./requirements.txt
RUN pip install -r /requirements.txt

COPY main.py ./main.py
COPY configuration.py ./configuration.py
COPY decorators.py ./decorators.py


ENTRYPOINT [ "python", "main.py" ]