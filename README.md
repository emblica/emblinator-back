
# Annotator backend

## Run locally

- Create virtualenvrionment
- Install imagemagick `brew install freetype imagemagick`
- Install requirements `pip install -r requirements.txt`
- Set environment variables (`GOOGLE_APPLICATION_CREDENTIALS`)
- Run `ENVIRONMENT=local flask run`

## Run and build docker

- `docker build -t annotator-backend .`
- Run dev server: `docker run -it -p 5000:5000 annotator-backend flask run --host 0.0.0.0`
- In production: `docker run -p 8000:8000 annotator-backend`

## Important commands

- Create db schema `flask create-db`
- Create job in db `flask insert-file-info`

## Run tests

 - Make sure you have postgres database `annotator-test` (`createdb annotator-test`)
 - Run `py.test`
