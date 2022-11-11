FROM python:3.10-alpine

# Change localtime
RUN cp /usr/share/zoneinfo/Europe/Andorra /etc/localtime
RUN echo "Europe/Andorra" > /etc/timezone

ADD . /scrapyrealestate/
WORKDIR /scrapyrealestate/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./main.py"]