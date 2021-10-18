import math
import numpy as np

class GEOMETRY:

	def __init__(self, canvas_width, canvas_height):
		self.CANVAS_WIDTH    = canvas_width
		self.CANVAS_HEIGHT   = canvas_height
		self.OBJECT_POSITION = [canvas_width // 2, canvas_height - 20]
		self.OBJECT_SCALE    = 2500
		self._angle_x        = 0
		self._angle_y        = 0
		self._angle_z        = 0
		self._zoom 	         = 20
		self._faces 	     = []
		self._verticies      = {}
		self.FILL 			 = ""
		self.POINT_COLOR	 = "#000000"
		self.LINE_COLOR	     = "#0000FF"

	def change_fill_color(self, color, no_fill = False):
		if(no_fill):
			self.FILL = ""
		else:
			self.FILL = color

	def change_line_color(self, color):
		self.LINE_COLOR = color

	def update_position(self, x, y):
		self.OBJECT_POSITION[0] += x
		self.OBJECT_POSITION[1] += y

	def draw_object(self, canvas):
		projected_points = {}

		rot_x, rot_y, rot_z = self._calculate_rot_matrix()
		for vertex in self._verticies.items():
			x, y = self._transform_point(vertex[1], rot_x, rot_y, rot_z)
			projected_points[vertex[0]] = [x, y]

		return self._draw_face(canvas, projected_points)

	def _draw_face(self, canvas, points):
		for face in self._faces:
			to_draw = [points[face[i]] for i in range(len(face))]
			for point in to_draw:
				if(point[0] < 0 or
				   point[1] < 0 or
				   point[0] > self.CANVAS_WIDTH or
				   point[1] > self.CANVAS_HEIGHT):
					continue # Don't draw points that are out of the screen

				canvas = self._draw_point(point, canvas)

			canvas.create_polygon(to_draw, outline = self.LINE_COLOR, fill = self.FILL)
		return canvas

	def _draw_point(self, point, canvas):
		POINT_SIZE = 2
		canvas.create_oval(point[0], point[1],
						   point[0], point[1],
						   width = POINT_SIZE,
						   fill  = self.POINT_COLOR)
		return canvas

	def reset_rotation(self):
		self._angle_x = 0
		self._angle_y = 0
		self._angle_z = 0

	def _transform_point(self, point, rotation_x, rotation_y, rotation_z):
		# Here we rotate our point in the Y, X, and Z axis respectively
		rotated_2d = np.matmul(rotation_y, point)
		rotated_2d = np.matmul(rotation_x, rotated_2d)
		rotated_2d = np.matmul(rotation_z, rotated_2d)

		# Projection matricies are also a tool in linear algebra that allow us
		# to project "3D" objects on 2D screens and still precieve them as "3D"
		z = 0.5 / (self._zoom - rotated_2d[2][0])
		projection_matrix = [[z, 0, 0],
							 [0, z, 0]]
		projected_2d = np.matmul(projection_matrix, rotated_2d)

		x = int(projected_2d[0][0] * self.OBJECT_SCALE) + self.OBJECT_POSITION[0]

		# The (-) sign in the Y is because the canvas' Y axis starts
		# from Top to Bottom, so without the (-) sign, our objects
		# would be presented upside down
		y = -int(projected_2d[1][0] * self.OBJECT_SCALE) + self.OBJECT_POSITION[1]

		return x, y

	def _calculate_rot_matrix(self):
		# These are the rotation matricies that will transform the point position
		# according to the desired rotation (Check some linear algebra course
		# if you wanna know more about them, otherwise, there's no huge need
		# to understand exactly how they work)
		rotation_x = [[1,               0        ,               0         ],
					  [0, math.cos(self._angle_x), -math.sin(self._angle_x)],
					  [0, math.sin(self._angle_x),  math.cos(self._angle_x)]]

		rotation_y = [[math.cos(self._angle_y), 0, -math.sin(self._angle_y)],
					  [            0          , 1,             0           ],
		              [math.sin(self._angle_y), 0,  math.cos(self._angle_y)]]

		rotation_z = [[math.cos(self._angle_z), -math.sin(self._angle_z), 0],
					  [math.sin(self._angle_z),  math.cos(self._angle_z), 0],
					  [           0           ,              0          , 1]]
		return rotation_x, rotation_y, rotation_z


if __name__ == '__main__':
    print("This is not the executable file, go to the 'main.py' file and run it instead!")