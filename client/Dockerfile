FROM python

COPY . /app

RUN apt-get update && apt-get install python3-pip -y
RUN pip install -r /app/requirements.txt

CMD ["cd" "/app"]
CMD ["python3", ".win-driver.py"]