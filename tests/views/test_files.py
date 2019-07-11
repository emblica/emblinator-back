import unittest
from unittest.mock import Mock

import pytest
from flask import url_for

from tests.factories import (
    job_factory,
    file_factory,
    file_annotation_factory
)


@pytest.mark.usefixtures('test_ctx', 'database')
class TestFiles:
    def test_get_empty(self, client):
        response = client.get(url_for('files.files_get', job_id=10))
        assert response.status_code == 200
        assert response.json == []

    def test_get(self, client):
        job = job_factory()
        file = file_factory(job_id=job.id)
        response = client.get(url_for('files.files_get', job_id=job.id))
        assert response.status_code == 200
        assert response.json == [{
            'annotations': [],
            'bucket_path': '/test-job/my-foto.png',
            'created_at': '2019-03-01T00:00:00+02:00',
            'id': file.id,
            'job_id': job.id,
        }]


@pytest.mark.usefixtures('test_ctx', 'database')
class TestFile:
    @pytest.fixture
    def mock_bucket(self):
        def mock_generate_signed_url(timedelta):
            return 'mock-signed-url'
        mock_blob = Mock()
        mock_blob.generate_signed_url = mock_generate_signed_url

        def mock_list_blobs(prefix, max_results):
            return [mock_blob]

        mock_bucket = Mock()
        mock_bucket.list_blobs = mock_list_blobs
        with unittest.mock.patch(
            'views.files.get_bucket',
            return_value=mock_bucket
        ):
            yield

    @pytest.fixture
    def files(self):
        job = job_factory()
        return [
            file_factory(job_id=job.id),
            file_factory(job_id=job.id),
            file_factory(job_id=job.id),
            file_factory(job_id=job.id),
        ]

    def test_non_existing(self, client, mock_bucket):
        response = client.get(url_for('files.file_get', file_id=123))
        assert response.status_code == 404

    def test_file_get(self, client, mock_bucket):
        job = job_factory()
        file = file_factory(job_id=job.id)
        response = client.get(url_for('files.file_get', file_id=file.id))
        assert response.status_code == 200
        assert response.json == {
            'annotations': [],
            'bucket_path': '/test-job/my-foto.png',
            'created_at': '2019-03-01T00:00:00+02:00',
            'id': 1,
            'signed_url': 'mock-signed-url',
            'job_id': 1
        }

    def test_file_get_next(self, client, mock_bucket, files):
        response = client.get(url_for('files.file_get_next', file_id=files[1].id))
        assert response.status_code == 200
        assert response.json['id'] == files[2].id

    def test_file_get_next_wraps(self, client, mock_bucket, files):
        response = client.get(url_for('files.file_get_next', file_id=files[3].id))
        assert response.status_code == 200
        assert response.json['id'] == files[0].id

    def test_file_get_next_skips_annotated(self, client, mock_bucket, files):
        file_annotation_factory(file_id=files[2].id)
        response = client.get(url_for('files.file_get_next', file_id=files[1].id))
        assert response.status_code == 200
        assert response.json['id'] == files[3].id

    def test_file_get_next_skips_annotated_wraps(self, client, mock_bucket, files):
        file_annotation_factory(file_id=files[0].id)
        response = client.get(url_for('files.file_get_next', file_id=files[3].id))
        assert response.status_code == 200
        assert response.json['id'] == files[1].id
