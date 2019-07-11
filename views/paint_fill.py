import base64
import tempfile

import cv2
import numpy
from flask import Blueprint, jsonify, request

api = Blueprint('paint_fill', __name__, url_prefix='/api')
base64_png_begin = b'data:image/png;base64,'


def base_64_as_image(string_data):
    if not string_data.startswith(base64_png_begin.decode()):
        return ValueError('Invalid parameter, not base64 png string')
    binary_png_data = base64.b64decode(string_data[len(base64_png_begin):])
    return cv2.imdecode(
        numpy.fromstring(binary_png_data, numpy.uint8),
        cv2.IMREAD_UNCHANGED

    )


@api.route('/paint_fill', methods=['POST'])
def paint_fill():
    request

    points = request.json['points']
    base64_image_data = request.json['dataString']
    base64_mask_data = request.json['maskData']
    color = request.json['color']

    image = base_64_as_image(base64_image_data)[:,:,:3]
    original_mask = base_64_as_image(base64_mask_data)

    marker = numpy.ones_like(image[:,:,0]).astype(numpy.int32) * cv2.GC_PR_FGD
    mask_alpha = original_mask[0:10000000, 0:100000, 3]
    mask_red = original_mask[0:10000000, 0:100000, 0]

    marker[numpy.logical_and(mask_alpha > 128, mask_red < 128)] = cv2.GC_BGD
    marker[numpy.logical_and(mask_alpha > 128, mask_red > 128)] = cv2.GC_FGD
    marker[0, :] = cv2.GC_BGD
    marker[:, 0] = cv2.GC_BGD
    marker[-1, :] = cv2.GC_BGD
    marker[:, -1] = cv2.GC_BGD
    marker = numpy.uint8(marker)

    bgd_model = numpy.zeros((1, 65), numpy.float64)
    fgd_model = numpy.zeros((1, 65), numpy.float64)

    marked, _, _ = cv2.grabCut(
        image,
        marker,
        None,
        bgd_model,
        fgd_model,
        5,
        cv2.GC_INIT_WITH_MASK
    )

    mask2 = numpy.where((marked == 2) | (marked == 0), 0, 1).astype('uint8')

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask2 = cv2.erode(numpy.uint8(mask2), kernel, iterations=1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask2 = cv2.dilate(numpy.uint8(mask2), kernel, iterations=1)

    alpha = numpy.ones(mask2.shape) * 0
    alpha[mask2 == 1] = 255

    final_image = numpy.dstack((
        mask2 * color[2],
        mask2 * color[1],
        mask2 * color[0],
        alpha
    ))

    with tempfile.TemporaryDirectory() as file_dir:
        file_path = file_dir + '/file.png'
        cv2.imwrite(file_path, final_image)

        with open(file_path, 'rb') as file_object:
            img_binary_data = file_object.read()

    return jsonify({
        'status': 'ok',
        'image_data': (base64_png_begin + base64.b64encode(img_binary_data)).decode('utf-8')
    })
