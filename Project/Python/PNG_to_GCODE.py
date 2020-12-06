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
    return all_instructions


# In[13]:


#naive_to_gcode(naive_gcode("Images/gray_test.png", 0.7))


# # Marching Squares

# In[14]:


def get_reference_squares(filename, threshold, increment):
    data = img_to_gray(import_image(filename))
    references = []
    num_rows = len(data)
    num_cols = len(data[0])
    important_squares = []
    print(str(num_rows) + "x" + str(num_cols))
    for row in range(0, num_rows, increment):
        for col in range(0, num_cols, increment):
            if data[row][col] < threshold:
                important_squares.append([row, col])
    plt.imshow(data, cmap="gray")
    plt.show()
    return important_squares


# In[15]:


#get_reference_squares("Images/dog.jpg", .5, 5)


# In[16]:


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


# In[17]:


#get_case(str([0,0,0,0]))


# In[18]:


def check_corner(data, row, col, threshold):
    corner = 0
    if data[row][col] > threshold:
        corner = 1
    else:
        corner = 0
    return corner


# In[19]:


def check_case(data, row_num, col_num, increment, threshold):
    corners = []
    for row, col in [(row_num+i,col_num+j) for i in (0,increment) for j in (0,increment)]:
        if row < len(data) and col < len(data[0]):
            corners.append(check_corner(data, row, col, threshold))
        elif row > len(data):
            row = len(data)-1
            corners.append(check_corner(data, row, col, threshold))
        elif col > len(data[0]):
            col = len(data[0])-1
            corners.append(check_corner(data, row, col, threshold))
    return get_case(str(corners))


# In[20]:


def check_square(row_num, col_num, data, increment, threshold):
    corners = []
    contours = []
    case = 0
    for row, col in [(row_num+i,col_num+j) for i in (0,increment) for j in (0,increment)]:
        try:
            #This is for adjacent squares in bounds
            if data[row][col] > threshold:
                interpolant = np.round((data[row_num][col_num]/data[row][col])*increment)
                if row > row_num:
                    contours.append([row_num + interpolant, col_num])
                elif row < row_num:
                    contours.append([row_num - interpolant, col_num])
                elif col > col_num:
                    contours.append([row_num, col_num + interpolant])
                elif col < col_num:
                    contours.append([row_num, col_num - interpolant])
                else:
                    print("Something went wrong")
        except IndexError:
             #This is for if the adjacent square is out of bounds
            print(row)
            print(col)
            contours.append([row, col])
            print("This cell is out of bounds")
            print("Don't worry this may happen, but needs to be dealt with.")
            print("-"*40)
        except ZeroDivisionError:
             #This is for if the adjacent square is Pure black
            print(row)
            print(col)
            print("This SHOULD never happen")
            print("-"*40)
        except:
            #This is to catch any other error
            print("Unexpected error:", sys.exc_info()[0])
            print("-"*40)
        case = get_case(str(corners))
        res = [] 
        for i in contours:
            if i not in res:
                res.append(i)
    return res


# In[21]:


#print(check_square(25, 190, gray_img, 5, 0.5))
#check_case(gray_img, 25, 190, 5, 0.5)


# In[22]:


def get_ms_contours(filename, threshold, increment, marker_size):
    refrences = get_reference_squares(filename, threshold, increment)
    x = []
    y = []
    data = img_to_gray(import_image(filename))
    squares = []
    contours = []
    for coord in refrences:
        contours.append([check_case(data, coord[0], coord[1], increment, threshold), check_square(coord[0], coord[1], data, increment, threshold)])
    for contour in contours:
        case = contour[0]
        coords = contour[1]
        for coord in coords:
            x.append(coord[1])
            y.append(coord[0])
    plt.scatter(x, y, s = marker_size)
    return contours


# In[23]:


#get_ms_contours("Images/gray_test.png", .7, 5, 5)


# # Define GCODE

# In[24]:


def get_GCode(contours):
    i = 0
    all_instructions = []
    to_coords = lambda coords: {'X': coords[1], 'Y': coords[0]}
    for coords in contours:
        if i == 0:
            gcode = GCodeRapidMove(**to_coords(coords))
            print("%s" % gcode)
            i=1
        else:
            gcode = GCodeLinearMove(**to_coords(coords))
            print("%s" % gcode)
            i=0
        all_instructions.append(gcode)
        print("-" * 40)
    return all_instructions


# In[25]:


#gcodes = get_GCode(get_ms_contours("Images/gray_test.png", .7, 5, 1))


# # Output GCODE to file

# In[26]:


def output_gcode(all_instructions, filename):
    File_object = open(filename,"w")
    for gcode in all_instructions:
        print(gcode)
        File_object.write(str(gcode) + ";\n")
    File_object.close()


# In[27]:


#output_gcode(naive_to_gcode(naive_gcode("Images/smile.png", 0.7)), "output2.gcode")


# In[28]:


#output_gcode(get_GCode(get_ms_contours("Images/gray_test.png", .7, 5, 1)), "output4.gcode")


# In[ ]:




