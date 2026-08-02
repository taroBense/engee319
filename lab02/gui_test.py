import tkinter
from tkinter import PhotoImage
from tkinter.ttk import *


colour_b = "red"
# build GUI here:
# main window
window = tkinter.Tk()

mic = PhotoImage(file="mic.png")
mic = mic.subsample(10, 10)

# frames, top and bottom
input_frame = tkinter.Frame(window)
input_frame.pack(side="top")
output_frame = tkinter.Frame(window)
output_frame.pack(side="bottom")

# input frame content
instruction_label = tkinter.Label(input_frame,
    text="Press buttton to record:")
instruction_label.pack(side="top")

record_button = tkinter.Button(input_frame,
    text="Record",
    image=mic,
    compound="left"
    )
record_button.pack(side="bottom")

record_button.image = mic

# output frame content
bulb_label = tkinter.Label(output_frame,
    text=f"bulb colour: {colour_b}")
bulb_label.pack(side="bottom")

# generate GUI
window.mainloop()