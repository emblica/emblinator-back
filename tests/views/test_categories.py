import pytest
from flask import url_for

from tests.factories import job_factory, category_factory


@pytest.mark.usefixtures('test_ctx', 'database')
class TestCategories:
    @pytest.fixture
    def job(self):
        return job_factory()

    @pytest.fixture
    def categories(self, job):
        category_factory(job_id=job.id)
        category_factory(job_id=job.id)

    def test_returns_400_without_proper_arguments(self, client):
        response = client.get(url_for('categories.categories'))
        assert response.status_code == 400
        assert response.json == {
            'error': 'Error in arguments (job_id)'
        }

    def test_returns_200(self, client, categories, job):
        response = client.get(url_for('categories.categories', job_id=job.id))
        assert response.status_code == 200

    def test_returns_empty_list_on_unknown_category(self, client):
        response = client.get(url_for('categories.categories', job_id=5))
        assert response.status_code == 200
        assert response.json == []

    def test_returns_correct_data(self, client, categories, job):
        response = client.get(url_for('categories.categories', job_id=job.id))
        assert response.json == [
            {
                'color': '#FF00FF',
                'id': 1,
                'job_id': 1,
                'name': 'Puu'
            },
            {
                'color': '#FF00FF',
                'id': 2,
                'job_id': 1,
                'name': 'Puu'
            }
        ]

    def test_does_not_return_categories_from_other_job(
        self, client, categories, job
    ):
        category_factory(job_id=job_factory().id)
        response = client.get(url_for('categories.categories', job_id=job.id))
        assert len(response.json) == 2
