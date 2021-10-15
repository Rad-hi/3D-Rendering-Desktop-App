import obj_files_handler
import geometry

import math

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import pyscreenshot as ImageGrab

class GUI(tk.Tk):

	BACKGROUND_COLOR = '#131313'
	CANVAS_WIDTH 	 = 840
	CANVAS_HEIGHT	 = 560
	CANVAS_COLOR 	 = 'white'
	COMMON_X 		 = 0.97	# Many graphical elements share the same relative X position
	MOVING_STEP		 = 10


	def __init__(self, title = '3D_Viz', min_size = (1165, 630)):
		super().__init__()
		self.file_exists = False
		self.changed = True # A flag used to only redraw the object when a change occured
		self._initialise_window(title, min_size)
		self._create_canvas()
		self._create_widgets()
		self._geometry_handler = geometry.GEOMETRY(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
		self._reset_rotation()

	def _initialise_window(self, title, min_size):
		self.title(title)
		self.minsize(*min_size)
		self['bg'] = self.BACKGROUND_COLOR

	def _create_canvas(self):
		self.canvas = tk.Canvas(self, width  = self.CANVAS_WIDTH,
		                 			  height = self.CANVAS_HEIGHT,
		                 			  bg 	 = self.CANVAS_COLOR)
		self.canvas.place(relx = 0.03, rely = 0.052)

	def _create_widgets(self):
		self._create_zoom_slider()
		self._create_x_rot_slider()
		self._create_y_rot_slider()
		self._create_z_rot_slider()
		self._create_reset_rot_button()
		self._create_import_file_button()
		self._create_screenshot_button()
		self._create_up_down_left_right_buttons()

	def _create_zoom_slider(self):
		ttk.Label(self, text = "Zoom:", foreground = "#ffffff", background = "#131113")\
		   .place(relx = self.COMMON_X, rely = 0.052, relheight = 0.035, relwidth = 0.2, anchor = "ne")

		self.zoom_slider = ttk.Scale(self, from_ = 500, to = 1, orient = "horizontal", command = self._changed)
		self.zoom_slider.set(22)
		self.zoom_slider.place(relx = self.COMMON_X, rely = 0.088, relheight = 0.04, relwidth = 0.2, anchor = "ne")

		# Add a separator for visual purposes
		ttk.Separator(self, orient = "horizontal")\
		   .place(relx = self.COMMON_X, rely = 0.160, relwidth = 0.2, anchor = "ne")
		
	def _create_x_rot_slider(self):
		ttk.Label(self, text = "X Rotation:", foreground = "#ffffff", background = "#131113")\
		   .place(relx = self.COMMON_X, rely = 0.184, relheight = 0.035, relwidth = 0.2, anchor = "ne")
		
		self.x_rotation_slider = ttk.Scale(self, from_ = -0.05, to = 0.05, orient = "horizontal", command = self._changed)
		self.x_rotation_slider.set(0)
		self.x_rotation_slider.place(relx = self.COMMON_X, rely = 0.220, relheight = 0.04, relwidth = 0.2, anchor = "ne")

	def _create_y_rot_slider(self):
		ttk.Label(self, text = "Y Rotation:", foreground = "#ffffff", background = "#131113")\
		   .place(relx = self.COMMON_X, rely = 0.294, relheight = 0.035, relwidth = 0.2, anchor = "ne")
		
		self.y_rotation_slider = ttk.Scale(self, from_ = -0.05, to = 0.05, orient = "horizontal", command = self._changed)
		self.y_rotation_slider.set(0)
		self.y_rotation_slider.place(relx = self.COMMON_X, rely = 0.330, relheight = 0.04, relwidth = 0.2, anchor = "ne")

	def _create_z_rot_slider(self):
		ttk.Label(self, text = "Z Rotation:", foreground = "#ffffff", background = "#131113")\
		   .place(relx = self.COMMON_X, rely = 0.394, relheight = 0.035, relwidth = 0.2, anchor = "ne")
		
		self.z_rotation_slider = ttk.Scale(self, from_ = -0.05, to = 0.05, orient = "horizontal", command = self._changed)
		self.z_rotation_slider.set(0)
		self.z_rotation_slider.place(relx = self.COMMON_X, rely = 0.430, relheight = 0.04, relwidth = 0.2, anchor = "ne")

		
	def _create_reset_rot_button(self):
		ttk.Button(self, text = "Reset rotation", command = self._reset_rotation)\
		   .place(relx = self.COMMON_X, rely = 0.505, relheight = 0.05, relwidth = 0.095, anchor = "ne")
	
	def _create_import_file_button(self):
		ttk.Button(self, text = "Take a screenshot", command = self._take_screenshot)\
		   .place(relx = self.COMMON_X, rely = 0.895, relheight = 0.05, relwidth = 0.2, anchor = "ne")
	
	def _create_screenshot_button(self):
		self.FILE_NAME = tk.StringVar()
		ttk.Label(self, textvariable = self.FILE_NAME, foreground = "#ffffff", background = "#131113")\
		   .place(relx = 0.86, rely = 0.817, relheight = 0.035, relwidth = 0.09, anchor="ne")
		
		ttk.Button(self, text = "Import file", command = self._read_file)\
		   .place(relx = self.COMMON_X, rely = 0.815, relheight = 0.05, relwidth = 0.095, anchor="ne")
	
	def _create_up_down_left_right_buttons(self):
		# Common values for placements of the buttons
		COMM_X = 0.89
		COMM_Y = 0.660
		COMM_RELATIVE_HIEGHT = 0.05
		COMM_RELATIVE_WIDTH  = 0.03
		COMM_ANCHOR_NE = "ne"

		ttk.Button(self, text = "U", command = self._move_up)\
		   .place(relx = COMM_X, rely = 0.595, relheight = COMM_RELATIVE_HIEGHT,
		   		  relwidth = COMM_RELATIVE_WIDTH, anchor = COMM_ANCHOR_NE)

		ttk.Button(self, text = "D", command = self._move_down)\
		   .place(relx = COMM_X, rely = 0.725, relheight = COMM_RELATIVE_HIEGHT,
		   		  relwidth = COMM_RELATIVE_WIDTH, anchor = COMM_ANCHOR_NE)

		ttk.Button(self, text = "L", command = self._move_left)\
		   .place(relx = 0.84, rely = COMM_Y, relheight = COMM_RELATIVE_HIEGHT,
		   		  relwidth = COMM_RELATIVE_WIDTH, anchor = COMM_ANCHOR_NE)

		ttk.Button(self, text = "R", command = self._move_right)\
		   .place(relx = 0.94, rely = COMM_Y, relheight = COMM_RELATIVE_HIEGHT,
		   		  relwidth = COMM_RELATIVE_WIDTH, anchor = COMM_ANCHOR_NE)

	def _changed(self, *args):
		self.changed = True

	def _reset_rotation(self):
		self._geometry_handler.reset_rotation()
		self.x_rotation_slider.set(0)
		self.y_rotation_slider.set(0)
		self.z_rotation_slider.set(0)
		self._changed()

	def _take_screenshot(self):
		#Grab the top-left corner's coordinates
		x = self.winfo_rootx() + self.canvas.winfo_x()
		y = self.winfo_rooty() + self.canvas.winfo_y()

		#Grab the bottom-right corner's coordinates
		x1 = x + self.canvas.winfo_width()
		y1 = y + self.canvas.winfo_height()

		#Crop the screenshot to the determined coordinates
		screenshot = ImageGrab.grab().crop((x, y, x1, y1))
		SAVE_PATH = filedialog.asksaveasfilename(defaultextension = ".png",
												 filetypes = (("PNG Files", "*.png"),
												 ("All Files", "*.*")))
		
		#Check if they actually saved and didn't exit before saving
		if SAVE_PATH:
			screenshot.save(SAVE_PATH)

	def _read_file(self):
		messagebox.showinfo(message = 'Only .obj files are compatible!', title = "WARNING")
		
		file_path = filedialog.askopenfilename(defaultextension = ".obj",
											   filetypes = (("OBJ Files", "*.obj"),
											   ("All Files", "*.*")))
		
		if len(file_path) and file_path[-4:] != ".obj":
			messagebox.showinfo(message = "Incompatible file format", title = "ERROR")

		elif len(file_path):
			self.FILE_NAME.set(file_path.split('/')[-1])
			self._reset_rotation()
			with open(file_path) as file:
				self._geometry_handler._verticies, self._geometry_handler._faces = obj_files_handler.extract_data(file)
				self.file_exists = True
				pass

	def _move_up(self):
		self._geometry_handler.update_position(0, -1 * self.MOVING_STEP)
		self._changed()
	
	def _move_down(self):
		self._geometry_handler.update_position(0, self.MOVING_STEP)
		self._changed()
	
	def _move_left(self):
		self._geometry_handler.update_position(-1 * self.MOVING_STEP, 0)
		self._changed()
	
	def _move_right(self):
		self._geometry_handler.update_position(self.MOVING_STEP, 0)
		self._changed()

	def draw(self):
		self._get_rotations()
		self._get_zoom()
		if(self.file_exists and self.changed):
			#Delete all the previous points and lines in order to draw new ones
			self.canvas.delete("all")
			
			self.canvas = self._geometry_handler.draw_object(self.canvas)
			self.changed = False

	def _get_zoom(self):
		self._geometry_handler._zoom = self.zoom_slider.get() #math.exp(self.zoom_slider.get())

	def _get_rotations(self):
		self._geometry_handler._angle_x = self.x_rotation_slider.get()
		self._geometry_handler._angle_y = self.y_rotation_slider.get()
		self._geometry_handler._angle_z = self.z_rotation_slider.get()