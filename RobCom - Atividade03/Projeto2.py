#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "DualStream799"

# Importing Libraries:
from matplotlib import pyplot as plt
from heapq import nlargest, nsmallest
from math import atan, degrees, sqrt
import numpy as np
import time
import cv2


def frame_flip(capture, flip=False, flip_mode=0):
	"""Recieves a webcam frame and flips it or not, depending on 'flip' argument
	X-axis Flip (Vertical): 'flip_mode' = 0
	Y-axis Flip (Horizontal): 'flip_mode' > 0
	Both-axis Flip(Vertical and Horizontal): 'flip_mode' < 0 """

	# Capture frame-by-frame:
	ret, frame = capture.read()
	# Invert captured frame:
	if flip == True:
		return cv2.flip(frame, 1)
	else:
		return frame

def text_on_frame(frame, text, position, thickness, font_size=1, text_color=(255, 255, 255), shadow_color=(128, 128, 128), font_style=cv2.FONT_HERSHEY_SIMPLEX, line_style=cv2.LINE_AA):
	"""Displays a text on the frame with a shadow behind it for better visualization on any background"""
	cv2.putText(frame, text, position, font_style, font_size, shadow_color, thickness+1, line_style)
	cv2.putText(frame, text, position, font_style, font_size, text_color, thickness, line_style)

def calculate_m (point1, point2):
	"""Calculates the angular coeficient of a line between two points"""
	return (point2[1] - point1[1])/(point2[0] - point1[0])

def calculate_h(point, m):
	"""  """
	return point[1] - m*point[0]
	
def angular_coefficient(point1, point2, decimals=0):
	"""Calculates the angular coefficient if a line between two points using the current formula: (y - y0) = m*(x - x0)"""
	return round(degrees(atan((point2[1] - point1[1])/(point2[0] - point1[0]))), decimals)



def calculate_vanishing_point(p1, p2, q1, q2):
	
	m1 = calculate_m(p1, p2)
	m2 = calculate_m(q1, q2)
	
	h1 = calculate_h(p1, m1)
	h2 = calculate_h(q1, m2)
	
	xi = (h2 - h1)/(m1 - m2)
	yi = m1*xi + h1
	
	return (xi, yi)



# Window name text:
window_name = "Vanishing Point Detector Algorithm"
# Window width and height:
window_size = (640, 480)
# Display mode controller:
display_mode = 'default'
dev_mode = True
# Angular Coefficient start value:
m = 0.0
sheet_distance = 0.0
min_matches_val = 1
# Line Filters:
min_proj_x = 400 # vertical lines' filter
min_proj_y = 200 # horizontal lines' filter
min_45_deg = 100 # 45º lines' filter
# Display mode dict for text display:
display_mode_text_dict = {'default': 'Nothing',
						  'canny': 'Edges',
						  'hough': 'Perspective Lines',
						  'projection': 'Vanishing Point',
						  'all': 'Everything'}
# Color dict for "paint" elements:
color_dict = {'cyan': (255, 255, 0),
			  'magenta': (255, 0, 255)}


# Parameters to use when opening the webcam:
if dev_mode:
	cap = cv2.VideoCapture('video_test01.mp4')
else:
	cap = cv2.VideoCapture(0)

# Setting a resolution limit for video capture:
cap.set(cv2.CAP_PROP_FRAME_WIDTH, window_size[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, window_size[1])


while True:

	# Reads frame and flips it horizontally:
	bgr_frame = frame_flip(cap, True, 1)
	# Converts frame from BGR to Grayscale:
	gray_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2GRAY)
	# Converts frame from BGR to RGB:
	rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

	# Bluring the grayscale frame in order to enhance edge detection:
	blured_frame = cv2.GaussianBlur(gray_frame, ksize=(5, 5), sigmaX=0)
	# Using Canny's algorithm to detect edges:
	edges_frame = cv2.Canny(blured_frame, 50, 150, apertureSize=3)
	
	if display_mode == 'hough' or display_mode == 'projection' or display_mode == 'all':
		# Makes a copy of the captured frame:
		lines_frame = bgr_frame.copy()
		# Using Hough's algorithm to detect lines:
		#hough_points = cv2.HoughLinesP(edges_frame, 1, np.pi/180, 200)
		hough_rho_theta = cv2.HoughLines(edges_frame, 1, np.pi/180, 200)
#		if hough_points is not None:]
#
#			for x1, y1, x2, y2 in hough_points[0]:
#				point1 = (x1, y1)
#				point2 = (x2, y2)
#				color = (255, 0, 255)
#				cv2.line(lines_frame, point1, point2, color, 2)
#			print(len(hough_points))
		lines_list = []
		if hough_rho_theta is not None:
			for line in hough_rho_theta:
				for rho, theta in line:
					# Converts the lines detected from polar to cartesian representation:
					a = np.cos(theta)
					b = np.sin(theta)
					x0 = a*rho
					y0 = b*rho
					x1 = int(x0 + 1000*(-b))
					y1 = int(y0 + 1000*(a))
					x2 = int(x0 - 1000*(-b))
					y2 = int(y0 - 1000*(a))
					# Calculates line's filter parameters:
					proj_x = abs(x1 - x2) # small values means a almost vertical line
					proj_y = abs(y1 - y2) # snall values means a almost horizontal line
					proj_assimetry = abs(proj_x - proj_y) # small values means a 45º line
					# Gets rid of almost horizontal or vertical lines (and avoids 'angular_coefficient' method gets 'ZeroDivisionError'):
					if  proj_x > min_proj_x and proj_y > min_proj_y:
						# Creates two point from the positions calculated previously:
						point1 = (x1, y1)
						point2 = (x2, y2)
						# Calculates angular coefficient:
						m = angular_coefficient(point1, point2, decimals=5)
						# Stores the two points and the algular coefficient:
						lines_list.append((point1, point2, m, proj_assimetry))
						# Draws the resulting line on the frame:
						cv2.line(lines_frame, point1, point2, (255, 0, 255), 1)


		if  display_mode == 'projection' or display_mode == 'all':
			# Makes a copy of the captured frame:
			vanishing_frame = lines_frame.copy()
			
			# Checks if there's at least two lines to calculate the vanishing point:
			if len(lines_list) >= 2:
				# Finds the two lines closest to 45º:
				min_inc_line = nsmallest(2, lines_list, key=lambda x: x[3])
				# Calculates the position of the vanishing point using the the two lines found:
				#calculate_vanishing_point()


				print(min_inc_line[0])

	# Displays the resulting frame (Using keyboard to change visualization: simply change the image to be displayed):
	# Key '1':
	if display_mode == 'default':
		text_on_frame(bgr_frame, "Detecting " + display_mode_text_dict[display_mode], (0, 30), 1)
		cv2.imshow(window_name, bgr_frame)
	# Key '2':
	elif display_mode == 'canny':
		text_on_frame(edges_frame, "Detecting " + display_mode_text_dict[display_mode], (0, 30), 1)
		cv2.imshow(window_name, edges_frame)
	# Key '3':
	elif display_mode == 'hough':
		text_on_frame(lines_frame, "Detecting " + display_mode_text_dict[display_mode], (0, 30), 1)
		cv2.imshow(window_name, lines_frame)
	# Key '4':
	elif display_mode == 'projection':
		text_on_frame(vanishing_frame, "Detecting " + display_mode_text_dict[display_mode], (0, 30), 1)
		cv2.imshow(window_name, vanishing_frame)

	# Waits for a certain time (in milisseconds) for a key input ('0xFF' is used to handle input changes caused by NumLock):
	delay_ms = 60
	key_input = cv2.waitKey(delay_ms) & 0xFF

	# Display Mode Switch:
	# Exit the program:
	if  key_input == ord('q'):	
		break
	# Capture a frame and saves it as a .jpg file:
	elif key_input == ord('c'):
		cv2.imwrite('single_frame.jpg', cv2.flip(bgr_frame, 1))
		print('frame aptured')
	# Default visualization:
	elif key_input == ord('1'):
		display_mode = 'default'
		print(display_mode)
	# Edge Detection visualization:
	elif key_input == ord('2'):
		display_mode = 'canny'
		print(display_mode)
	# Line Detection visualization:
	elif key_input == ord('3'):
		display_mode = 'hough'
		print(display_mode)
	elif key_input == ord('4'):
		display_mode = 'projection'
		print(display_mode)
	elif key_input == ord('d'):
		dev_mode = not dev_mode
		print("dev_mode:", dev_mode)

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()