import base64
import colorsys
import io
import os

import click
import sqlalchemy
import werkzeug
from flask import Flask, jsonify
from flask_cors import CORS
from google.cloud import storage


def create_app(environment=os.environ.get('ENVIRONMENT', 'deployment')):
    app = Flask(__name__)

    CORS(app)

    app.config.from_object('configs.' + environment)

    from models import db
    db.init_app(app)

    from views.files import api
    app.register_blueprint(api)
    from views.file_annotations import api
    app.register_blueprint(api)
    from views.jobs import api
    app.register_blueprint(api)
    from views.categories import api
    app.register_blueprint(api)
    from views.paint_fill import api
    app.register_blueprint(api)

    @app.errorhandler(werkzeug.exceptions.HTTPException)
    def handle_bad_request(e):
        if e.name == 'Not Found':
            return jsonify({
                'error': 'Not found'
            }), 404
        elif e.name == 'Bad Request':
            return jsonify({
                'error': 'Error in arguments ({})'.format(', '.join(e.args))
            }), 400
        raise

    @app.errorhandler(sqlalchemy.orm.exc.NoResultFound)
    def handle_no_result_found(e):
        return jsonify({
            'error': 'Not found'
        }), 404

    @app.cli.command()
    def create_db():
        db.drop_all()
        db.create_all()

    @app.cli.command()
    @click.argument('job_id')
    @click.argument('export_path')
    def export_annotations(job_id, export_path):
        from models import File, Category, Job
        from views.files import get_bucket

        bucket = get_bucket()

        job = Job.query.filter_by(id=job_id).one()

        export_path = 'exports/' + export_path + '/'

        annotated_files = (file for file in files if file.annotations)
        for index, file in enumerate(annotated_files, start=1):
            newest_annotation = sorted(
                file.annotations, key=lambda a: a.created_at
            )[-1]

            categories = newest_annotation.categories

            binary_annotation_data = base64.b64decode(
                newest_annotation.data[len('data:image/png;base64,'):]
            )

            # Original
            blob = list(bucket.list_blobs(prefix=file.bucket_path, max_results=1))[0]
            file_object = io.BytesIO()
            blob.download_to_file(file_object)
            file_object.seek(0)
            new_blob = bucket.blob(export_path + f'{index:04d}_original.png')
            new_blob.upload_from_file(file_object)

            # Annotation
            new_blob = bucket.blob(export_path + f'{index:04d}_annotation.png')
            new_blob.upload_from_string(binary_annotation_data)

            # Labels
            new_blob = bucket.blob(export_path + f'{index:04d}_categories.json')
            new_blob.upload_from_string(categories)

    @app.cli.command()
    @click.argument('prefix')
    @click.argument('job_name')
    @click.argument('categories')
    def insert_file_info(prefix, job_name, categories):
        # prefix = '70de_big/'
        # job_name = 'Test images 70 degree angle'

        category_names = [c.capitalize() for c in categories.split(',')]

        from models import File, Category, Job

        job = Job(
            name=job_name,
            prefix=prefix
        )
        db.session.add(job)

        for category_index, category_name in enumerate(category_names):
            h_value = category_index * 1.0 / len(category_names)

            # Remove green
            green_width_in_h_space = 0.33
            green_start_in_h_space = 0.116
            h_value = h_value * (1 - green_width_in_h_space)
            if h_value > green_start_in_h_space:
                h_value += green_width_in_h_space

            HSV_tuple = (
                h_value,
                [0.3, 0.6, 0.9][category_index % 3],
                [1.0, 0.9, 0.8][category_index % 3]
            )
            RGB_tuple = colorsys.hsv_to_rgb(*HSV_tuple)

            db.session.add(Category(
                job=job,
                name=category_name,
                color='#' + ''.join([
                    '{0:02x}'.format(int(255 * part))
                    for part in RGB_tuple
                ])
            ))

        storage_client = storage.Client()
        bucket = storage_client.get_bucket(
            os.environ['BUCKET_NAME']
        )

        for blob in bucket.list_blobs(prefix=prefix):
            if any(
                blob.path.lower().endswith('.' + extension)
                for extension in [
                    'jpg', 'jpeg', 'png'
                ]
            ):
                db.session.add(File(
                    bucket_path=blob.name,
                    job=job,
                ))

        db.session.commit()

    return app


if __name__ == '__main__':
    app = create_app()
else:
    gunicorn_app = create_app()
