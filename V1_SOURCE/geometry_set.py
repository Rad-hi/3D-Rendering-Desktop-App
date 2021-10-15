#!/usr/bin/env python3

####################
### Dependencies ###
####################

import math
import gc
import numpy as np

########################
### Global variables ###
########################

LINE_COLOR = "#0000FF"
POINT_SIZE = 2
POINT_COLOR = '#000000'

CANVAS_WIDTH = 840
CANVAS_HEIGHT = 560

OBJECT_POSITION = [CANVAS_WIDTH//2, CANVAS_HEIGHT-20]
OBJECT_SCALE = 2500


def UpdatePosition(x, y):
    global OBJECT_POSITION

    OBJECT_POSITION[0] += x
    OBJECT_POSITION[1] += y


def DrawLine (i, j, points, canvas):
    point_01 = points[i]
    point_02 = points[j]
    canvas.create_line(point_01[0], point_01[1],
                       point_02[0], point_02[1],
                       fill = LINE_COLOR)
    return canvas

def DrawPoint(point, canvas):
    canvas.create_oval(point[0], point[1],
                       point[0], point[1],
                       width = POINT_SIZE,
                       fill = POINT_COLOR)
    return canvas

def DrawTriangle(face, canvas, points):
  points = [points[face[0]], 
            points[face[1]], 
            points[face[2]]]
  for point in points:
    canvas = DrawPoint(point, canvas)
  canvas.create_polygon(points, outline = LINE_COLOR, fill = "")

  return canvas

def TransformPoint(point, rotation_x, rotation_y, rotation_z, zoom):

    #Here we rotate our point in the Y, X, and Z axis respectively
    rotated_2d = np.matmul(rotation_y, point)
    rotated_2d = np.matmul(rotation_x, rotated_2d)
    rotated_2d = np.matmul(rotation_z, rotated_2d)

    #Projection matricies are also a tool in linear algebra that allow us
    #to project "3D" objects on 2D screens and still precieve them as "3D"
    z = 1/(zoom - rotated_2d[2][0])
    projection_matrix = [[z, 0, 0],
                        [0, z, 0]]
    projected_2d = np.matmul(projection_matrix, rotated_2d)
    x = int(projected_2d[0][0] * OBJECT_SCALE) + OBJECT_POSITION[0]
    #The (-) sign in the Y is because the canvas' Y axis starts
    #from Top to Bottom, so without the (-) sign, our objects
    #would be presented upside down
    y = -int(projected_2d[1][0] * OBJECT_SCALE) + OBJECT_POSITION[1]

    return x, y

def CalculateMatrix(angle_x, angle_y, angle_z):

  #These are the rotation matricies that will transform the point position
  #according to the desired rotation (Check some linear algebra course
  #if you wanna know more about em, otherwise, there's no huge need
  #to understand exactly how they work)
  rotation_x = [[1, 0, 0],
                [0, math.cos(angle_x), -math.sin(angle_x)],
                [0, math.sin(angle_x), math.cos(angle_x)]]

  rotation_y = [[math.cos(angle_y), 0, -math.sin(angle_y)],
                [0, 1, 0],
                [math.sin(angle_y), 0, math.cos(angle_y)]]

  rotation_z = [[math.cos(angle_z), -math.sin(angle_z), 0],
                [math.sin(angle_z), math.cos(angle_z), 0],
                [0, 0 ,1]]
  return rotation_x, rotation_y, rotation_z

#This function is the one that orchestrates all the actions.
#First is transforms the points, draws them, then draws the lines
#according to the faces list
def DrawObject(canvas, Verticies, Faces, angle_x, angle_y, angle_z, zoom):
    projected_points = {}
    rot_x, rot_y, rot_z = CalculateMatrix(angle_x, angle_y, angle_z)
    for vertex in Verticies.items():
      x, y = TransformPoint(vertex[1],
                            rot_x,
                            rot_y,
                            rot_z,
                            zoom)
      projected_points[vertex[0]] = [x, y]

    #Faces could be presented with more than 3 verticies, but for now,
    #we're only drawing triangles and ignoring the rest
    for face in Faces:
      canvas = DrawTriangle(face, canvas, projected_points)
    return canvas

if __name__ == '__main__':
    print("""This is not the executable file,
             go to the 'main.py' file and run
             it instead!""")
