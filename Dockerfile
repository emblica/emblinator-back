FROM python:3.7-slim
ENV MAGICK_HOME=/usr
RUN apt-get update && \
    apt-get install -y imagemagick libsm6 libxext6 libxrender-dev
WORKDIR /app
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY ./ ./
CMD ["gunicorn","--bind", "0.0.0.0:8000", "app:gunicorn_app"]
