FROM python

COPY . /app

RUN apt-get update && apt-get install pythin3-pip -y
RUN pip install -r /app/requirements.txt

CMD ["python3", "/app/win-driver.py"]