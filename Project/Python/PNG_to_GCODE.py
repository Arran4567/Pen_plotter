#!/usr/bin/env python
# coding: utf-8

# # Library Imports

# In[1]:


import os
import sys
import skimage 
import numpy as np
import matplotlib.pyplot as plt
from pygcode import *
from skimage import measure
from skimage import io
from skimage import data
from skimage.color import rgb2gray
from PIL import Image


# # Import PNG file

# In[2]:


class Contour:
    def __init__(self, start_row, start_col, end_row, end_col):
        self.start_row = start_row
        self.start_col = start_col
        self.end_row = end_row
        self.end_col = end_col
        
    def get_start(self):
        return self.start_row, self.start_col
    
    def get_end(self):
        return self.end_row, self.end_col
        
    def set_start(self, r, c):
        self.start_row = r
        self.start_col = c
    
    def set_end(self, r, c):
        self.end_row = r
        self.end_col = c


# In[3]:


class Square:
    def __init__(self, top_left, contours):
        self.case = case
        self.top_left = top_left
        self.contours = contours


# In[4]:


def import_image(path):
    file = os.path.join(path)
    img = ""
    try:
        img = io.imread(file)
    except:
        print("File not found")
    return img


# In[5]:


#image = import_image("Images/dog.jpg")


# # Grayscale Image

# In[6]:


def img_to_gray(original):
    grayscale = rgb2gray(original)
    fig, axes = plt.subplots(1, 1, figsize=(4, 4))

    axes.imshow(grayscale, cmap=plt.cm.gray)
    
    fig.tight_layout()
    return grayscale


# In[7]:


#gray_img = img_to_gray(import_image("Images/dog.jpg"))


# # Find Contours

# In[8]:


def find_contours(image, accuracy):
    img = np.flipud(image)
    
    # Find contours at a constant value defined by parameter accuracy
    contours = measure.find_contours(img, accuracy)
    
    # Display the image and plot all contours found
    fig, ax = plt.subplots()

    for n, contour in enumerate(contours):
        ax.plot(contour[:, 1], contour[:, 0], linewidth=1)

    ax.axis('image')
    plt.show()
    print(contours)
    return contours


# In[9]:


#contours = find_contours(gray_img, .3)
#len(contours)


# # Naive Approach

# In[10]:


def naive_gcode(image, threshold):
    data = img_to_gray(import_image(image))
    
    num_rows = len(data)
    num_cols = len(data[0])
    print(num_rows)
    print(num_cols)
    
    lines = []
    cols = []
                
    for row in range(0, num_rows):
        cols = []
        border = True
        for col in range(0, num_cols): 
            if data[row][col] > threshold:
                if border == False:
                    cols.append(col - 1)
                    border = True
            elif data[row][col] < threshold and border == True:
                cols.append(col)
                border = False
            elif data[row][col] < threshold and col == num_cols-1:
                cols.append(col)
                border = False
        if len(cols) % 2 != 0:
            cols.append(cols[len(cols)-1])
        lines.append(cols)
    
    #Display coords
    i=0
    points = []
    for row in range(0, num_rows):
        for point in lines[i]:
            points.append([i, point])
        i += 1
    
    xs = []
    ys = []
    for coord in points:
        xs.append(coord[1])
        ys.append(coord[0])
    plt.scatter(xs, ys, s = 1)
    plt.show()
    
    lines.reverse()
    return lines


# In[11]:


#naive_gcode("Images/gray_test.png", 0.7)


# In[12]:


def naive_to_gcode(lines):
    all_instructions = []
    num_rows = len(lines)
    to_coords = lambda coords: {'X': coords[0], 'Y': coords[1]}
    i = 0
    for row in range(0, num_rows):
        for col in lines[row]:
            if i == 0:
                gcode = GCodeRapidMove(**to_coords([col, row]))
                print("%s" % gcode)
                i=1
            else:
                gcode = GCodeLinearMove(**to_coords([col, row]))
                print("%s" % gcode)
                i=0
            all_instructions.append(gcode)
    print(all_instructions)
    return all_instructions


# In[13]:


#naive_to_gcode(naive_gcode("Images/gray_test.png", 0.7))


# # Marching Squares

# In[14]:


def get_case(x):
    return {
        str([0,0,0,0]): 0,
        str([0,0,1,0]): 1,
        str([0,0,0,1]): 2,
        str([0,0,1,1]): 3,
        str([0,1,0,0]): 4,
        str([0,1,1,0]): 5,
        str([0,1,0,1]): 6,
        str([0,1,1,1]): 7,
        str([1,0,0,0]): 8,
        str([1,0,1,0]): 9,
        str([1,0,0,1]): 10,
        str([1,0,1,1]): 11,
        str([1,1,0,0]): 12,
        str([1,1,1,0]): 13,
        str([1,1,0,1]): 14,
        str([1,1,1,1]): 15,
    }.get(x, 16)


# In[15]:


#get_case(str([0,0,0,0]))


# In[16]:


def check_corner(data, row, col, threshold):
    corner = 0
    if row >= len(data) and col >= len(data[0]):
        row = len(data)-1
        col = len(data[0])-1
    elif col >= len(data[0]):
        col = len(data[0])-1
    elif row >= len(data):
        row = len(data)-1
    else:
        if data[row][col] > threshold:
            corner = 1
        else:
            corner = 0
    return corner


# In[17]:


def check_case(data, row_num, col_num, increment, threshold):
    corners = []
    for row, col in [(row_num+i,col_num+j) for i in (0,increment) for j in (0,increment)]:
        if row < len(data) and col < len(data[0]):
            corners.append(check_corner(data, row, col, threshold))
        elif row >= len(data) and col >= len(data[0]):
            row = len(data)-1
            col = len(data[0])-1
            corners.append(check_corner(data, row, col, threshold))
        elif row >= len(data):
            row = len(data)-1
            corners.append(check_corner(data, row, col, threshold))
        elif col >= len(data[0]):
            col = len(data[0])-1
            corners.append(check_corner(data, row, col, threshold))
    return get_case(str(corners))


# In[18]:


def calc_interpolant(val1, val2, threshold, increment):
    interpolant = (val1-threshold)/(val1-val2)
    return np.round(interpolant*5)


# In[19]:


def check_square(data, row_num, col_num, increment, threshold):
    case = check_case(data, row_num, col_num, increment, threshold)
    corners = []
    contour = []
    for row, col in [(row_num+i,col_num+j) for i in (0,increment) for j in (0,increment)]:
        if row >= len(data) and col >= len(data[0]):
            row = len(data)-1
            col = len(data[0])-1
        elif col >= len(data[0]):
            col = len(data[0])-1
        elif row >= len(data):
            row = len(data)-1
        corners.append([row, col])
    if case == 1 or case == 14:
        left_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[2][0]][corners[2][1]], threshold, increment)
        bottom_interpolant = calc_interpolant(data[corners[2][0]][corners[2][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        contour.append([corners[0][0] + left_interpolant, corners[0][1], corners[2][0], corners[2][1] + bottom_interpolant])
    elif case == 2 or case == 13:
        bottom_interpolant = calc_interpolant(data[corners[2][0]][corners[2][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        right_interpolant = calc_interpolant(data[corners[1][0]][corners[1][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        contour.append([corners[2][0], corners[2][1] + bottom_interpolant, corners[1][0] + right_interpolant, corners[1][1]])
    elif case == 3 or case == 12:
        left_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[2][0]][corners[2][1]], threshold, increment)
        right_interpolant = calc_interpolant(data[corners[1][0]][corners[1][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        contour.append([corners[0][0] + left_interpolant, corners[0][1], corners[1][0] + right_interpolant, corners[1][1]])
    elif case == 4 or case == 11:
        top_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[1][0]][corners[1][1]], threshold, increment)
        right_interpolant = calc_interpolant(data[corners[1][0]][corners[1][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        contour.append([corners[0][0], corners[0][1] + top_interpolant, corners[1][0] + right_interpolant, corners[1][1]])
    elif case == 5 or case == 10:
        top_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[1][0]][corners[1][1]], threshold, increment)
        left_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[2][0]][corners[2][1]], threshold, increment)
        bottom_interpolant = calc_interpolant(data[corners[2][0]][corners[2][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        right_interpolant = calc_interpolant(data[corners[1][0]][corners[1][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        contour.append([corners[0][0], corners[0][1] + top_interpolant, corners[0][0] + left_interpolant, corners[0][1]])
        contour.append([corners[2][0], corners[2][1] + bottom_interpolant, corners[1][0] + right_interpolant, corners[1][1]])
    elif case == 6 or case == 9:
        top_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[1][0]][corners[1][1]], threshold, increment)
        bottom_interpolant = calc_interpolant(data[corners[2][0]][corners[2][1]], data[corners[3][0]][corners[3][1]], threshold, increment)
        contour.append([corners[0][0], corners[0][1] + top_interpolant, corners[2][0], corners[2][1] + bottom_interpolant])
    elif case == 7 or case == 8:
        top_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[1][0]][corners[1][1]], threshold, increment)
        left_interpolant = calc_interpolant(data[corners[0][0]][corners[0][1]], data[corners[2][0]][corners[2][1]], threshold, increment)
        contour.append([corners[0][0], corners[0][1] + top_interpolant, corners[0][0] + left_interpolant, corners[0][1]])
    return contour


# In[20]:


#print(check_case(gray_img, 145, 140, 5, 0.7))
#print(check_square(gray_img, 145, 140, 5, 0.7))


# In[21]:


def get_reference_squares(data, threshold, increment):#
    references = []
    num_rows = len(data)
    num_cols = len(data[0])
    important_squares = []
    print(str(num_rows) + "x" + str(num_cols))
    for row in range(0, num_rows, increment):
        for col in range(0, num_cols, increment):
            if check_case(data, row, col, increment, threshold) != 15 and check_case(data, row, col, increment, threshold) != 0:
                important_squares.append([row, col])
    plt.imshow(data, cmap="gray")
    xs = [x[1] for x in important_squares]
    ys = [x[0] for x in important_squares]
    plt.scatter(xs, ys, 0.5)
    plt.show()
    return important_squares


# In[22]:


#get_reference_squares(np.flipud(img_to_gray(import_image("Images/smile.png"))), .5, 5)


# In[23]:


def get_ms_contours(filename, threshold, increment):
    data = np.flipud(img_to_gray(import_image(filename)))
    references = get_reference_squares(data, threshold, increment)
    x = []
    y = []
    squares = []
    contours = []
    for coord in references:
        square = check_square(data, coord[0], coord[1], increment, threshold)
        print(square)
        contours.append(square)
    return contours


# In[24]:


#print(get_ms_contours("Images/gray_test.png", .7, 5))


# In[25]:


def ms_to_GCode(squares):
    i = 0
    all_instructions = []
    to_coords = lambda coords: {'X': coords[1], 'Y': coords[0]}
    for contours in squares:
        for contour in contours:
            initial_coords = [contour[0], contour[1]]
            final_coords = [contour[2], contour[3]]
            initial_coords_gcode = GCodeRapidMove(**to_coords(initial_coords))
            final_coords_gcode = GCodeLinearMove(**to_coords(final_coords))
            all_instructions.append(initial_coords_gcode)
            all_instructions.append(final_coords_gcode)
    return all_instructions


# In[26]:


#gcodes = ms_to_GCode(get_ms_contours("Images/dog.jpg", .7, 5))
#print(gcodes)


# # Output GCODE to file

# In[27]:


def output_gcode(all_instructions, filename):
    File_object = open(filename,"w")
    for gcode in all_instructions:
        print(gcode)
        File_object.write(str(gcode) + ";\n")
    File_object.close()


# In[28]:


#output_gcode(naive_to_gcode(naive_gcode("Images/smile.png", 0.7)), "output2.gcode")


# In[29]:


#output_gcode(ms_to_GCode(get_ms_contours("Images/dog.jpg", .7, 5)), "output.gcode")


# In[ ]:




