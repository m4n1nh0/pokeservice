FROM python:3.10
LABEL maintainer="Mariano Mendonça <marianofmendonca@gmail.com>"
WORKDIR /code/

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update &&  \
    apt-get install -y --no-install-recommends gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

#Updade pip
RUN python -m pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . /code/

EXPOSE 8080
CMD [ "sh", "-c", "alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8080"]