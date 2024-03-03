FROM ubuntu:latest
LABEL authors="mariano"

ENTRYPOINT ["top", "-b"]