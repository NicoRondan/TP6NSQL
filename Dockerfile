FROM python:latest
WORKDIR /src
COPY . /src
RUN pip3 install flask pymongo 
EXPOSE 5000