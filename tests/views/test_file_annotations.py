import pytest
from flask import url_for

from tests.factories import (
    job_factory,
    file_factory,
    file_annotation_factory
)


@pytest.fixture
def file_annotation():
    job = job_factory()
    file = file_factory(job_id=job.id)
    return file_annotation_factory(file_id=file.id)


@pytest.mark.usefixtures('test_ctx', 'database')
class TestFileAnnotationsGet:
    def test_returns_200(self, client, file_annotation):
        response = client.get(url_for('file_annotations.file_annotations_get'))
        assert response.status_code == 200

    def test_returns_correct_data(self, client, file_annotation):
        response = client.get(url_for('file_annotations.file_annotations_get'))
        assert response.json == [
            {
                'created_at': file_annotation.created_at.isoformat(),
                'file_id': 1,
                'id': 1,
                'image_url': 'http://localhost/api/file_annotations/1.png'
            }
        ]


@pytest.mark.usefixtures('test_ctx', 'database')
class TestFileAnnotationGet:
    def test_returns_404_with_unkonown_id(self, client):
        response = client.get(url_for(
            'file_annotations.file_annotation_get',
            annotation_id=5
        ))
        assert response.status_code == 404
        assert response.json == {'error': 'Not found'}

    def test_returns_200(self, client, file_annotation):
        response = client.get(url_for(
            'file_annotations.file_annotation_get',
            annotation_id=file_annotation.id
        ))
        assert response.status_code == 200

    def test_returns_correct_data(self, client, file_annotation):
        response = client.get(url_for(
            'file_annotations.file_annotation_get',
            annotation_id=file_annotation.id
        ))
        assert response.json == {
            'created_at': file_annotation.created_at.isoformat(),
            'file_id': 1,
            'id': 1,
            'image_url': 'http://localhost/api/file_annotations/1.png'
        }
