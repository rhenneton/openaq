FROM python:3.7
WORKDIR /code
COPY python/requirements.txt .
RUN pip install -r requirements.txt
COPY python/ .
EXPOSE 8050

RUN python setup.py install

CMD ["python", "openaq/dashboard/main.py"]
