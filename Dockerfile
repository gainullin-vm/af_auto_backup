FROM python:latest

RUN apt-get update

COPY backup2.py /home/ubuntu/backup2.py
COPY dev02_access /home/ubuntu/.ssh/dev02_access
COPY server460_access /home/ubuntu/.ssh/server460_access
COPY prod_af_access /home/ubuntu/.ssh/prod_af_access

WORKDIR /home/ubuntu/

CMD ["python3", "/home/ubuntu/backup2.py"]

