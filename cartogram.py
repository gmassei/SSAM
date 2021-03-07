"""
/***************************************************************************
Name            : cartogram
Description     :build a cartogram inside SSAM - Spatial Sustainability 
				Assessment Model Based on Carson Farmer QGIS plugin and on 
				an algorithm proposed in the following paper: Dougenik, J. A, 
				N. R. Chrisman, and D. R. Niemeyer. 1985.  "An algorithm to 
				construct continuous cartograms."  Professional Geographer 37:75-81
Date			: 10/05/2019
copyright       : ARPA Umbria - Universita' degli Studi di Perugia (C) 2016
email           : (developper) Gianluca Massei (g_massa@libero.it)

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt5.QtCore import pyqtSignal, QObject, QVariant
from qgis.core import QgsDistanceArea, QgsGeometry, QgsPointXY


import os,sys
import math
import traceback


class CartogramFeature(object):
	"""Stores various calculated values for each feature."""

	def __init__(self):
		self.center_x = -1
		self.center_y = -1
		self.value = -1
		self.area = -1
		self.mass = -1
		self.radius = -1

class CartogramWorker(QObject):
	"""Background worker which actually creates the cartogram."""

	finished = pyqtSignal(object, int)
	error = pyqtSignal(Exception, basestring)
	progress = pyqtSignal(float)

	def __init__(self, layer, field_name, iterations):
		"""Constructor."""
		QObject.__init__(self)

		self.layer = layer
		self.field_name = field_name
		self.iterations = iterations

		# used to store the computed minimum value when the input data contains
		# zero or null values in the column used to create the cartogram
		self.min_value = None

		# set default exit code - if this doesn't change everything went well
		self.exit_code = -1

	def run(self):
		ret = None
		feature_count = self.layer.featureCount()

		step = self.get_step()
		steps = 0

		for i in range(self.iterations):
			(meta_features,
				force_reduction_factor) = self.get_reduction_factor(
				self.layer, self.field_name)

			for feature in self.layer.getFeatures():
				if self.exit_code > 0:
					break

				old_geometry = feature.geometry()
				new_geometry = self.transform(meta_features,
					force_reduction_factor, old_geometry)

				self.layer.dataProvider().changeGeometryValues({
					feature.id() : new_geometry})

				steps += 1
				if step == 0 or steps % step == 0:
					self.progress.emit(steps / float(feature_count) * 100)

		if self.exit_code == -1:
			self.progress.emit(100)
			ret = self.layer
		self.finished.emit(ret, self.exit_code)

	def kill(self):
		self.exit_code = 1

	def get_reduction_factor(self, layer, field):
		"""Calculate the reduction factor."""
		data_provider = layer.dataProvider()
		meta_features = []

		total_area = 0.0
		total_value = 0.0

		if self.min_value is None:
			self.min_value = self.get_min_value(data_provider, field)

		for feature in data_provider.getFeatures():
			meta_feature = CartogramFeature()

			geometry = QgsGeometry(feature.geometry())

			area = QgsDistanceArea().measureArea(geometry)
			total_area += area

			feature_value = feature.attribute(field)
			if type(feature_value) is None or feature_value == 0:
				feature_value = self.min_value / 100

			total_value += feature_value

			meta_feature.area = area
			meta_feature.value = feature_value

			centroid = geometry.centroid()
			(cx, cy) = centroid.asPoint().x(), centroid.asPoint().y()
			meta_feature.center_x = cx
			meta_feature.center_y = cy

			meta_features.append(meta_feature)

		fraction = total_area / total_value

		total_size_error = 0

		for meta_feature in meta_features:
			polygon_value = meta_feature.value
			polygon_area = meta_feature.area

			if polygon_area < 0:
				polygon_area = 0

			# this is our 'desired' area...
			desired_area = polygon_value * fraction

			# calculate radius, a zero area is zero radius
			radius = math.sqrt(polygon_area / math.pi)
			meta_feature.radius = radius

			if desired_area / math.pi > 0:
				mass = math.sqrt(desired_area / math.pi) - radius
				meta_feature.mass = mass
			else:
				meta_feature.mass = 0

			size_error = max(polygon_area, desired_area) / \
				min(polygon_area, desired_area)

			total_size_error += size_error

		average_error = total_size_error / len(meta_features)
		force_reduction_factor = 1 / (average_error + 1)

		return (meta_features, force_reduction_factor)

	def transform(self, meta_features, force_reduction_factor, geometry):
		"""Transform the geometry based on the force reduction factor."""

		if geometry.isMultipart():
			geometries = []
			for polygon in geometry.asMultiPolygon():
				new_polygon = self.transform_polygon(polygon, meta_features,
					force_reduction_factor)
				geometries.append(new_polygon)
			return QgsGeometry.fromMultiPolygonXY(geometries)
		else:
			polygon = geometry.asPolygon()
			new_polygon = self.transform_polygon(polygon, meta_features,
				force_reduction_factor)
			return QgsGeometry.fromPolygon(new_polygon)

	def transform_polygon(self, polygon, meta_features,
		force_reduction_factor):
		"""Transform the geometry of a single polygon."""

		new_line = []
		new_polygon = []

		for line in polygon:
			for point in line:
				x = x0 = point.x()
				y = y0 = point.y()
				# compute the influence of all shapes on this point
				for feature in meta_features:
					cx = feature.center_x
					cy = feature.center_y
					distance = math.sqrt((x0 - cx) ** 2 + (y0 - cy) ** 2)

					if (distance > feature.radius):
						# calculate the force exerted on points far away from
						# the centroid of this polygon
						force = feature.mass * feature.radius / distance
					else:
						# calculate the force exerted on points close to the
						# centroid of this polygon
						xF = distance / feature.radius
						# distance ** 2 / feature.radius ** 2 instead of xF
						force = feature.mass * (xF ** 2) * (4 - (3 * xF))
					force = force * force_reduction_factor / distance
					x = (x0 - cx) * force + x
					y = (y0 - cy) * force + y
				new_line.append(QgsPointXY(x, y))
			new_polygon.append(new_line)
			new_line = []
		#print new_polygon
		return new_polygon

	def get_step(self):
		"""Determine how often the progress bar should be updated."""

		feature_count = self.layer.featureCount()

		# update the progress bar at each .1% increment
		step = feature_count // 1000

		# because we use modulo to determine if we should emit the progress
		# signal, the step needs to be greater than 1
		if step < 2:
			step = 2

		return step

	def get_min_value(self, data_provider, field):
		features = []
		for feature in data_provider.getFeatures():
			feature_value = feature.attribute(field)
			if not type(feature_value) is None and feature_value != 0:
				features.append(feature.attribute(field))

		return min(features)

class Postprocessing():
	def __init__():
		pass

	def export2JSON(layer):
		currentDir = unicode(os.path.abspath( os.path.dirname(sys.argv[0])))
		geoJsonFile=os.path.join(currentDir,"cartogram")
		error = QgsVectorFileWriter.writeAsVectorFormat(layer, geoJsonFile, "utf-8", None, "GeoJSON")
		if error == QgsVectorFileWriter.NoError:
			print("success!", os.path.dirname(sys.argv[0]))


