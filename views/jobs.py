from flask import Blueprint, jsonify
from sqlalchemy import func

from models import Job, db, FileAnnotation, File

api = Blueprint('jobs', __name__, url_prefix='/api')


@api.route('/jobs')
def jobs():
    annotations_subquery = (
        db.session
        .query(
            File.id.label('file_id'),
            func.count(FileAnnotation.id).label('annotation_count')
        )
        .join(
            FileAnnotation, File.id == FileAnnotation.file_id
        )
        .group_by(File)
        .cte()
    )

    done_subquery = (
        db.session
        .query(
            File.id.label('file_id')
        )
        .filter(
            File.status == 'done'
        )
        .cte()
    )

    query = (
        db.session
        .query(
            Job,
            func.count(File.id),
            func.count(annotations_subquery.c.annotation_count),
            func.count(done_subquery.c.file_id)
        )
        .outerjoin(File, File.job_id == Job.id)
        .outerjoin(annotations_subquery, File.id == annotations_subquery.c.file_id)
        .outerjoin(done_subquery, File.id == done_subquery.c.file_id)
        .group_by(Job)
        .order_by(Job.id)
    )

    return jsonify([
        {
            'id': job.id,
            'name': job.name,
            'prefix': job.prefix,
            'file_count': file_count,
            'annotated_count': annotated_count,
            'done_count': done_count,
        }
        for job, file_count, annotated_count, done_count in query
    ])

@api.route('/job/<id>')
def job(id):
    job = Job.query.filter_by(id=id).first()
    return jsonify({
        'id': job.id,
        'name': job.name
    })
