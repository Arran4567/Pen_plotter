#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Imports the functions from the specified files
png = __import__("PNG_to_GCODE")
dxf = __import__("DXF_to_GCODE")
sim = __import__("Simulation")


# In[2]:


#Initial turtle setup
def turtle_setup():
    t1 = sim.create_turtle()
    sim.close_sim(t1)
    return t1


# In[3]:


#t1 = turtle_setup()


# In[6]:


#Reopens the environment after it's been closed
def open_sim(title):
    t = sim.resurrect_environment(title)
    return t


# In[7]:


#Closes the environment
def close_sim(t):
    sim.close_sim(t)


# In[8]:


#Sets the home location of the turtle
def calibrate_sim(t, x, y):
    sim.set_home(t, x, y)


# In[9]:


#Moves the turtle to the specified co-ordinates without drawing
def move_turtle(t, x, y, scale):
    sim.move_pos(t, x, y, scale)


# In[10]:


#Moves the turtle to the specified co-ordinates while drawing
def draw_output(t, gcode, scale):
    sim.convert_gcode(t, gcode, scale)
    return True


# In[11]:


#t1 = open_sim("Calibrate")
#calibrate_sim(t1, -750, -400)
#close_sim(t1)


# In[12]:


#Generates a preview of the specified dxf file
def view_dxf(file_path):
    fig, doc, msp, group = dxf.get_dxf(file_path)
    return fig, doc, msp, group


# In[13]:


#Generates gcode from the specified dxf file
def dxf_generate_gcode(file_path, output_path):
    fig, doc, msp, group = view_dxf(file_path)
    dxf.output_all_info(msp, output_path)


# In[14]:


#Generates gcode from the specified image file
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


#Sets the stop global variable in simulation to true
def stop_sim():
    sim.set_stop(True)

