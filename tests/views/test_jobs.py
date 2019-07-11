import pytest
from flask import url_for

from tests.factories import job_factory


@pytest.mark.usefixtures('test_ctx', 'database')
class TestJobs:
    def test_returns_200(self, client):
        job_factory()
        response = client.get(url_for('jobs.jobs'))
        assert response.status_code == 200

    def test_returns_correct_data(self, client):
        job_factory()
        response = client.get(url_for('jobs.jobs'))
        assert response.json == [
            {
                'id': 1,
                'name': 'Test job',
                'prefix': '/test-job'
            }
        ]
