import datetime

from models import Job, db, Category, File, FileAnnotation


def category_factory(**kwargs):
    base_parameters = dict(
        name='Puu',
        color='#FF00FF',
        created_at=datetime.datetime(2019, 1, 1)
    )
    category = Category(**dict(**kwargs, **base_parameters))
    db.session.add(category)
    db.session.commit()
    return category


def job_factory():
    job = Job(
        name='Test job',
        prefix='/test-job',
        created_at=datetime.datetime(2019, 2, 1)
    )
    db.session.add(job)
    db.session.commit()
    return job


def file_factory(**kwargs):
    base_parameters = dict(
        bucket_path='/test-job/my-foto.png',
        created_at=datetime.datetime(2019, 3, 1)
    )
    file = File(**dict(**kwargs, **base_parameters))
    db.session.add(file)
    db.session.commit()
    return file


def file_annotation_factory(**kwargs):
    base_parameters = dict(
        data='pngstring',
        created_at=datetime.datetime(2019, 4, 1)
    )
    file_annotation = FileAnnotation(**dict(**kwargs, **base_parameters))
    db.session.add(file_annotation)
    db.session.commit()
    return file_annotation
