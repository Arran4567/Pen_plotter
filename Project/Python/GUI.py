#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import wx
app = wx.App()
backend = __import__("Integration")


# In[2]:


#Initial setup
t1 = backend.turtle_setup()
home = (0,0)


# In[3]:


#Classes defining the tab panels for the notebook
class TabOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        img = wx.Image(500, 500)
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img))
        
class TabTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.GCODE = wx.TextCtrl(self, style = wx.TE_READONLY | wx.TE_MULTILINE)
        
        bsizer = wx.BoxSizer()
        bsizer.Add(self.GCODE, 1, wx.EXPAND)
        
        self.SetSizerAndFit(bsizer)


# In[4]:


#The dialog that appears when a png or jpg image is chosen
class raterImageDialog(wx.Dialog):

    #Class initialisation
    def __init__(self, *args, **kw):
        super(raterImageDialog, self).__init__(*args, **kw)

        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Rasterized Image Settings")

    #Interface Definition
    def InitUI(self):
        
        #Objects
        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.threshold = wx.TextCtrl(pnl, value = "0.7")
        self.marchSq = wx.RadioButton(pnl, label='Marching Squares (Contour only)',
            style=wx.RB_GROUP)
        self.naive = wx.RadioButton(pnl, label='Naive (Complete Image)')
        okButton = wx.Button(self, wx.ID_OK)
        closeButton = wx.Button(self, label='Close')
        
        #Layout and sizing
        sb = wx.StaticBox(pnl, label='Algorithm')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        sbs.Add(self.marchSq)
        sbs.Add(self.naive)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.StaticText(pnl, id = 1, label ="Black Threshold"))
        hbox1.Add(self.threshold, flag=wx.LEFT, border=5)
        sbs.Add(hbox1)
        pnl.SetSizer(sbs)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)
        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)
        self.SetSizer(vbox)

        #Action when closeButton is pressed
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)
    
    #Function called by closeButton press
    def OnClose(self, e):
        self.Destroy()


# In[5]:


#The main panel of the program
class MainPanel(wx.Panel):
    
    #Panel initialisation
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        #Objects
        self.filepath = wx.TextCtrl(self, value="Filename", size=(500,-1), style = wx.TE_READONLY)
        self.btnOpen =wx.Button(self, label="Open")
        self.Bind(wx.EVT_BUTTON, self.OnOpen, self.btnOpen)
        self.btnCalibrate =wx.Button(self, label="Calibrate")
        self.Bind(wx.EVT_BUTTON, self.OnCalibrate, self.btnCalibrate)
        self.btnPrint =wx.Button(self, label="Print Image")
        self.Bind(wx.EVT_BUTTON, self.OnPrint, self.btnPrint)
        self.btnStop =wx.Button(self, label="Emergency Stop")
        self.Bind(wx.EVT_BUTTON, self.OnStop, self.btnStop)
        self.scale = wx.TextCtrl(self, value = "1", size=(500,-1))
        self.nb = wx.Notebook(self)
        self.tab1 = TabOne(self.nb)
        self.tab2 = TabTwo(self.nb)
        self.nb.AddPage(self.tab1, "Image Preview")
        self.nb.AddPage(self.tab2, "GCODE")

        self.btnStop.Disable()

        #Layout and sizing
        subSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        grid.Add(self.btnOpen, pos=(0,0))
        grid.Add(self.btnCalibrate, pos=(0,1))
        grid.Add(self.btnPrint, pos=(0,2))
        grid.Add(self.btnStop, pos=(0,4))
        grid.Add(wx.StaticText(self, label ="File Path:"), pos=(1,0))
        grid.Add(self.filepath, pos=(2,0), span=(0,5))
        grid.Add(wx.StaticText(self, label ="Scale:"), pos=(3,0))
        grid.Add(self.scale, pos=(4,0), span=(0,5))
        grid.Add(self.nb, pos=(5,0), span=(5,5))
        subSizer.Add(grid, 0, wx.ALL, 5)
        self.SetSizerAndFit(subSizer)
        
        self.calibrated = False
        
    #Defines the actions that are taken when the open button is pressed
    def OnOpen(self,e):
        
        #Retrieves the file path
        self.dirname = ''
        self.filename = ''
        self.file_extension = ''
        wildcard = "DXF files (*.dxf)|*.dxf|JPEG and PNG files (*.jpg;*.png)|*.jpg;*.png"
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", wildcard, wx.FD_OPEN)
        generated = False
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            self.path = self.dirname + "\\" + self.filename
            self.filepath.SetValue(self.dirname + "\\" + self.filename)
            self.file_extension = os.path.splitext(self.path)[1]
            
            #Performs the actions to create the relevant gcode and preview, depending on the extension of the file chosen.
            if self.file_extension.lower() == ".png" or self.file_extension.lower() == ".jpg":
                self.PreviewImage(self, self.path)
                dlgRI = raterImageDialog(None)
                res = dlgRI.ShowModal()
                if res == wx.ID_OK:
                    strThreshold = dlgRI.threshold.GetValue()
                    if strThreshold.replace('.','',1).isdigit():
                        if float(strThreshold) < 1:
                            algorithm = dlgRI.naive.GetValue()
                            threshold = float(dlgRI.threshold.GetValue())
                            backend.png_generate_gcode(self.path, threshold, "output.gcode", algorithm)
                            generated = True
                        else:
                            msg = wx.MessageDialog(self, "Please enter a number between 1 and 0 for the threshold.",'Incorrect scale', wx.OK | wx.ICON_ERROR)
                            msg.ShowModal()
                    else:
                        msg = wx.MessageDialog(self, "Please enter a number between 1 and 0 for the threshold.",'Incorrect scale', wx.OK | wx.ICON_ERROR)
                        msg.ShowModal()
                dlgRI.Destroy()
            elif self.file_extension.lower() == ".dxf":
                print(self.path)
                self.PreviewDXF(self, self.path)
                backend.dxf_generate_gcode(self.path, "output.gcode")
                generated = True
            else:
                print(self.file_extension)
                
            #Calls for the gcode to be previewed if it has been generated
            if generated == True:
                self.PreviewGCODE(self)
                generated = False
                
        dlg.Destroy()
    
    #Displays the preview of an image file in tab one of the notebook
    def PreviewImage(self, e, path):
        filename, file_extension = os.path.splitext(path)
        img_size = 500
        img = wx.Image(path, wx.BITMAP_TYPE_ANY)
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = img_size
            NewH = img_size * H / W
        else:
            NewH = img_size
            NewW = img_size * W / H
        img = img.Scale(NewW,NewH)
        self.tab1.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()
    
    #Displays the preview of a dxf file in tab one of the notebook
    def PreviewDXF(self, e, path):
        backend.view_dxf(path)
        img_size = 500
        img = wx.Image('Images/Outputs/dxf_output.png', wx.BITMAP_TYPE_ANY)
        W = img.GetWidth()
        H = img.GetHeight()
        if W > H:
            NewW = img_size
            NewH = img_size * H / W
        else:
            NewH = img_size
            NewW = img_size * W / H
        img = img.Scale(NewW,NewH)
        self.tab1.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.Refresh()
        
    #Displays the preview of the gcode from "output.gcode" in tab two of the notebook
    def PreviewGCODE(self, e):
        fileGCODE = open("output.gcode", 'r') 
        Lines = fileGCODE.readlines()
        string_lines = ""
        for line in Lines:
            string_lines = string_lines + line
        self.tab2.GCODE.WriteText(string_lines)
        
    #Defines what happens when the calibrate button is pressed
    def OnCalibrate(self, e):
        dlg = wx.MessageDialog(self, "Are you sure you want to calibrate the simulation home position?",'Calibrate?',wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            frame = CalibrationWindow(None, "Calibrate")
            parent=wx.GetTopLevelParent(self)
            parent.Show(False)
            frame.SetFocus()
            frame.Raise()
        else:
            print("No pressed")
            
    #Defines what happens when the print button is pressed
    def OnPrint(self, e):
        if self.scale.GetValue().replace('.','',1).isdigit() and float(self.scale.GetValue()) > 0:
            t1 = backend.open_sim("Click to close when simulation finishes.")
            self.btnStop.Enable()
            close = backend.draw_output(t1, "output.gcode", float(self.scale.GetValue()))
            if close:
                self.btnStop.Disable()
        else:
            dlg = wx.MessageDialog(self, "Please enter a positive integer for the scale.",'Incorrect scale', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
    
    #Defines what happens when the stop button is pressed
    def OnStop(self, e):
        backend.stop_sim()
        self.btnStop.Disable()


# In[6]:


#The main window of the project
class MainWindow(wx.Frame):

    def __init__(self, parent, title):
        self.dirname=''
        
        #Objects
        self.frame = wx.Frame.__init__(self, parent, title=title, size=(500,-1))
        self.CreateStatusBar()
        self.panel = MainPanel(self)
        filemenu= wx.Menu()
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file")
        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)
        
        #Calls the relevant function when corresponding buttons are pressed
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        #layout and sizing
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.panel)
        self.SetSizerAndFit(mainSizer)
        self.Show(True)
    
    #Defines what happens when the open menu item is pressed
    def OnOpen(self,e):
        self.panel.OnOpen(e)
        
    #Defines what happens when the about menu item is pressed
    def OnAbout(self,e):
        dlg = wx.MessageDialog( self, "This program was created as an MSc dissertation. " +
                            "It can convert PNG, JPEG & DXF files into GCODE and then create a 2D print from the GCODE.")
        dlg.ShowModal()
        dlg.Destroy()

    #Defines what happens when the exit menu item is pressed
    def OnExit(self,e):
        self.Close(True)  # Close the frame.


# In[7]:


#The panel for the calibration window
class CalibrationPanel(wx.Panel):
    def __init__(self, parent):
        
        #Initial setup
        wx.Panel.__init__(self, parent)
        self.t1 = backend.open_sim("Calibrate")
        global home
        backend.move_turtle(self.t1, home[0], home[1], 1)
        
        #Objects
        self.lblX = wx.StaticText(self, wx.ID_ANY, label="Home x value:", style=wx.ALIGN_CENTER)
        self.txtXCoord = wx.TextCtrl(self, value=str(home[0]), size=(100,-1))
        self.lblY = wx.StaticText(self, wx.ID_ANY, label="Home Y value:", style=wx.ALIGN_CENTER)
        self.txtYCoord = wx.TextCtrl(self, value=str(home[1]), size=(100,-1))
        self.btnCalibrate =wx.Button(self, label="Set home")
        self.Bind(wx.EVT_BUTTON, self.OnCalibrate, self.btnCalibrate)
        self.btnExit =wx.Button(self, label="Done")
        self.Bind(wx.EVT_BUTTON, self.OnExit, self.btnExit)

        #Layout and sizing
        subSizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridBagSizer(hgap=5, vgap=5)
        grid.Add(self.lblX, pos=(0,0))
        grid.Add(self.txtXCoord, pos=(0,1))
        grid.Add(self.lblY, pos=(0,2))
        grid.Add(self.txtYCoord, pos=(0,3))
        grid.Add(self.btnCalibrate, pos=(1,1))
        grid.Add(self.btnExit, pos=(1,3))
        subSizer.Add(grid, 0, wx.ALL, 5)
        self.SetSizerAndFit(subSizer)
        
    #Defines what happens when the calibrate button is pressed
    def OnCalibrate(self,e):
        if self.txtXCoord.GetValue().replace('-','',1).isdigit() and self.txtYCoord.GetValue().replace('-','',1).isdigit():
            xCoord = int(self.txtXCoord.GetValue())
            yCoord = int(self.txtYCoord.GetValue())
            backend.calibrate_sim(self.t1, xCoord, yCoord)
            global home
            home = (xCoord,yCoord)
        else:
            dlg = wx.MessageDialog(self, "Please enter an integer for the x and y values.",'Incorrect value', wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            
    #Defines what happens when the exit button is pressed
    def OnExit(self,e):
        dlg = wx.MessageDialog(self, "Any changes since confirming calibration by pressing 'Set Home' will be lost. \n" + 
                               "Are you sure you're done calibrating the simulation home position?",
                               'Calibrated?',wx.YES_NO | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        if result == wx.ID_YES:
            backend.close_sim(self.t1)
            mainFrame.Show(True)
            parent=wx.GetTopLevelParent(self)
            parent.Close(True)  # Close the frame.
        else:
            print("No pressed")


# In[8]:


#The window for the calibration page
class CalibrationWindow(wx.Frame):

    def __init__(self, parent, title):
        self.dirname=''
        self.frame = wx.Frame.__init__(self, parent, title=title, size=(500,-1), style=wx.CAPTION)
        self.CreateStatusBar()
        
        #Creates panel
        panel = CalibrationPanel(self)
        
        #Layout and sizing
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(panel)
        self.SetSizerAndFit(mainSizer)
        self.Show(True)


# In[9]:


#Sets up the GUI and starts the MainLoop to open it
mainFrame = MainWindow(None, "2D Plotter")
mainFrame.CenterOnScreen()
mainFrame.SetFocus()
mainFrame.Raise()
app.MainLoop()


# In[ ]:




