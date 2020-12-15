#!/usr/bin/env python
# coding: utf-8

# # Library Imports

# In[1]:


import ezdxf #ezdxf v0.13
import matplotlib.pyplot as plt
from ezdxf.addons.drawing.matplotlib_backend import MatplotlibBackend
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.groupby import groupby
from pygcode import * #pygcode v0.2.1


# # Import DXF File and Create Image

# In[2]:


def get_dxf(file_loc):
    
    #Reads in the dxf file
    doc = ezdxf.readfile(file_loc)
    msp = doc.modelspace()
    group = groupby(entities=msp, dxfattrib='layer')
    
    #Produces a preview image
    layout = doc.layouts.get('Model')
    figure = plt.figure()
    axis = fig.add_axes([0, 0, 1, 1])
    context = RenderContext(doc)
    output = MatplotlibBackend(ax)
    Frontend(context, output).draw_layout(layout, finalize=True)
    output.finalize()
    figure.savefig('Images/Outputs/dxf_output.png', dpi=600)
    
    return fig, doc, msp, group


# In[3]:


#fig, doc, msp, group = get_dxf("DXF/frame.dxf")


# # Print DXF Entities

# In[4]:


#Print statements to help understand the outputs of ezdxf
def print_line(e):
    print("LINE:")
    print("start point: %s" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)


# In[5]:


#Print statements to help understand the outputs of ezdxf
def print_arc(e):
    print("ARC:")
    print("start point: %s" % e.start_point)
    print("end point: %s" % e.end_point)
    print("start angle: %s" % e.dxf.start_angle)
    print("end angle: %s" % e.dxf.end_angle)
    print("radius: %s\n" % e.dxf.radius)


# In[6]:


#Print statements to help understand the outputs of ezdxf
def print_circle(e):
    print("Circle:")
    print("centre point: %s" % e.dxf.center)
    print("radius: %s\n" % e.dxf.radius)


# In[7]:


#Print statements to help understand the outputs of ezdxf
def print_poly(e):
    print("POLYLINE:")
    print("THIS POLYLINE CONTAINS:\n")
    for entity in e.virtual_entities():
        if entity.dxftype() == 'LINE':
            print_line(entity)
        elif entity.dxftype() == 'ARC':
            print_arc(entity)
        else:
            print("Unknown entity")
    print('-'*40)


# In[8]:


#Print statements to help understand the outputs of ezdxf
def list_entities(group):
    for layer, entities in group.items():
        print(f'Layer "{layer}" contains following entities:')
        for entity in entities:
            print('    {}'.format(str(entity)))
        print('-'*40)


# In[9]:


#list_entities(group)


# In[10]:


#Print statements to help understand the outputs of ezdxf
def print_all_info(msp):
    for e in msp:
        if e.dxftype() == 'LINE':
            print_line(e)
        elif e.dxftype() == 'ARC':
            print_arc(e)
        elif e.dxftype() == 'CIRCLE':
            print_circle(e)
        elif e.dxftype() == 'POLYLINE':
            print_poly(e)
        else:
            print("Unknown entity")


# In[11]:


#print_all_info(msp)


# # Convert Entities to GCODE

# In[12]:


#Converts a dxf LINE entity to gcode instructions
def line_to_gcode(e):
    x_start = e.dxf.start[0]
    y_start = e.dxf.start[1]
    x_end = e.dxf.end[0]
    y_end = e.dxf.end[1]
    gcode = [
        GCodeRapidMove(X=x_start,Y=y_start),
        GCodeLinearMove(X=x_end,Y=y_end),
    ]
    return gcode


# In[13]:


#Converts a dxf ARC entity to gcode instructions
def arc_to_gcode(e):
    x_start = str(e.start_point[0])
    y_start = str(e.start_point[1])
    a_start = str(e.dxf.start_angle)
    a_end = str(e.dxf.end_angle)
    radius = str(e.dxf.radius)
    gcode = [
        "G03 R " + radius + " X" + x_start + " Y" + y_start + " S" + a_start + " E" + a_end,
    ]
    return gcode


# In[14]:


#Converts a dxf CIRCLE entity to gcode instructions
def circle_to_gcode(e):
    x_center = e.dxf.center[0]
    y_center = e.dxf.center[1]
    radius = e.dxf.radius
    
    x_start = x_center
    y1_start = x_center - radius
    y2_start = y_center + radius
    
    gcode = [
        GCodeRapidMove(X=x_start,Y=y1_start),
        "G03 R " + str(radius) + " X" + str(x_start) + " Y" + str(y1_start) + " S-90" +" E90",
        "G03 R " + str(radius) + " X" + str(x_start) + " Y" + str(y2_start) + " S90" +" E270",
    ]
    return gcode


# In[15]:


#Converts a dxf POLYLINE entity to gcode instructions
def poly_to_gcode(e):
    gcodes =[]
    for entity in e.virtual_entities():
        if entity.dxftype() == 'LINE':
            gcode = line_to_gcode(entity)
            for g in gcode:
                gcodes.append(str(g))
        elif entity.dxftype() == 'ARC':
            gcode = arc_to_gcode(entity)
            for g in gcode:
                gcodes.append(str(g))
        else:
            print("Unknown entity")
    return gcodes


# # Ouput all GCODE to file

# In[16]:


#Loops through all entities in the dxf file and converts each entity to the corresponding gcode instructions
#The gcode is then saved to an output file
def output_all_info(msp, filename):
    all_instructions = []
    gcodes = []
    for e in msp:
        if e.dxftype() == 'LINE':
            gcode = line_to_gcode(e)
            for g in gcode:
                all_instructions.append(str(g))
        elif e.dxftype() == 'ARC':
            gcode = arc_to_gcode(e)
            for g in gcode:
                all_instructions.append(str(g))
        elif e.dxftype() == 'CIRCLE':
            gcode = circle_to_gcode(e)
            for g in gcode:
                all_instructions.append(str(g))
        elif e.dxftype() == 'POLYLINE':
            gcodes = poly_to_gcode(e)
            all_instructions.extend(gcodes)
        else:
            print("Unknown entity")
    File_object = open(filename,"w")
    for gcode in all_instructions:
        print(gcode)
        File_object.write(gcode + ";\n")
    File_object.close()


# In[17]:


#output_all_info(msp, "output3.gcode")


# In[ ]:





# In[ ]:




