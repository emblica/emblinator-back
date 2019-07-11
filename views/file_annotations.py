import base64
import io

import wand
from flask import Blueprint, request, jsonify, make_response, url_for
from wand.image import Image
from wand.display import display

from models import File, FileAnnotation, db
from views.files import get_bucket

api = Blueprint('file_annotations', __name__, url_prefix='/api')


@api.route('/file_annotations')
def file_annotations_get():
    return jsonify([
        {
            'id': file_annotation.id,
            'file_id': file_annotation.file_id,
            'created_at': file_annotation.created_at.isoformat(),
            'image_url': (
                url_for(
                    'file_annotations.file_annotation_get_png',
                    annotation_id=file_annotation.id
                )
            )
        }
        for file_annotation in FileAnnotation.query
    ])


@api.route('/file_annotations/preview/<annotation_id>.png')
def file_annotation_get_preview(annotation_id):
    bucket = get_bucket()

    file_annotation = FileAnnotation.query.get(annotation_id)

    annotation_binary_data = base64.b64decode(
        file_annotation.data[len('data:image/png;base64,'):]
    )
    annotation_file_object = io.BytesIO()
    annotation_file_object.write(annotation_binary_data)
    annotation_file_object.seek(0)

    blob = bucket.blob(file_annotation.file.bucket_path)
    original_file_object = io.BytesIO()
    blob.download_to_file(original_file_object)
    original_file_object.seek(0)

    image_size = 'x300'

    with Image(file=original_file_object) as original_img:
        with Image(file=annotation_file_object) as annotation_img:
            original_img.transform(resize=image_size)
            annotation_img.transform(resize=image_size)
            new_img = original_img.convert('png')

            new_img.composite(
                image=annotation_img,
                left=0,
                top=0,
                operator='dissolve',
                arguments='50',
            )

            binary_data = new_img.make_blob()

            response = make_response(binary_data)
            response.headers.set('Content-Type', 'image/png')

            return response

    return jsonify({'moi': 'hei'})


@api.route('/file_annotations/<annotation_id>.png')
def file_annotation_get_png(annotation_id):
    file_annotation = FileAnnotation.query.get(annotation_id)

    response = make_response(base64.b64decode(
        file_annotation.data[len('data:image/png;base64,'):]
    ))

    response.headers.set('Content-Type', 'image/png')

    return response


@api.route('/file_annotations/<annotation_id>')
def file_annotation_get(annotation_id):
    file_annotation = FileAnnotation.query.get_or_404(annotation_id)

    return jsonify({
        'id': file_annotation.id,
        'file_id': file_annotation.file_id,
        'created_at': file_annotation.created_at.isoformat(),
        'image_url': (
            url_for(
                'file_annotations.file_annotation_get_png',
                annotation_id=file_annotation.id
            )
        )
    })


@api.route('/file_annotations', methods=['POST'])
def file_annotation_post():
    file = File.query.get(request.json['file_id'])

    file_annotation = FileAnnotation(
        file=file,
        data=request.json['image_data'],
        categories=request.json['categories'],
    )
    db.session.add(file_annotation)
    db.session.commit()

    return make_response(jsonify({'status': 'created'}), 201)
