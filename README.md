# Emblinator backend

Emblinator is an image annotation tool, designed to make it easy to create annotated images for (among others) supervised machine learning tasks.

This repo hosts the backend for Emblinator. You should checkout the [frontend](https://github.com/emblica/emblinator-front) to get both the frontend and the backend running.

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
- Create virtualenvrionment for python. You should use Python 3.7.4.
- Install imagemagick `brew install freetype imagemagick`
- Install requirements `pip install -r requirements.txt`

#### Create GCP environment
Emblinator uses GCP storage buckets for image storage.
- Set up Google storage (guide [here](https://cloud.google.com/storage/docs/creating-buckets))
  -  your images should be sorted into folders like so:
  ```
    - folder1
        - image1_1
        - image1_2
        - ...
    - folder 2
        - image2_1
        - image2_2
        - ...
  ```
- Set up Google Cloud Platform application credentials (guide [here](https://cloud.google.com/docs/authentication/getting-started))
  - you can create a `/secrets/`-folder for them, that folder is in `.gitignore`

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

### Create database entities

- Use `flask insert-file-info` to create the image and category DB entries. Run this before running server!

```
flask insert-file-info [OPTIONS] PREFIX JOB_NAME CATEGORIES
```
 where
  - `PREFIX` is folder where images are located in bucket
  - `JOB_NAME` is used for ui listing in jobs
  - `CATEGORIES` Comma separated list of categories to be added for this job

For example:
```
#flask insert-file-info waterplants Waterplants water,plant
```

### Run application:
```
flask run
```
