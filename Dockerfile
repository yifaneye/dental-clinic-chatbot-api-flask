From alpine:latest

RUN apk add --no-cache py-pip
RUN pip3 install --upgrade pip

COPY ./chat /chat
WORKDIR /chat

RUN pip3 install -r requirements.txt

EXPOSE 5003

WORKDIR /chat/chat
ENTRYPOINT ["python3"]
CMD ["__init__.py"]