import tkinter as tk # The python tcl/tk ui construction api

# Module to build the user interface for colour setting

# Global variables to hold the current colour values
red = 0
green = 0
blue = 0
changeHandler = None
    
# To create a window to hold control buttons
top = tk.Tk() # The tcl/tk object
left = tk.Frame(top, background='red')
left.pack(side='left')
middle = tk.Frame(top, background='green')
middle.pack(side='left')
right = tk.Frame(top, background='blue')
right.pack(side='left')

# Make buttons for the red column
redUp10=tk.Button(left,text='Up 10', width=6)
redUp10.pack(side='top', padx=6, pady=6)
redUp1=tk.Button(left,text='Up', width=6)
redUp1.pack(side='top', padx=6, pady=6)
redLabel = tk.Label(left,  text='99', width=6, fg='white', background='red')
redLabel.pack(side='top', padx=6, pady=6)
redDown1=tk.Button(left,text='Down', width=6)
redDown1.pack(side='top', padx=6, pady=6)
redDown10=tk.Button(left,text='Down 10', width=6)
redDown10.pack(side='top', padx=6, pady=6)

# Make buttons for the green column
greenUp10=tk.Button(middle,text='Up 10', width=6)
greenUp10.pack(side='top', padx=6, pady=6)
greenUp1=tk.Button(middle,text='Up', width=6)
greenUp1.pack(side='top', padx=6, pady=6)
greenLabel = tk.Label(middle,  text='99', width=6, fg='white', background='green')
greenLabel.pack(side='top', padx=6, pady=6)
greenDown1=tk.Button(middle,text='Down')
greenDown1.pack(side='top', padx=6, pady=6)
greenDown10=tk.Button(middle,text='Down 10', width=6)
greenDown10.pack(side='top', padx=6, pady=6)

# Make buttons for the blue column
blueUp10=tk.Button(right,text='Up 10', width=6)
blueUp10.pack(side='top', padx=6, pady=6)
blueUp1=tk.Button(right,text='Up', width=6)
blueUp1.pack(side='top', padx=6, pady=6)
blueLabel = tk.Label(right,  text='99', width=6, fg='white', background='blue')
blueLabel.pack(side='top', padx=6, pady=6)
blueDown1=tk.Button(right,text='Down', width=6)
blueDown1.pack(side='top', padx=6, pady=6)
blueDown10=tk.Button(right,text='Down 10', width=6)
blueDown10.pack(side='top', padx=6, pady=6)

# Update function to be called when colour values may have changed
def updateColours():
    global red, green, blue
    global top, redLabel, greenLabel, blueLabel
    global changeHandler
    if red < 0:
        red = 0
    if red > 100:
        red = 100
    redLabel.config(text = str(red))
    if green < 0:
        green = 0
    if green > 100:
        green = 100
    greenLabel.config(text = str(green))
    if blue < 0:
        blue = 0
    if blue > 100:
        blue = 100
    blueLabel.config(text = str(blue))
    top.update()
    # Call change handler if registered
    if changeHandler:
      changeHandler(red, green, blue)

# Handler functions for button presses
def changeRed(delta):
  global red;
  red = red + delta;
  updateColours()

def changeGreen(delta):
  global green;
  green = green + delta;
  updateColours()

def changeBlue(delta):
  global blue;
  blue = blue + delta;
  updateColours()

# Attach handlers to buttons
redUp10.configure(command = lambda: changeRed(10))
redUp1.configure(command = lambda: changeRed(1))
redDown10.configure(command = lambda: changeRed(-10))
redDown1.configure(command = lambda: changeRed(-1))
greenUp10.configure(command = lambda: changeGreen(10))
greenUp1.configure(command = lambda: changeGreen(1))
greenDown10.configure(command = lambda: changeGreen(-10))
greenDown1.configure(command = lambda: changeGreen(-1))
blueUp10.configure(command = lambda: changeBlue(10))
blueUp1.configure(command = lambda: changeBlue(1))
blueDown10.configure(command = lambda: changeBlue(-10))
blueDown1.configure(command = lambda: changeBlue(-1))

# Functions to set and get colour values
def setUIColours(r, g, b):
  global red, blue, green
  red = r
  blue = b
  green = g
  updateColours()

def getUIColours():
  global red, blue, green
  return [red, green, blue]

# Function to set change handler
def setUIHandler(h):
  global changeHandler
  changeHandler = h;

def waitForInput():
  global top
  top.mainloop()

# Start with GUI set correctly
updateColours()
