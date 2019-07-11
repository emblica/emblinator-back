from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import backref

db = SQLAlchemy()


class BaseMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Job(db.Model, BaseMixin):
    id = Column(Integer, primary_key=True, nullable=False)

    name = Column(String, nullable=False)
    prefix = Column(String, nullable=False)


class Category(db.Model, BaseMixin):
    id = Column(Integer, primary_key=True, nullable=False)

    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    job = db.relationship('Job')

    name = Column(String, nullable=False)
    color = Column(String, nullable=False)


class File(db.Model, BaseMixin):
    id = Column(Integer, primary_key=True, nullable=False)

    job_id = Column(Integer, ForeignKey('job.id'), nullable=False)
    job = db.relationship('Job', backref='files')

    bucket_path = Column(String, nullable=False)

    status = Column(String, nullable=True)
    # ALTER TABLE file ADD COLUMN status character varying;


class FileAnnotation(db.Model, BaseMixin):
    id = Column(Integer, primary_key=True)

    file_id = Column(Integer, ForeignKey('file.id'), nullable=False)
    file = db.relationship(
        'File',
        backref=backref('annotations', order_by='FileAnnotation.created_at')
    )

    data = Column(String, nullable=False)
    categories = Column(String, nullable=False)
