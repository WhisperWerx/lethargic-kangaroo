#-----------------------------------------------------------------------------------
# #######   ######  ## ## ## ######## #######
# ##    ## ##    ## ## ## ## ##       ##    ##
# #######  ##    ## ## ## ## #####    #######
# ##       ##    ## ## ## ## ##       ##   ##
# ##        ######   ######  ######## ##    ##
#
# #######  #######   ######  ######## ######## ##       ######## #######
# ##    ## ##    ## ##    ## ##          ##    ##       ##       ##    ##
# #######  #######  ##    ## #####       ##    ##       #####    #######
# ##       ##   ##  ##    ## ##          ##    ##       ##       ##   ##
# ##       ##    ##  ######  ##       ######## ######## ######## ##    ##
#
# ##    ##    ###     ######
# ##    ##   ####    ##    ##
# ##   ##      ##    ##    ##
# ##  ##       ## ## ##    ##
# #####        ## ##  ######
#-----------------------------------------------------------------------------------

# Tkinter is a library for creating GUIs comprisode of wdigets
from tkinter import *

# The serial library is used for establishing connections between the PC and a 
# device connected via COM port
import serial
import serial.tools.list_ports

# Numpy is a library for easy file access
import numpy

# Matplot lib is a library for plotting data
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.animation as animation


		

# Instantiate the main window
root = Tk()
root.title('Power Profiler')
root.geometry('1000x750')

#-----------------------------------------------------------------------------------
# CONNECTION FRAME
# This frame contains a OptionsMenu with available COM ports, one of which should
# be the Arduino used to drive the system. 
#-----------------------------------------------------------------------------------

# Instatiate the serial connection
ser = serial.Serial()
ser.baudrate = 9600
ser.timeout = 10

port = StringVar()	#Tkinter variable for the menu
ports = []			#List for the menu options
#Populate list of ports
for comport in serial.tools.list_ports.comports():
	# Lists are indexed and unsorted, the append function adds
	# a new item to the end of the list
	ports.append(comport)
port.set(ports[0])

def connectPort():
	global ser
	global port
	space = port.get().find(' ')
	ser.port = port.get()[0:space]
	print(ser.port)

def refreshMenu(container, menu, button1, button2):
	global port
	global ports
	menu.destroy()
	button1.destroy()
	button2.destroy()
	
	# Create a list that contains all devices connected via COM port
	ports = []
	for comport in serial.tools.list_ports.comports():
		ports.append(comport)

	port.set(ports[0])
	menu = OptionMenu(container, port, *ports)
	menu.config(width="75")
	button2 = Button(container, text='Connect',  width = '10', command=lambda: connectPort())
	button1 = Button(container, text='Refresh',  width = '10', command=lambda: refreshMenu(container, menu, button1, button2))
	
	menu.grid(row = 0, column = 0, sticky = 'ew')
	button1.grid(row = 0, column = 1)
	button2.grid(row = 0, column = 2)

# Instantiate the connection pane
def updateConnection():
	connection = Frame(root, padx = 5, pady = 5, borderwidth = 2, relief = RIDGE)
	menu_Ports = OptionMenu(connection, port, *ports)
	menu_Ports.config(width="75")
	btn_Refresh = Button(connection, text='Refresh', width = '10', padx = 5, pady = 2, command=lambda: refreshMenu(connection, menu_Ports, btn_Refresh, btn_Connect))
	btn_Connect = Button(connection, text='Connect', width = '10', padx = 5, pady = 2, command=lambda: connectPort())

	menu_Ports.grid(row = 0, column = 0, sticky = 'ew')
	btn_Refresh.grid(row = 0, column = 1)
	btn_Connect.grid(row = 0, column = 2)
	connection.pack(side = TOP, fill = BOTH, expand = 1)
	return connection

#-----------------------------------------------------------------------------------
# GRAPH 
# The graph is self contained and doesnt need a container.
#-----------------------------------------------------------------------------------

#f = Figure(figsize=(5,5), dpi=100)
#a = f.add_subplot(111)
#a.plot([1,2,3,4,5,6,7,8],[5,7,6,9,1,4,3,2])

#canvas = FigureCanvasTkAgg(f, root)
#canvas.draw()
#canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
# canvas.get_tk_widget().grid(row=0, column=0, sticky='ew')

#toolbar = NavigationToolbar2Tk(canvas, root)
#toolbar.update()
#canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
# canvas.get_tk_widget().grid(row=0, column=0, sticky='ew')

#-----------------------------------------------------------------------------------
# STATUS FRAME
# The status frame contains a read out of instantaneous and average values
# read from the Arduino.
#-----------------------------------------------------------------------------------

# Instantiate the status pane
def updateStatus():
	status = Frame(root, padx=5, pady=5, borderwidth = 2, relief = RIDGE, width="200")
	l_status = Label(status, text='Average Values', font = ("Helvetica", 12))
	l_voltage = Label(status, text='Avg V(V):', font = ("Helvetica", 24), fg = 'maroon')
	l_avgI = Label(status, text='Avg I(mA):', font = ("Helvetica", 24), fg = 'maroon')
	l_avgP = Label(status, text='Avg P(mW):', font = ("Helvetica", 24), fg = 'maroon')
	l_t = Label(status, text='Time(s):', font = ("Helvetica", 24), fg = 'maroon')

	l_vRead = Label(status, text=10, justify=RIGHT)
	l_iRead = Label(status, text=100, justify=RIGHT)
	l_pCalc = Label(status, text=0.01, justify=RIGHT)
	l_tRead = Label(status, text=0, justify=RIGHT)

	# Pack the status pane
	l_status.grid(row = 0, column = 0, sticky='e')
	l_voltage.grid(row = 1, column = 0, sticky='w')
	l_avgI.grid(row = 1, column = 2, sticky='w')
	l_avgP.grid(row = 2, column = 0, sticky='w')
	l_t.grid(row = 2, column = 2, sticky='w')

	l_vRead.grid(row = 1, column = 1, sticky='e')
	l_iRead.grid(row = 1, column = 3, sticky='e')
	l_pCalc.grid(row = 2, column = 1, sticky='e')
	l_tRead.grid(row = 2, column = 3, sticky='e')
	return status

#-----------------------------------------------------------------------------------
# CONTROL FRAME
# The Control Frame works in conjunction with the Graph Frame. The axis divisions,
# plots, and units are all set in the Control Frame. The start button is also found
# in the control frame (I think its purpose is self explanatory).
#-----------------------------------------------------------------------------------
def updateControl():
	# Instantiate tkinter variables for checkboxes
	# For (en/dis)abling plots
	plotV = IntVar()
	plotI = IntVar()
	plotP = IntVar()
	# For adjusting major divisions of the x & y axis 
	divV = IntVar()
	divI = IntVar()
	divP = IntVar()
	divT = IntVar()
	# For setting the units per division
	Vupd = IntVar()
	Iupd = IntVar()
	Pupd = IntVar()
	Tupd = IntVar()
	# For setting the unit magnitude
	unitV = StringVar()
	unitI = StringVar()
	unitP = StringVar()
	unitT = StringVar()

	# Create a list that the tkinter variables will draw a value from
	divisions = [5,10,20]					#Number of major divisions
	unitsPerDivision = [1,5,10,20,50,100]	#Units per major division
	unitsV = ['V','mV']						#Voltage units
	unitsI = ['A','mA','uA']				#Current units
	unitsP = ['W','mW','uW']				#Power units
	unitsT = ['s','ms','us']				#Time units

	# Set tkinter variables
	plotV.set(0)
	plotI.set(1)
	plotP.set(0)

	# Instantiate the control pane
	ctrl = Frame(root, padx=5, pady=5, borderwidth = 2, relief = RIDGE, width="150")

	# Instantiate check boxes for enabling different plots
	check_V = Checkbutton(ctrl, variable=plotV)
	check_I = Checkbutton(ctrl, variable=plotI)
	check_P = Checkbutton(ctrl, variable=plotP)

	# Instantiate all the text needed in the box
	label_plot = Label(ctrl, text='Plot')
	label_unit = Label(ctrl, text='Unit')
	label_div = Label(ctrl, text='# Divisions')
	label_upd = Label(ctrl, text='Units / Div')
	label_V = Label(ctrl, text='Voltage')
	label_I = Label(ctrl, text='Current')
	label_P = Label(ctrl, text='Power')
	label_T = Label(ctrl, text='Time')
	label_port = Label(ctrl, text='COM Port')

	#instatiate the unit selection menus
	menu_unitV = OptionMenu(ctrl, unitV, *unitsV)
	menu_unitI = OptionMenu(ctrl, unitI, *unitsI)
	menu_unitP = OptionMenu(ctrl, unitP, *unitsP)
	menu_unitT = OptionMenu(ctrl, unitT, *unitsT)
	menu_unitV.config(width=3)
	menu_unitI.config(width=3)
	menu_unitP.config(width=3)
	menu_unitT.config(width=3)
	unitV.set(unitsV[0])	# Default voltage unit is V
	unitI.set(unitsI[1])	# Default current unit is mA
	unitP.set(unitsP[0])	# Default power unit is W
	unitT.set(unitsT[0])	# Default time unit is s

	menu_Vdiv = OptionMenu(ctrl, divV, *divisions)
	menu_Idiv = OptionMenu(ctrl, divI, *divisions)
	menu_Pdiv = OptionMenu(ctrl, divP, *divisions)
	menu_Tdiv = OptionMenu(ctrl, divT, *divisions)
	menu_Vdiv.config(width=3)
	menu_Idiv.config(width=3)
	menu_Pdiv.config(width=3)
	menu_Tdiv.config(width=3)
	divV.set(divisions[0])	# Default divisions = 5
	divI.set(divisions[0])	# Default divisions = 5
	divP.set(divisions[0])	# Default divisions = 5
	divT.set(divisions[0])	# Default divisions = 5

	menu_Vupd = OptionMenu(ctrl, Vupd, *unitsPerDivision)
	menu_Iupd = OptionMenu(ctrl, Iupd, *unitsPerDivision)
	menu_Pupd = OptionMenu(ctrl, Pupd, *unitsPerDivision)
	menu_Tupd = OptionMenu(ctrl, Tupd, *unitsPerDivision)
	menu_Vupd.config(width=3)
	menu_Iupd.config(width=3)
	menu_Pupd.config(width=3)
	menu_Tupd.config(width=3)
	Vupd.set(unitsPerDivision[0])	# Default units/division = 1
	Iupd.set(unitsPerDivision[5])	# Default units/division = 100
	Pupd.set(unitsPerDivision[0])	# Default units/division = 1
	Tupd.set(unitsPerDivision[0])	# Default units/division = 1

	#menu_ports = OptionMenu(ctrl, port, *ports, lambda: command = setPort(port.get()))
	#menu_ports.config(width=75)
	#port.set(ports[0])

	btn_Start = Button(ctrl, text='Start', width = '5')

	# Place widgets in the control frame
	label_plot.grid(row=0, column=0)
	check_V.grid(row = 1, column = 0)
	check_I.grid(row = 2, column = 0)
	check_P.grid(row = 3, column = 0)

	label_V.grid(row = 1, column = 1)
	label_I.grid(row = 2, column = 1)
	label_P.grid(row = 3, column = 1)
	label_T.grid(row = 4, column = 1)

	label_unit.grid(row=0, column=2)
	menu_unitV.grid(row=1, column=2, sticky='ew')
	menu_unitI.grid(row=2, column=2, sticky='ew')
	menu_unitP.grid(row=3, column=2, sticky='ew')
	menu_unitT.grid(row=4, column=2, sticky='ew')

	label_div.grid(row = 0, column = 3)
	menu_Vdiv.grid(row = 1, column = 3, sticky='ew')
	menu_Idiv.grid(row = 2, column = 3, sticky='ew')
	menu_Pdiv.grid(row = 3, column = 3, sticky='ew')
	menu_Tdiv.grid(row = 4, column = 3, sticky='ew')

	label_upd.grid(row = 0, column = 4)
	menu_Vupd.grid(row = 1, column = 4, sticky='ew')
	menu_Iupd.grid(row = 2, column = 4, sticky='ew')
	menu_Pupd.grid(row = 3, column = 4, sticky='ew')
	menu_Tupd.grid(row = 4, column = 4, sticky='ew')

	#label_port.grid(row = 0, column = 5)
	#menu_ports.grid(row = 1, column = 5, sticky='ew')

	btn_Start.grid(row = 1, column = 5, rowspan = 4, padx = 2, sticky='nsew')
	return ctrl
#-----------------------------------------------------------------------------------

# Place widgets
# bar.grid(row = 0, column = 0, padx = 5, pady = 5, rowspan=2, sticky='nsew')
#status.grid(row = 0, column = 1, padx = 5, pady = 5,sticky='nsew')
#ctrl.grid(row = 1, column = 1, padx = 5, pady = 5,sticky='nsew')

connect = updateConnection()

#-----------------------------------------------------------------------------------
# GRAPH 
# The graph is self contained and doesnt need a container.
#-----------------------------------------------------------------------------------

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)
xs = []		#Time 
yv = []		#Voltage
#a.plot([1,2,3,4,5,6,7,8],[5,7,6,9,1,4,3,2])

canvas = FigureCanvasTkAgg(f, root)
canvas.draw()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
# canvas.get_tk_widget().grid(row=0, column=0, sticky='ew')

def animate(i, xs, ys):
	line = ser.readline()
	line_as_list = line.split(b',')
	i = int(line_as_list[0])
	voltage = line_as_list[1]
	voltage_as_list = voltage.split(b'\n')
	volt_float = float(voltage_as_list[0])
	
	xs.append(i)
	yv.append(volt_float)
	
	a.clear()
	a.plot(xs, ys, label="Voltage vs. Time")
	
	

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
# canvas.get_tk_widget().grid(row=0, column=0, sticky='ew')

status = updateStatus()
control = updateControl()

control.pack(side=RIGHT, fill=BOTH, expand=1)
status.pack(side=RIGHT, fill=BOTH, expand=1)



root.mainloop()