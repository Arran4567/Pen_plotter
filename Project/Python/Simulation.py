#!/usr/bin/env python
# coding: utf-8

# In[1]:


from turtle import *
import re
from pygcode import *
import gc


# In[2]:


#Global variables used for storing home location and whether an emergency stop should be performed
x_home = 0
y_home = 0
stop = False


# In[3]:


#A function to change the value of the global stop variable
def set_stop(bool_stop):
    global stop 
    stop = bool_stop


# In[4]:


#Creates the turtle object
def create_turtle():
    t = Turtle()
    return t


# In[5]:


#Basic setup for the turtle environment
def setup_turtle(t, title):
    s = t.getscreen()
    s.title(title)
    s.setup(width = 1.0, height = 1.0)
    canvas = s.getcanvas()
    root = canvas.winfo_toplevel()
    root.overrideredirect(1)
    
    t.hideturtle()
    t.penup()
    t.shape("classic")
    t.showturtle()
    t.speed(10)


# In[6]:


#Provides a method for closing the environment on click
def close_on_click(t):
    t.getscreen().exitonclick()


# In[7]:


#Provides a method for closing the environment on demand
def close_sim(t):
    t.getscreen().bye()


# In[8]:


#Reopens the environment with a new turtle object
def resurrect_environment(title):
    Turtle._screen = None
    TurtleScreen._RUNNING = True
    t = create_turtle()
    setup_turtle(t, title)
    return t


# In[9]:


#A function to change the value of the global home variables
def set_home(t, x, y):
    global x_home
    global y_home
    t.showturtle()
    t.setposition(x, y)


# In[10]:


#t1 = create_turtle()
#setup_turtle(t1, "Calibrate marker")


# In[11]:


#set_home(t1, -750, -400)
#close_on_click(t1)


# In[12]:


#close_sim(t1)


# In[13]:


#Moves the turtle to specified co-ordinates without drawing a line
def move_pos(t, x, y, scale):
    t.penup()
    t.setposition((x * scale) + x_home, (y*scale) + y_home)


# In[14]:


#Moves the turtle to specified co-ordinates while drawing a line
def draw_line(t, x, y, scale):
    t.pendown()
    t.setposition((x * scale) + x_home, (y*scale) + y_home)


# In[15]:


#Moves the turtle along a specific arced path while drawing a line
def draw_arc(t, x, y, r, start, end, scale):
    x_real = (x * scale) + x_home
    y_real = (y * scale) + y_home
    r_real = r * scale
    extent = end-start
    while extent < 0:
        extent += 360
    print(x_real, y_real)
    
    t.penup()
    t.setposition(x_real, y_real)
    t.pendown()
    t.setheading(start)
    t.circle(r_real, extent)


# In[16]:


#Converts the gcode read from a specified file into variables which can be used to move the turtle
def convert_gcode(t, gcode, scale):
    global stop
    with open(gcode, 'r') as fh:
        for line_text in fh.readlines():
            if stop == False:
                line = Line(line_text)

                print(line)  # will print the line (with cosmetic changes)

                x_substring = float(re.search("X(.*?) ", str(line)).group(1))
                y_substring = float(re.search("Y(.*?) ", str(line)).group(1))

                print(x_substring)
                print(y_substring)

                if str(line)[0:3] == "G00":
                    print("G00")
                    move_pos(t, x_substring, y_substring, scale)
                elif str(line)[0:3] == "G01":
                    print("G01")
                    draw_line(t, x_substring, y_substring, scale)
                elif str(line)[0:3] == "G03":
                    print("G03")
                    r = float(re.search("R(.*?) ", str(line)).group(1))
                    start = float(re.search("S(.*?) ", str(line)).group(1))+90
                    end = float(re.search("E(.*?) ", str(line)).group(1))+90
                    draw_arc(t, x_substring, y_substring, r, start, end, scale)
                else:
                    print("Please enter valid instructions.")

                print('-'*40)  # will print the line (with cosmetic changes)
            else:
                stop = False
                close_sim(t)
    close_on_click(t)
    return True


# In[17]:


#draw_arc(t, 3.516934, 2.6563950000000003, 0.119156, 270.0, 315.0)


# In[20]:


#t1 = create_turtle()
#set_home(t1, -750, -400)
#close_sim(t1)
#t1 = resurrect_environment("Click screen when finished to exit")
#convert_gcode(t1, "output.gcode", 1)


# In[21]:


#t1 = resurrect_environment("Click screen when finished to exit")
#convert_gcode(t1, "output2.gcode", 1, 2000, 1200)


# In[22]:


#t1 = resurrect_environment("Click screen when finished to exit")
#convert_gcode(t1, "output4.gcode", 1, 2000, 1200)

