FROM python:3.8.10
RUN mkdir /code
ADD ./requirements.txt /code
ADD ./tema2SPRC.py /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python3 tema2SPRC.py
