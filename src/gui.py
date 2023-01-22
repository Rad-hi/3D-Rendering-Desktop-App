import obj_files_handler as obj_files_handler 
from geometry import Geometry

import math
import tkinter as tk
from tkinter import ttk, filedialog, colorchooser, messagebox
import pyscreenshot as ImageGrab

class GUI(tk.Tk):
	''''''
	BACKGROUND_COLOR = '#131313'
	CANVAS_WIDTH = 840
	CANVAS_HEIGHT = 525
	CANVAS_COLOR = 'white'
	COMMON_X = 0.97	# Many graphical elements share the same relative X position
	MOVING_STEP = 10
	POINT_SIZE = 1 
	POINT_COLOR = '#131313'

	def __init__(self, title = '3D_Viz', min_size = (1165, 630)):
		''''''
		super().__init__()
		self._file_exists = False # A flag for whether the file has been loaded or not
		self._changed = True # A flag used to only redraw the object when a change occured
		self._geometry_handler = Geometry(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
		
		self._fill_color_holder = "#000000"
		self._line_color_holder = "#0000FF"

		self.__initialise_window(title, min_size)
		self.__create_widgets()
		self.__reset_rotation()

	def __initialise_window(self, title, min_size):
		self.title(title)
		self.minsize(*min_size)
		self['bg'] = self.BACKGROUND_COLOR

	def __create_widgets(self):
		self.__create_canvas()
		self.__create_zoom_slider()

		ttk.Separator(self, orient = "horizontal").place(
			relx=self.COMMON_X, 
			rely=0.160, 
			relwidth=0.2, 
			anchor="ne"
		)

		self.__create_x_rot_slider()
		self.__create_y_rot_slider()
		self.__create_z_rot_slider()
		self.__create_reset_rot_button()
		self.__create_import_file_button()
		self.__create_screenshot_button()
		self.__create_up_down_left_right_buttons()
		self.__create_color_pickers()
		self.__create_fill_check()

	def __create_canvas(self):
		self._canvas_color = tk.StringVar()
		self._canvas_color.set("#FFFFFF")
		self._canvas = tk.Canvas(self, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg=self._canvas_color.get())
		self._canvas.place(relx=0.03, rely=0.052)

	def __create_zoom_slider(self):
		ttk.Label(self, text="Zoom:", foreground="#ffffff", background="#131113").place(relx=self.COMMON_X, rely=0.052, relheight=0.035, relwidth=0.2, anchor="ne")
		self.zoom_slider = ttk.Scale(self, from_=0.1, to=1000, orient="horizontal", command=self.__changed)
		self.zoom_slider.set(self._geometry_handler.zoom)
		self.zoom_slider.place(relx=self.COMMON_X, rely=0.088, relheight=0.04, relwidth=0.2, anchor="ne")

	def __create_x_rot_slider(self):
		ttk.Label(self, text="X Rotation:", foreground="#ffffff", background="#131113").place(relx=self.COMMON_X, rely=0.184, relheight=0.035, relwidth=0.2, anchor="ne")
		self.x_rotation_slider = ttk.Scale(self, from_=-math.pi, to=math.pi, orient="horizontal", command=self.__changed)
		self.x_rotation_slider.set(0)
		self.x_rotation_slider.place(relx=self.COMMON_X, rely=0.220, relheight=0.04, relwidth=0.2, anchor="ne")

	def __create_y_rot_slider(self):
		ttk.Label(self, text="Y Rotation:", foreground="#ffffff", background="#131113").place(relx=self.COMMON_X, rely=0.294, relheight=0.035, relwidth=0.2, anchor="ne")
		self.y_rotation_slider = ttk.Scale(self, from_=-math.pi, to=math.pi, orient="horizontal", command=self.__changed)
		self.y_rotation_slider.set(0)
		self.y_rotation_slider.place(relx=self.COMMON_X, rely=0.330, relheight=0.04, relwidth=0.2, anchor="ne")

	def __create_z_rot_slider(self):
		ttk.Label(self, text="Z Rotation:", foreground="#ffffff", background="#131113").place(relx=self.COMMON_X, rely=0.394, relheight=0.035, relwidth=0.2, anchor="ne")
		self.z_rotation_slider = ttk.Scale(self, from_=-math.pi, to=math.pi, orient="horizontal", command=self.__changed)
		self.z_rotation_slider.set(0)
		self.z_rotation_slider.place(relx=self.COMMON_X, rely=0.430, relheight=0.04, relwidth=0.2, anchor="ne")

	def __create_reset_rot_button(self):
		ttk.Button(self, text="Reset rotation", command=self.__reset_rotation).place(relx=self.COMMON_X, rely=0.505, relheight=0.05, relwidth=0.095, anchor="ne")

	def __create_import_file_button(self):
		ttk.Button(self, text="Take a screenshot", command=self.__take_screenshot).place(relx=self.COMMON_X, rely=0.895, relheight=0.05, relwidth=0.2, anchor="ne")

	def __create_screenshot_button(self):
		self.FILE_NAME = tk.StringVar()
		ttk.Label(self, textvariable=self.FILE_NAME, foreground="#ffffff", background="#131113").place(relx=0.86, rely=0.817, relheight=0.035, relwidth=0.09, anchor="ne")
		ttk.Button(self, text="Import file", command=self.__read_file).place(relx=self.COMMON_X, rely=0.815, relheight=0.05, relwidth=0.095, anchor="ne")

	def __create_up_down_left_right_buttons(self):
		# Common values for placements of the buttons
		COMM_X = 0.89
		COMM_Y = 0.660
		COMM_RELATIVE_HIEGHT = 0.05
		COMM_RELATIVE_WIDTH  = 0.03
		ttk.Button(self, text="U", command=self.__move_up).place(relx=COMM_X, rely=0.595, relheight=COMM_RELATIVE_HIEGHT, relwidth=COMM_RELATIVE_WIDTH, anchor="ne")
		ttk.Button(self, text="D", command=self.__move_down).place(relx=COMM_X, rely=0.725, relheight=COMM_RELATIVE_HIEGHT, relwidth=COMM_RELATIVE_WIDTH, anchor="ne")
		ttk.Button(self, text="L", command=self.__move_left).place(relx=0.84, rely=COMM_Y, relheight=COMM_RELATIVE_HIEGHT, relwidth=COMM_RELATIVE_WIDTH, anchor="ne")
		ttk.Button(self, text="R", command=self.__move_right).place(relx=0.94, rely=COMM_Y, relheight=COMM_RELATIVE_HIEGHT, relwidth=COMM_RELATIVE_WIDTH, anchor="ne")

	def __create_color_pickers(self):
		'''Create the color pickers to change line/canvas/fill colors'''
		COMM_Y = 0.92

		# FILL
		self.fill_color = tk.StringVar()
		self.fill_color.set("#000000")
		ttk.Label(self, text="Fill color:", foreground="#ffffff", background="#131113").place(relx=0.08, rely=COMM_Y - 0.01, relheight=0.035, anchor="ne")
		self._fill_btn = tk.Button(self, text="", command=self.__pick_color_fill, relief='flat')
		self._fill_btn.place(relx=0.095, rely=COMM_Y, relheight=0.015, relwidth=0.05)
		self._fill_btn['bg'] = self.fill_color.get()

		# LINE
		self.line_color = tk.StringVar()
		self.line_color.set("#0000FF")
		ttk.Label(self, text="Line color:", foreground="#ffffff", background="#131113").place(relx=0.24, rely=COMM_Y - 0.01, relheight=0.035, anchor="ne")
		self._line_btn = tk.Button(self, text="", command=self.__pick_color_line, relief='flat')
		self._line_btn.place(relx=0.255, rely=COMM_Y, relheight=0.015, relwidth=0.05)
		self._line_btn['bg'] = self.line_color.get()

		# CANVAS' BACKGROUND
		ttk.Label(self, text="Canvas color:", foreground="#ffffff", background="#131113").place(relx=0.42, rely=COMM_Y - 0.01, relheight=0.035, anchor="ne")
		self._canvas_btn = tk.Button(self, text="", command=self.__pick_color_canvas, relief='flat')
		self._canvas_btn.place(relx=0.435, rely=COMM_Y, relheight=0.015, relwidth=0.05)

	def __create_fill_check(self):
		self._check_no_fill = tk.IntVar()
		ttk.Checkbutton(self, text="No fill", variable=self._check_no_fill, command=self.__changed, onvalue=True, offvalue=False).place(relx=0.704, rely=0.91, relheight=0.035)

	def __pick_color_fill(self):
		self.__pick_color("f")

	def __pick_color_line(self):
		self.__pick_color("l")

	def __pick_color_canvas(self):
		self.__pick_color("c")

	def __pick_color(self, picker):
		if(picker == "f"):
			col = colorchooser.askcolor(initialcolor = self.fill_color.get())
			if(col[1]):
				self.fill_color.set(col[1])
				self._fill_btn['bg']  = col[1]
		
		elif(picker == "c"):
			col = colorchooser.askcolor(initialcolor = self._canvas_color.get())
			if(col[1]):
				self._canvas_color.set(col[1])
				self._canvas_btn['bg']  = col[1]
				self._canvas['bg'] = self._canvas_color.get()
		
		else:
			col = colorchooser.askcolor(initialcolor = self.line_color.get())
			if(col[1]):
				self.line_color.set(col[1])
				self._line_btn['bg']  = col[1]
		
		self.__changed()

	def __changed(self, *args):
		self._changed = True

	def __reset_rotation(self):
		self._geometry_handler.reset_rotation()
		self.x_rotation_slider.set(0)
		self.y_rotation_slider.set(0)
		self.z_rotation_slider.set(0)
		self.__changed()

	def __take_screenshot(self):
		#Grab the top-left corner's coordinates
		x = self.winfo_rootx() + self._canvas.winfo_x()
		y = self.winfo_rooty() + self._canvas.winfo_y()

		#Grab the bottom-right corner's coordinates
		x1 = x + self._canvas.winfo_width()
		y1 = y + self._canvas.winfo_height()

		#Crop the screenshot to the determined coordinates
		screenshot = ImageGrab.grab().crop((x, y, x1, y1))
		save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("PNG Files", "*.png"), ("All Files", "*.*")))

		#Check if they actually saved and didn't exit before saving
		if save_path:
			screenshot.save(save_path)

	def __read_file(self):
		messagebox.showinfo(message='Only .obj files are compatible!', title="WARNING")

		file_path = filedialog.askopenfilename(defaultextension=".obj", filetypes=(("OBJ Files", "*.obj"), ("All Files", "*.*")))

		if len(file_path) and file_path[-4:] != ".obj":
			messagebox.showinfo(message="Incompatible file format", title="ERROR")

		elif len(file_path):
			self.FILE_NAME.set(file_path.split('/')[-1])
			self.__reset_rotation()
			with open(file_path) as file:
				self._geometry_handler._verticies, self._geometry_handler._faces = obj_files_handler.extract_data(file)
				self._file_exists = True

	def __move_up(self):
		self._geometry_handler.update_position(0, -1 * self.MOVING_STEP)
		self.__changed()

	def __move_down(self):
		self._geometry_handler.update_position(0, self.MOVING_STEP)
		self.__changed()

	def __move_left(self):
		self._geometry_handler.update_position(-1 * self.MOVING_STEP, 0)
		self.__changed()

	def __move_right(self):
		self._geometry_handler.update_position(self.MOVING_STEP, 0)
		self.__changed()

	def draw(self):
		self.__set_rotations()
		self.__set_zoom()
		if(self._file_exists and self._changed):
			#Delete all the previous points and lines in order to draw new ones
			self._canvas.delete("all")
			self.__update_colors()
			self.__draw_object()
			self._changed = False

	def __set_zoom(self):
		self._geometry_handler.set_zoom(self.zoom_slider.get())

	def __set_rotations(self):
		self._geometry_handler.reset_rotation(x=self.x_rotation_slider.get(), 
											  y=self.y_rotation_slider.get(), 
											  z=self.z_rotation_slider.get()
		)

	def __change_fill_color(self, color: str, no_fill: bool = False):
		'''Change the face fill color'''
		self._fill_color_holder = "" if no_fill else color

	def __change_line_color(self, color):
		''''''
		self._line_color_holder = color

	def __draw_point(self, point: 'tuple(int, int)') -> None:
		'''Draw a point on the canvas'''
		self._canvas.create_oval(point[0], point[1],
						   		 point[0], point[1],
						   		 width=self.POINT_SIZE,
						   		 fill=self.POINT_COLOR)

	def __draw_faces(self, points: dict) -> None:
		''''''
		for face in self._geometry_handler.faces:
			# Grab the points that make up that specific face
			to_draw = [points[f] for f in face]
			for point in to_draw:
				if(point[0] < 0 or
				   point[1] < 0 or
				   point[0] > self.CANVAS_WIDTH or
				   point[1] > self.CANVAS_HEIGHT
				):
					continue # Don't draw points that are out of the screen
				self.__draw_point(point)

			self._canvas.create_polygon(to_draw, outline=self._line_color_holder, fill=self._fill_color_holder)
	
	def __draw_object(self):
		'''Draw the object on the canvas'''
		projected_points = self._geometry_handler.transform_object()
		self.__draw_faces(projected_points)
	
	def __update_colors(self):
		self.__change_fill_color(self.fill_color.get(), self._check_no_fill.get())
		self.__change_line_color(self.line_color.get())