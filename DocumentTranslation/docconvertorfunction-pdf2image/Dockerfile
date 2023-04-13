# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:4-python3.10-appservice
#FROM mcr.microsoft.com/azure-functions/python:4-python3.9
FROM mcr.microsoft.com/azure-functions/python:4-python3.9-appservice

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

COPY requirements.txt /
RUN pip install -r /requirements.txt

RUN apt-get install poppler-utils -y
COPY . /home/site/wwwroot



