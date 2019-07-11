from flask import Blueprint, request, jsonify

from models import Category

api = Blueprint('categories', __name__, url_prefix='/api')


@api.route('/categories')
def categories():
    job_id = request.args['job_id']

    category_query = Category.query.filter(Category.job_id == job_id)

    return jsonify([
        {
            'id': category.id,
            'job_id': category.job_id,
            'name': category.name,
            'color': category.color,
        }
        for category in category_query
    ])