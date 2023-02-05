from timer import time_me
import math
import numpy as np
import numba

@numba.njit(nogil=True, cache=True, fastmath=True)
def matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray:
	'''
	@brief: Matrix multiplication from scratch
	@param A: First matrix 
	@param B: Second matrix
	@Note: A, and B must be multiplicable matrices; that must have a common dimension
	@return C: Product of A and B
	'''
	rows, cols = A.shape[0], B.shape[1]
	C = np.zeros((rows, cols))
	for i in range(rows):
		for j in range(cols):
			for k in range(rows):
				C[i, j] += A[i, k] * B[k, j]
	return C

@numba.njit(nogil=True, cache=True)
def max_3d_array(arr: np.ndarray, axis: int) -> float:
	'''
	Find the maximum in a miltidimensional array, in the provided axis
	'''
	max_ = -np.inf
	for i in arr:
		if i[axis] >= max_: 
			max_ = i[axis] 
	return max_

@numba.njit(nogil=True, cache=True)
def min_3d_array(arr: np.ndarray, axis: int) -> float:
	'''
	Find the minimum in a miltidimensional array, in the provided axis
	'''
	min_ = np.inf
	for i in arr:
		if i[axis] <= min_: 
			min_ = i[axis] 
	return min_

class Geometry:
	'''
	Geometry handling class (linear algebra)
	'''
	OBJECT_SCALE = 2000 # Maybe make this dynamic depending on the object size
	
	def __init__(self, canvas_width: int, canvas_height: int) -> None:
		'''
		'''
		self._obj_position = np.array((canvas_width//2, canvas_height//2))
		self._zoom = 50.0
		self._angle_x = 0.0
		self._angle_y = 0.0
		self._angle_z = 0.0
		self._faces = None
		self._verticies = None

	def upload_object(self, verts: np.ndarray, faces: list) -> None:
		'''Uploads the verticies and faces to manipulate'''
		self._verticies = self.__normalize_3d_array(verts, axis=0)
		self._faces = faces

	def update_position(self, x: int, y: int) -> None:
		'''Update x, y position of the object'''
		self._obj_position[0] += x
		self._obj_position[1] += y
	
	@time_me
	def transform_object(self) -> 'list(list(int, int))':
		'''Retur the points of the object transformed according to the current pose'''
		rot_x, rot_y, rot_z = self.__calculate_rot_matrix()
		projected_points = []
		for pt in self._verticies:
			x, y = self.__transform_point(pt, rot_x, rot_y, rot_z, self._zoom, self._obj_position, self.OBJECT_SCALE)
			projected_points.append([x, y])
		return projected_points

	@property
	def faces(self) -> list:
		'''Get the faces formed between the points'''
		return self._faces

	@property
	def zoom(self) -> int:
		'''Get the current zoom value'''
		return self._zoom

	@property
	def orientation(self) -> 'tuple(float, float, float)':
		'''Returns the object's current angles'''
		return self._angle_x, self._angle_y, self._angle_z

	def set_zoom(self, zoom: float) -> None:
		'''Set the new zoom value'''
		self._zoom = zoom

	def step_rotation(self, 
					  x: float = 0.0,
					  y: float = 0.0,
					  z: float = 0.0
	) -> None:
		'''Increment the orientation of the object on its axis'''
		self._angle_x += x
		self._angle_y += y
		self._angle_z += z

	def reset_rotation(self, 
					   x: float = None,
					   y: float = None,
					   z: float = None
	) -> None:
		'''Reset the rotation to a specific position, if provided, else to 0'''
		self._angle_x = 0 if x is None else x
		self._angle_y = 0 if y is None else y
		self._angle_z = 0 if z is None else z

	@staticmethod
	@numba.njit(nogil=True, cache=True, fastmath=True)
	def __normalize_3d_array(arr: np.ndarray, 
							 range: 'tuple(float, float)' = (-1, 1),
							 axis: int = 2
	) -> np.ndarray:
		'''
		@brief: Normalize an array values within a range based on a specified axis
		@param arr: The array to be normalized
		@param range: Normalized values range (min, max)
		@param axis: the axis to normalize based on
		@return arr: The normalized array
		'''
		mnx = min_3d_array(arr, 0)
		mxx = max_3d_array(arr, 0)
		mnz = min_3d_array(arr, 2)
		mxz = max_3d_array(arr, 2)
		mny = min_3d_array(arr, 1)
		mxy = max_3d_array(arr, 1)

		if axis == 0:
			diff = mxx - mnx
		elif axis == 1:
			diff = mxy - mny
		else:
			diff = mxz - mnz
		
		for pt in arr:
			pt[0] = (((pt[0]-mnx)*(range[1]-range[0]))/diff) + range[0]
			pt[1] = (((pt[1]-mny)*(range[1]-range[0]))/diff) + range[0]
			pt[2] = (((pt[2]-mnz)*(range[1]-range[0]))/diff) + range[0]	
		return arr

	@staticmethod
	@numba.njit(nogil=True, cache=True, fastmath=True)
	def __transform_point(point: np.ndarray, 
						  rotation_x: np.ndarray, 
						  rotation_y: np.ndarray, 
						  rotation_z: np.ndarray,
						  zoom: float,
						  obj_position: 'list[int, int]',
						  obj_scale: int
	) -> 'tuple(int, int)':
		'''
		@brief: Rotate the point in 3axis according to the provided rotation matrices
		@param point: 3D point
		@param rotation_x: Rotation matrix on X axis
		@param rotation_y: Rotation matrix on Y axis
		@param rotation_z: Rotation matrix on Z axis
		@param zoom: Zoom value
		@param obj_position: Object position within the screen
		@param obj_scale: Object scale
		@return transformed point: 2D tranformed projection of the 3D point
		'''
		# Rotate point on the Y, X, and Z axis respectively
		rotated_2d = matmul(rotation_y, point.reshape((3, 1)))
		rotated_2d = matmul(rotation_x, rotated_2d)
		rotated_2d = matmul(rotation_z, rotated_2d)

		# Project 3D point on 2D plane
		z = 0.5 / (zoom - rotated_2d[2][0])
		projection_matrix = np.array(((z, 0, 0), (0, z, 0)))
		projected_2d = matmul(projection_matrix, rotated_2d)

		x = int(projected_2d[0][0]*obj_scale) + obj_position[0]
		# The (-) sign in the Y is because the canvas' Y axis starts from Top to Bottom, 
		# so without the (-) sign, our objects would be presented upside down
		y = -int(projected_2d[1][0]*obj_scale) + obj_position[1]

		return x, y

	def __calculate_rot_matrix(self) -> 'tuple(np.array, np.array, np.array)':
		'''
		Calculate the rotation matrices on X, Y, and Z axis 
		that correspond to the current requested rotation
		'''
		rotation_x = np.array(
			(
				(1,               0        ,               0         ),
				(0, math.cos(self._angle_x), -math.sin(self._angle_x)),
				(0, math.sin(self._angle_x),  math.cos(self._angle_x))
			)
		)

		rotation_y = np.array(
			(
				(math.cos(self._angle_y), 0, -math.sin(self._angle_y)),
				(            0          , 1,             0           ),
		        (math.sin(self._angle_y), 0,  math.cos(self._angle_y))
			)
		)

		rotation_z = np.array(
			(
				(math.cos(self._angle_z), -math.sin(self._angle_z), 0),
				(math.sin(self._angle_z),  math.cos(self._angle_z), 0),
			 	(           0           ,              0          , 1)
			)
		)
		return rotation_x, rotation_y, rotation_z


if __name__ == '__main__':
    print("This is not the executable file, go to the 'main.py' file and run it instead!")