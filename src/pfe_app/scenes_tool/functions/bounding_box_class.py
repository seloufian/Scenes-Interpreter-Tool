import numpy as np


class BoundingBox:

	def __init__(self, xmin, ymin, xmax, ymax):
		self.xmin = xmin
		self.ymin = ymin
		self.xmax = xmax
		self.ymax = ymax
		self.area = abs(xmax - xmin) * abs(ymax - ymin)


	def get_features_array(self, other, image_dimensions, rate=0.05):
		ref_area = np.prod(image_dimensions)
		ref_len = np.sqrt(np.sum(np.square(image_dimensions)))

		features_list = list()
		features_list.append(self.importance(ref_area))
		features_list.append(self.size(other, rate))
		features_list.extend(self.positions(other))
		features_list.append(self.iou(other))
		features_list.append(self.collision(other))
		features_list.append(self.distance(other, ref_len))

		return np.array(features_list)


	def importance(self, ref_area):
		area_rate = self.area / ref_area

		if area_rate <= 0.01:
			return 0 # Less important

		elif 0.01 < area_rate <= 0.1:
			return 1

		elif 0.1 < area_rate <= 0.2:
			return 2

		return 3 # Most important


	def size(self, other, rate=0.05):
		if self.area == 0:
			return 2 if other.area else 1
		else:
			if 1-rate <= other.area / self.area <= 1+rate:
				return 1 # "other" is EQUAL to "self"

			elif other.area > self.area:
				return 2 # "other" is BIGGER than "self"

			return 0 # "other" is SMALLER than "self"


	def positions(self, other):
		positions_list = [0, 0, 0, 0]

		if self.xmax <= other.xmin: # "other" is on the RIGHT of "self"
			positions_list[0] = 1

		if other.xmax <= self.xmin: # "other" is on the LEFT of "self"
			positions_list[1] = 1

		if self.ymax <= other.ymin: # "other" is ON "self"
			positions_list[2] = 1

		if other.ymax <= self.ymin: # "other" is UNDER "self"
			positions_list[3] = 1

		return positions_list


	def intersects(self, other):
		if self.xmax <= other.xmin or self.xmin >= other.xmax:
			return False

		if self.ymax <= other.ymin or self.ymin >= other.ymax:
			return False

		return True


	def intersection(self, other):
		if self.intersects(other):
			xmin = max(self.xmin, other.xmin)
			ymin = max(self.ymin, other.ymin)

			xmax = min(self.xmax, other.xmax)
			ymax = min(self.ymax, other.ymax)

			return BoundingBox(xmin, ymin, xmax, ymax)

		return None


	def iou(self, other):
		if self.intersects(other):
			inter_area = self.intersection(other).area
			iou_value = inter_area / (self.area + other.area - inter_area)

			if iou_value <= 0.05:
				return 0

			elif 0.05 < iou_value <= 0.15:
				return 1

			elif 0.15 < iou_value <= 0.7:
				return 2

			elif 0.7 < iou_value <= 0.9:
				return 3

			return 4

		return -1


	def collision(self, other):
		if self.intersects(other):
			inter_area = self.intersection(other).area

			rel_area = inter_area / self.area if self.area > 0 else 0

			if rel_area <= 0.05:
				return 0 # "self" TOUCHES "other"

			elif 0.05 < rel_area <= 0.15:
				return 1 # small intersection

			elif 0.15 < rel_area <= 0.7:
				return 2 # medium intersection

			elif 0.7 < rel_area <= 0.95:
				return 3 # big intersection

			return 4 # "self" CONTAINS "other"

		return -1 # There is no collision


	def real_distance(self, other):
		positions = self.positions(other)

		if positions[1] and positions[2]:
			p1 = np.array((self.xmin, self.ymax))
			p2 = np.array((other.xmax, other.ymin))
			return np.linalg.norm(p1 - p2)

		elif positions[1] and positions[3]:
			p1 = np.array((self.xmin, self.ymin))
			p2 = np.array((other.xmax, other.ymax))
			return np.linalg.norm(p1 - p2)

		elif positions[0] and positions[3]:
			p1 = np.array((self.xmax, self.ymin))
			p2 = np.array((other.xmin, other.ymax))
			return np.linalg.norm(p1 - p2)

		elif positions[0] and positions[2]:
			p1 = np.array((self.xmax, self.ymax))
			p2 = np.array((other.xmin, other.ymin))
			return np.linalg.norm(p1 - p2)

		elif positions[0]:
			return other.xmin - self.xmax

		elif positions[1]:
			return self.xmin - other.xmax

		elif positions[2]:
			return self.ymin - self.ymax

		elif positions[3]:
			return self.ymin - other.ymax

		else:
			return 0.


	def distance(self, other, ref_len=1):
		if not self.intersects(other):
			distance = self.real_distance(other) / ref_len

			if 0 <= distance <= 0.01:
				return 0 # "other" TOUCHES "self"

			elif 0.01 < distance <= 0.1:
				return 1 # "other" is NEAR of "self"

			elif 0.1 < distance <= 0.2:
				return 2 # "other' is in PROXIMITY of "self"

			return 3 # "other" is FAR of "self"

		return -1 # The distance is zero (the two boxes are in collision)
