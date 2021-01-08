from base64 import b64decode, b64encode
from io import BytesIO

import numpy as np
from PIL import Image


def base64image_to_array(base64image):
	head, data = base64image.split(',', 1)

	extension = head.split(';')[0].split('/')[1]
	data = b64decode(str.encode(data))

	image = Image.open(BytesIO(data))
	image = np.array(image)

	return extension, image


def array_to_base64image(array):
	image = Image.fromarray(array)

	buffer = BytesIO()
	image.save(buffer, format='png')

	encoded_image = b64encode(buffer.getvalue()).decode('utf-8')

	return encoded_image
