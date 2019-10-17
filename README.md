
# Annotator backend

## Table of Contents
- [Running](#Running)
- [Setup](#Setup)

## Run locally

### Running application
- export env variables:
```
. ./export_local_db_variables.sh
```
- start Postgres in case it is stopped:
```
docker start emblinator-postgres
```
- Run Flask server:
```
flask run
```  

### Run and build docker in development

- fill `docker.env_default` and rename to `docker.env` 
- Create network for containers `docker network create emblinator`
- Add postgres to network `docker network connect emblinator emblinator-postgres`
- `docker build -t annotator-backend .`
- Run dev server: `docker run -it -p 5000:5000 --env-file docker.env --network emblinator  annotator-backend flask run --host 0.0.0.0`

### Run and build docker in production
 - TODO

## Important commands

- Create db schema `flask create-db`
- Create job in db `flask insert-file-info`

## Run tests

 - Make sure you have postgres database `annotator-test` (`createdb annotator-test`)
 - Run `py.test`

## Setup

#### Create python environment
- Create virtualenvrionment for python
- Install imagemagick `brew install freetype imagemagick`
- Install requirements `pip install -r requirements.txt`
- Set appropriate environment variables (`GOOGLE_APPLICATION_CREDENTIALS`).

#### Create database
- export env variables:
```
. ./export_local_db_variables.sh
```
- start a new postgres in docker:
```
docker run --name emblinator-postgres -d -e POSTGRES_DB=$POSTGRES_DB_NAME -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD -e POSTGRES_USER=$POSTGRES_USER -p 5432:5432 postgres
```
- setup DB:
```
flask create-db
```
- Create new job with images to be annotated
    - `PREFIX` Folder where images are located in bucket
    - `JOB_NAME` Ui listing in jobs
    - `CATEGORIES` Comma separated list of categories to be added for this job
```
flask insert-file-info [OPTIONS] PREFIX JOB_NAME CATEGORIES
#flask insert-file-info waterplants Waterplants water,plant
```
- run application:
```
flask run
```
