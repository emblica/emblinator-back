import os

import datetime

from flask import Blueprint, jsonify, request, abort
from google.cloud import storage
from sqlalchemy import not_
from sqlalchemy.orm import joinedload

from models import File, db

api = Blueprint('files', __name__, url_prefix='/api')


def get_bucket():
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(
        os.environ['BUCKET_NAME']
    )
    return bucket


def _file_as_dict(file):
    return {
        'id': file.id,
        'job_id': file.job_id,
        'bucket_path': file.bucket_path,
        'created_at': file.created_at.isoformat(),
        'status': file.status,
        'annotations': [
            {
                'id': annotation.id,
                'created_at': annotation.created_at.isoformat()
            }
            for annotation in file.annotations
        ]

    }


@api.route('/files')
def files_get():
    job_id = request.args['job_id']
    annotated = request.args.get('annotated', '')

    query = (
        File
        .query
        .options(joinedload(File.annotations))
        .filter(File.job_id == job_id)
    )

    if annotated in ['1', '0']:
        query = query.filter(
            File.annotations.any()
            if annotated == '1' else
            not_(File.annotations.any())
        )

    return jsonify([
        _file_as_dict(file)
        for file in query
    ])


@api.route('/files/<file_id>/next')
def file_get_next(file_id):
    file = (
        File
        .query
        .filter(
            not_(File.annotations.any()),
            File.id > file_id
        )
        .first()
    )

    if not file:
        file = File.query.filter(not_(File.annotations.any())).first()

    if not file:
        abort(404)

    return jsonify(_file_as_dict(file))


@api.route('/files/<file_id>')
def file_get(file_id):
    file = File.query.get_or_404(file_id)

    bucket = get_bucket()

    file_dict = _file_as_dict(file)
    file_dict['signed_url'] = (
        list(bucket.list_blobs(prefix=file.bucket_path, max_results=1))[0]
        .generate_signed_url(datetime.timedelta(hours=2))
    )

    return jsonify(file_dict)

@api.route('/files/<file_id>', methods=['PUT'])
def file_put(file_id):
    file = File.query.get_or_404(file_id)

    new_status = request.json['status']
    if new_status not in ['done', 'not-done']:
        return jsonify({'error': 'invalid status'}, 400)

    file.status = new_status
    db.session.commit()

    return jsonify(_file_as_dict(file))
