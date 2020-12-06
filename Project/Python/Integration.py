#!/usr/bin/env python
# coding: utf-8

# In[1]:


png = __import__("PNG_to_GCODE")
dxf = __import__("DXF_to_GCODE")
sim = __import__("Simulation")


# In[2]:


def turtle_setup():
    t1 = sim.create_turtle()
    close_sim(t1)
    return t1


# In[ ]:


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


# In[ ]:


#import_image("DXF/knot_005.dxf")


# In[ ]:


def open_sim(title):
    t = sim.resurrect_environment(title)
    return t


# In[ ]:


def close_sim(t):
    sim.close_sim(t)


# In[ ]:


def calibrate_sim(t, x, y):
    sim.set_home(t, x, y)
    x_home = x
    y_home = y


# In[ ]:


def move_turtle(t, x, y, scale):
    sim.move_pos(t, x, y, scale)


# In[ ]:


#turtle_setup()
#t1 = open_sim("Calibrate")
#calibrate_sim(t1, -750, -400)
#close_sim(t1)


# In[ ]:


def view_dxf(file_path):
    fig, doc, msp, group = dxf.get_dxf(file_path)
    return fig, doc, msp, group


# In[ ]:


def dxf_generate_gcode(file_path, output_path):
    fig, doc, msp, group = view_dxf(file_path)
    dxf.output_all_info(msp, output_path)


# In[ ]:


def png_generate_gcode(file_path, accuracy, output_path):
    instructions = png.naive_to_gcode(png.naive_gcode(file_path, accuracy))
    png.output_gcode(instructions, output_path)


# In[ ]:




