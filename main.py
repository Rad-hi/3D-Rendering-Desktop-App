#! /usr/bin/env python3

#################
### Main file ###
#################
"""
This file imports from two other files, so make sure they're in the same
directory.
"""
####################
### Dependencies ###
####################

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import gc

from PIL import Image
import pyscreenshot as ImageGrab

import geometry_set
import obj_files_handler

########################
### Global variables ###
########################

APP_WIDTH = 1165 #minimal width of the GUI
APP_HEIGHT = 630 #minimal height of the gui

CANVAS_WIDTH = geometry_set.CANVAS_WIDTH #width of the visualizing area
CANVAS_HEIGHT = geometry_set.CANVAS_HEIGHT
CANVAS_COLOR = "white"

MOVING_STEP = 10
zoom = 20
angle_x = 0.0
angle_y = 0.0
angle_z = 0.0

#This dict will store the verticies along with their order in the .obj file
#since we'll need the order when drawing the faces
Verticies = {}

#This list will be populated with the lists of indexes of the verticies that
#shall be connected to form a face (Face[[v1, v65, v2], [], ...)
Faces = []

def ReadFile():
	global Verticies
	global Faces

	#Graphical window warns about the kind of compatible files
	messagebox.showinfo(message = 'Only .obj files are compatible!',
						title = "WARNING")
	#Graphical window that retreives the path of the file
	file_path = filedialog.askopenfilename(defaultextension = ".obj",
										   filetypes = (("OBJ Files", "*.obj"),
										   ("All Files", "*.*")))
	#Check if the extension of the file chosen is .obj
	if file_path[-4:] != ".obj" and len(file_path):
		messagebox.showinfo(message = "Incompatible file format",
							title = "ERROR")

	elif len(file_path):
		FILE_NAME.set(file_path.split('/')[-1])
		ResetRotation()
		with open(file_path) as file:
			Verticies, Faces = obj_files_handler.ExtractData(file)

def MoveUp(*args):
	geometry_set.UpdatePosition(0, -1*MOVING_STEP)

def MoveDown(*args):
	geometry_set.UpdatePosition(0, MOVING_STEP)

def MoveLeft(*args):
	geometry_set.UpdatePosition(-1*MOVING_STEP, 0)

def MoveRight(*args):
	geometry_set.UpdatePosition(MOVING_STEP, 0)

def ResetRotation():
    global angle_x
    global angle_y
    global angle_z
    angle_x = 0.0
    angle_y = 0.0
    angle_z = 0.0
    x_rotation_slider.set(angle_x)
    y_rotation_slider.set(angle_y)
    z_rotation_slider.set(angle_z)

def TakeScreenshot():
	#Grab the top-left corner's coordinates
	x=root.winfo_rootx()+canvas.winfo_x()
	y=root.winfo_rooty()+canvas.winfo_y()

	#Grab the bottom-right corner's coordinates
	x1=x+canvas.winfo_width()
	y1=y+canvas.winfo_height()

	#Crop the screenshot to the determined coordinates
	IM = ImageGrab.grab().crop((x,y,x1,y1))
	SAVE_PATH = filedialog.asksaveasfilename(defaultextension = ".png",
											 filetypes = (("PNG Files", "*.png"),
											 ("All Files", "*.*")))
	#Check if they actually saved and didn't exit before saving
	if SAVE_PATH:
		IM.save(SAVE_PATH)

#This function will loop infinitely
def Update():
	global zoom
	global angle_x
	global angle_y
	global angle_z
	global canvas

	# Update the orientation of the object
	angle_x += x_rotation_slider.get()
	angle_y += y_rotation_slider.get()
	angle_z += z_rotation_slider.get()
	zoom = zoom_slider.get()

	#Delete all the previous points and lines in order to draw new ones
	canvas.delete("all")
	canvas = geometry_set.DrawObject(canvas,
									 Verticies,
									 Faces,
									 angle_x,
									 angle_y,
									 angle_z,
									 zoom)

	#This line calls the Update function every 2 milliseconds
	#If you want to control the FPS, you can change the value there with:
	#round(1000/FPS), and give FPS a value like 30
	root.after(2, Update)

######################
### Main show-room ###
######################

root = tk.Tk()
root.title("3D-Viz")
root.minsize(APP_WIDTH, APP_HEIGHT)
root["bg"] = "#131113"

###############################
### Drawing board's section ###
###############################

canvas = tk.Canvas(root, width = CANVAS_WIDTH,
                         height = CANVAS_HEIGHT,
                         bg = CANVAS_COLOR)

#X and Y start at the Top-Left corner (X == Y == 0)
#At the Bottom-Right corner, relx == rely == 1 (relative-X, relative-Y)
#You can use pack(), or grid() if you don't feel comfortable working with
#relative placing
canvas.place(relx = 0.03, rely = 0.052)

##############################
### Zoom elements' section ###
##############################

zoom_label = ttk.Label(root, text = "Zoom:",
                             foreground = "#ffffff",
                             background = "#131113")
zoom_label.place(relx = 0.97,
                 rely = 0.052,
                 relheight = 0.035,
                 relwidth = 0.2,
                 anchor="ne")
zoom_slider = ttk.Scale(root, from_ = 500,
                              to = 1,
                              orient = "horizontal")
zoom_slider.set(zoom)
zoom_slider.place(relx = 0.97,
                  rely = 0.088,
                  relheight = 0.04,
                  relwidth = 0.2,
                  anchor="ne")

##########################################################
### Separating line between zoom and rotation elements ###
##########################################################

zoom_rot_seperator = ttk.Separator(root,
								   orient = "horizontal")
zoom_rot_seperator.place(relx = 0.97,
                         rely = 0.160,
                         relwidth = 0.2,
                         anchor = "ne")

############################################
### Rotation elements in the GUI section ###
############################################

##################
### X Rotation ###
##################

x_rotation_label = ttk.Label(root, text = "X Rotation:",
                                   foreground = "#ffffff",
                                   background = "#131113")
x_rotation_label.place(relx = 0.97,
                       rely = 0.184,
                       relheight = 0.035,
                       relwidth = 0.2,
                       anchor="ne")
x_rotation_slider = ttk.Scale(root, from_ = -0.05,
                                    to = 0.05,
                                    orient = "horizontal")
x_rotation_slider.set(angle_x)
x_rotation_slider.place(relx = 0.97,
                        rely = 0.220,
                        relheight = 0.04,
                        relwidth = 0.2,
                        anchor = "ne")

##################
### Y Rotation ###
##################

y_rotation_label = ttk.Label(root, text = "Y Rotation:",
                                   foreground = "#ffffff",
                                   background = "#131113")
y_rotation_label.place(relx = 0.97,
                       rely = 0.294,
                       relheight = 0.035,
                       relwidth = 0.2,
                       anchor = "ne")
y_rotation_slider = ttk.Scale(root, from_ = -0.05,
                                    to = 0.05,
                                    orient = "horizontal")
y_rotation_slider.set(angle_y)
y_rotation_slider.place(relx = 0.97,
                        rely = 0.330,
                        relheight = 0.04,
                        relwidth = 0.2,
                        anchor = "ne")

##################
### Z Rotation ###
##################

z_rotation_label = ttk.Label(root, text = "Z Rotation:",
                                   foreground = "#ffffff",
                                   background = "#131113")
z_rotation_label.place(relx = 0.97,
                       rely = 0.394,
                       relheight = 0.035,
                       relwidth = 0.2,
                       anchor = "ne")
z_rotation_slider = ttk.Scale(root, from_ = -0.05,
                                    to = 0.05,
                                    orient = "horizontal")
z_rotation_slider.set(angle_z)
z_rotation_slider.place(relx = 0.97,
                        rely = 0.430,
                        relheight = 0.04,
                        relwidth = 0.2,
                        anchor = "ne")

######################
### RESET Rotation ###
######################

reset_rotation_button = ttk.Button(root,
                               text = "Reset rotation",
                               command = ResetRotation)
reset_rotation_button.place(relx = 0.97,
                        rely = 0.505,
                        relheight = 0.05,
                        relwidth = 0.095,
                        anchor = "ne")
reset_rotation_button.bind(ResetRotation)

#################################
### screenshot button section ###
#################################

screenshot_button = ttk.Button(root,
							   text = "Take a screenshot",
							   command = TakeScreenshot)
screenshot_button.place(relx = 0.97,
                        rely = 0.895,
                        relheight = 0.05,
                        relwidth = 0.2,
                        anchor = "ne")
screenshot_button.bind(TakeScreenshot)

##################################
### Import file button section ###
##################################

FILE_NAME = tk.StringVar()
import_file_label = ttk.Label(root, textvariable = FILE_NAME,
                                    foreground = "#ffffff",
                                    background = "#131113")
import_file_label.place(relx = 0.88,
                        rely = 0.817,
                        relheight = 0.035,
                        relwidth = 0.09,
                        anchor="ne")
import_file_button = ttk.Button(root,
						   	    text = "Import file",
						   	    command = ReadFile)
import_file_button.place(relx = 0.97,
                    	 rely = 0.815,
                    	 relheight = 0.05,
                    	 relwidth = 0.095,
                    	 anchor="ne")
import_file_button.bind(ReadFile)

#############################################
### UP, DOWN, LEFT, RIGHT buttons section ###
#############################################

##########
### UP ###
##########

up_button = ttk.Button(root,
					   text = "U",
					   command = MoveUp)
up_button.place(relx = 0.89,
            	rely = 0.595,
            	relheight = 0.05,
            	relwidth = 0.03,
            	anchor = "ne")
up_button.bind('<Up>', MoveUp)
root.bind('<Up>', MoveUp)

############
### DOWN ###
############

down_button = ttk.Button(root,
						 text = "D",
						 command = MoveDown)
down_button.place(relx = 0.89,
                  rely = 0.725,
                  relheight = 0.05,
                  relwidth = 0.03,
                  anchor = "ne")
down_button.bind('<Down>', MoveDown)
root.bind('<Down>', MoveDown)

############
### LEFT ###
############

left_button = ttk.Button(root,
						 text = "L",
						 command = MoveLeft)
left_button.place(relx = 0.84,
 				  rely = 0.660,
 				  relheight = 0.05,
 				  relwidth = 0.03,
 				  anchor = "ne")
left_button.bind('<Left>', MoveLeft)
root.bind('<Left>', MoveLeft)

#############
### RIGHT ###
#############

right_button = ttk.Button(root,
						  text = "R",
						  command = MoveRight)
right_button.place(relx = 0.94,
                  rely = 0.660,
                  relheight = 0.05,
                  relwidth = 0.03,
                  anchor = "ne")
right_button.bind('<Right>', MoveRight)
root.bind('<Right>', MoveRight)

#############################
### Main function section ###
#############################

if __name__ == '__main__':
    Update()

###############
root.mainloop()
gc.collect()
