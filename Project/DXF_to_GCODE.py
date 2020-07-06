#!/usr/bin/env python
# coding: utf-8

# # Library Imports

# In[1]:


import ezdxf
import matplotlib.pyplot as plt
from ezdxf.addons.drawing.matplotlib_backend import MatplotlibBackend
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.groupby import groupby
from pygcode import *


# # Import DXF File and Create Image

# In[2]:


def get_dxf(file_loc):
    doc = ezdxf.readfile(file_loc)
    msp = doc.modelspace()
    group = groupby(entities=msp, dxfattrib='layer')
    
    layout = doc.layouts.get('Model')
    fig = plt.figure()
    ax = fig.add_axes([0, 0, 1, 1])
    ctx = RenderContext(doc)
    out = MatplotlibBackend(ax)
    Frontend(ctx, out).draw_layout(layout, finalize=True)
    plt.show()
    out.finalize()
    fig.savefig('output.png', dpi=300)
    
    return doc, msp, group


# In[3]:


#doc, msp, group = get_dxf("DXF/knot_005.dxf")


# # Print DXF Entities

# In[4]:


def print_line(e):
    print("LINE:")
    print("start point: %s" % e.dxf.start)
    print("end point: %s\n" % e.dxf.end)


# In[5]:


def print_arc(e):
    print("ARC:")
    print("start point: %s" % e.start_point)
    print("end point: %s" % e.end_point)
    print("start angle: %s" % e.dxf.start_angle)
    print("end angle: %s" % e.dxf.end_angle)
    print("radius: %s\n" % e.dxf.radius)


# In[6]:


def print_circle(e):
    print("Circle:")
    print("centre point: %s" % e.dxf.center)
    print("radius: %s\n" % e.dxf.radius)


# In[7]:


def print_poly(e):
    print("POLYLINE:")
    print("THIS POLYLINE CONTAINS:\n")
    for entity in e.virtual_entities():
        if entity.dxftype() == 'LINE':
            print_line(entity)
        elif entity.dxftype() == 'ARC':
            print_arc(entity)
    print('-'*40)


# In[8]:


def list_entities(group):
    for layer, entities in group.items():
        print(f'Layer "{layer}" contains following entities:')
        for entity in entities:
            print('    {}'.format(str(entity)))
        print('-'*40)


# In[9]:


#list_entities(group)


# In[10]:


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


# In[11]:


#print_all_info(msp)


# # Convert Entities to GCODE

# In[12]:


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


def arc_to_gcode(e):
    x_start = e.start_point[0]
    y_start = e.start_point[1]
    x_end = e.end_point[0]
    y_end = e.end_point[1]
    radius = e.dxf.radius
    gcode = [
        GCodeRapidMove(X=x_start,Y=y_start),
        GCodeArcMoveCCW(X=x_end,Y=y_end, R=radius),
    ]
    return gcode


# In[14]:


def circle_to_gcode(e):
    x_center = e.dxf.center[0]
    y_center = e.dxf.center[1]
    radius = e.dxf.radius
    
    x_start = x_center
    y1_start = x_center + radius
    
    x1_end = x_center
    y1_end = x_center - radius
    
    x2_end = x_center
    y2_end = y1_start
    
    gcode = [
        GCodeRapidMove(X=x_start,Y=y1_start),
        GCodeArcMoveCCW(X=x1_end,Y=y1_end, R=radius),
        GCodeArcMoveCCW(X=x2_end,Y=y2_end, R=radius),
    ]
    return gcode


# In[15]:


def poly_to_gcode(e):
    gcodes =[]
    for entity in e.virtual_entities():
        if entity.dxftype() == 'LINE':
            gcode = line_to_gcode(entity)
            for g in gcode:
                gcodes.append(str(g))
        if entity.dxftype() == 'ARC':
            gcode = arc_to_gcode(entity)
            for g in gcode:
                gcodes.append(str(g))
    return gcodes


# # Ouput all GCODE to file

# In[16]:


def output_all_info(msp, filename):
    all_instructions = []
    gcodes = []
    for e in msp:
        if e.dxftype() == 'LINE':
            gcode = line_to_gcode(e)
            for g in gcode:
                all_instructions.append(str(g))
        if e.dxftype() == 'ARC':
            gcode = arc_to_gcode(e)
            for g in gcode:
                all_instructions.append(str(g))
        if e.dxftype() == 'CIRCLE':
            gcode = circle_to_gcode(e)
            for g in gcode:
                all_instructions.append(str(g))
        if e.dxftype() == 'POLYLINE':
            gcodes = poly_to_gcode(e)
            all_instructions.extend(gcodes)
    
    File_object = open(filename,"w")
    for gcode in all_instructions:
        print(gcode)
        File_object.write(gcode + " ;\n")
    File_object.close()


# In[17]:


#output_all_info(msp, "output.gcode")


# In[ ]:





# In[ ]:




