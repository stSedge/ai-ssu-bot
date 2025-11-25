FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y dos2unix 

COPY ./backend ./backend
RUN dos2unix /backend/start.sh
WORKDIR /backend
ENV PYTHONPATH=/backend/

# Установка зависимостей напрямую через pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir .

RUN chmod +x ./start.sh
EXPOSE 8000
CMD ["bash", "./start.sh"]
