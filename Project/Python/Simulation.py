#!/usr/bin/env python
# coding: utf-8

# In[1]:


from turtle import *
import re
from pygcode import *
import gc


# In[2]:


x_home = 0
y_home = 0


# In[3]:


def create_turtle():
    t = Turtle()
    return t


# In[4]:


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


# In[5]:


def close_on_click(t):
    t.getscreen().exitonclick()


# In[6]:


def close_sim(t):
    t.getscreen().bye()


# In[7]:


def resurrect_environment(title):
    Turtle._screen = None
    TurtleScreen._RUNNING = True
    t = create_turtle()
    setup_turtle(t, title)
    return t


# In[8]:


def set_home(t, x, y):
    t.showturtle()
    t.setposition(x, y)
    x_home = x
    y_home = y
    return x, y


# In[9]:


#t1 = create_turtle()
#setup_turtle(t1, "Calibrate marker")


# In[10]:


#x_home, y_home = set_home(t1, -750, -400)
#close_on_click(t1)


# In[11]:


#close_sim(t1)


# In[12]:


def move_pos(t, x, y, scale):
    t.penup()
    t.setposition((x * scale) + x_home, (y*scale) + y_home)


# In[13]:


def draw_line(t, x, y, scale):
    t.pendown()
    t.setposition((x * scale) + x_home, (y*scale) + y_home)


# In[14]:


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


# In[15]:


def convert_gcode(t, gcode, scale, x_fix, y_fix):
    with open(gcode, 'r') as fh:
        for line_text in fh.readlines():
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


# In[16]:


#draw_arc(t, 3.516934, 2.6563950000000003, 0.119156, 270.0, 315.0)


# In[17]:


#def draw_smiley(t):
#    t.showturtle()
#    t.speed(1)
#    t.up()
#    t.goto(0, -100)  # center circle around origin
#    t.down()
#    
#    t.begin_fill()
#    t.fillcolor("yellow")  # draw head
#    t.circle(100)
#    t.end_fill()

#    t.up()
#    t.goto(-67, -40)
#    t.setheading(-60)
#    t.width(5)
#    t.down()
#    t.circle(80, 120)  # draw smile

#    t.fillcolor("black")

#    for i in range(-35, 105, 70):
#        t.up()
#        t.goto(i, 35)
#        t.setheading(0)
#        t.down()
#        t.begin_fill()
#        t.circle(10)  # draw eyes
#        t.end_fill()
    
#    t.up()
#    t.goto(-67, -40)


# In[18]:


#draw_smiley()


# In[19]:


#t1 = resurrect_environment("Click screen when finished to exit")
#convert_gcode(t1, "output.gcode", 1, 2000, 1200)
#close_on_click(t1)


# In[20]:


#t1 = resurrect_environment("Click screen when finished to exit")
#convert_gcode(t1, "output2.gcode", 1, 2000, 1200)
#close_on_click(t1)


# In[21]:


#t1 = resurrect_environment("Click screen when finished to exit")
#convert_gcode(t1, "output4.gcode", 1, 2000, 1200)
#close_on_click(t1)


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




