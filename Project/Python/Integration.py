#!/usr/bin/env python
# coding: utf-8

# In[1]:


png = __import__("PNG_to_GCODE")
dxf = __import__("DXF_to_GCODE")
sim = __import__("Simulation")


# In[2]:


def turtle_setup():
    t1 = sim.create_turtle()
    sim.close_sim(t1)
    return t1


# In[3]:


#t1 = turtle_setup()


# In[4]:


def import_image(filename):
    if filename.endswith('.png'):
        img = png.import_image(filename)
        filetype = "png"
    elif filename.endswith('.dxf'):
        img, doc, msp, group = dxf.get_dxf(filename)
        filetype = "dxf"
    else:
        print("Please choose a supported file format.")
    return img


# In[5]:


#import_image("DXF/knot_005.dxf")


# In[6]:


def open_sim(title):
    t = sim.resurrect_environment(title)
    return t


# In[7]:


def close_sim(t):
    sim.close_sim(t)


# In[8]:


def calibrate_sim(t, x, y):
    sim.set_home(t, x, y)
    x_home = x
    y_home = y


# In[9]:


def move_turtle(t, x, y, scale):
    sim.move_pos(t, x, y, scale)


# In[10]:


def draw_output(t, gcode, scale):
    sim.convert_gcode(t, gcode, scale)


# In[11]:


#t1 = open_sim("Calibrate")
#calibrate_sim(t1, -750, -400)
#close_sim(t1)


# In[12]:


def view_dxf(file_path):
    fig, doc, msp, group = dxf.get_dxf(file_path)
    return fig, doc, msp, group


# In[13]:


def dxf_generate_gcode(file_path, output_path):
    fig, doc, msp, group = view_dxf(file_path)
    dxf.output_all_info(msp, output_path)


# In[14]:


def png_generate_gcode(file_path, accuracy, output_path, algorithm):
    if algorithm:
        instructions = png.naive_to_gcode(png.naive_gcode(file_path, accuracy))
    else:
        instructions = png.ms_to_GCode(png.get_ms_contours(file_path, accuracy, 5))
    png.output_gcode(instructions, output_path)


# In[15]:


#png_generate_gcode("Images\\dog.jpg", 0.7, "output.gcode", False)


# In[16]:


#dxf_generate_gcode("DXF\\frame.dxf", "output.gcode")
#t1 = open_sim("Click on the screen to close when finished.")
#draw_output(t1, "output.gcode", 1)


# In[17]:


def stop_sim():
    sim.set_stop(True)

