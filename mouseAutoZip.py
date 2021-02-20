import time
import mouse
import keyboard
from typing import NamedTuple

class MouseEvent():
    def __init__(self):
        self.events = [] #This is the list where all the events will be stored
    def start_record(self):
        self.events = [] # init list
        mouse.hook(self.events.append) #starting the mouse recording
    def stop_record(self):
        mouse.unhook(self.events.append) #Stopping the mouse recording
    def replay(self):
        mouse.play(self.events) #Playing the recorded events
    def saveEvents(self,file_name):
        open_file = open(file_name,"wb")
        pickle.dump(self.events,open_file)
        open_file.close()
    def loadEvents(self,file_name):
        open_file = open(file_name,"rb")
        self.events = pickle.load(open_file)
        open_file.close()

import tkinter as tk
from tkinter import filedialog
import pickle

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.mouse_events = MouseEvent()
        self.compressed_events =[]
        self.create_widgets()

    def create_widgets(self):
        self.rcd_mouse_btn = tk.Button(self)
        self.rcd_mouse_btn["text"] = "start record"
        self.rcd_mouse_btn["command"] = self.record_action
        self.rcd_mouse_btn.pack(side="top")

        self.sav_rcd_btn = tk.Button(self)
        self.sav_rcd_btn["text"] = "save record"
        self.sav_rcd_btn["command"] = self.save_record
        self.sav_rcd_btn.pack(side="top")

        self.zip_rcd_btn = tk.Button(self)
        self.zip_rcd_btn["text"] = "zip record"
        self.zip_rcd_btn["command"] = self.zip_events
        self.zip_rcd_btn.pack(side="top")
        
        self.load_rcd_btn = tk.Button(self)
        self.load_rcd_btn["text"] = "load record"
        self.load_rcd_btn["command"] = self.load_record
        self.load_rcd_btn.pack(side="top")
        
        self.play_rcd_btn = tk.Button(self)
        self.play_rcd_btn["text"] = "play record"
        self.play_rcd_btn["command"] = self.mouse_events.replay
        self.play_rcd_btn.pack(side="top")
        
        self.play_zip_btn = tk.Button(self)
        self.play_zip_btn["text"] = "play zipped"
        self.play_zip_btn["command"] = self.play_zip
        self.play_zip_btn.pack(side="top")
        
        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")
        
        ################
        #self.tst_btn = tk.Button(self)
        #self.tst_btn["text"] = "test"
        #self.tst_btn["command"] = self.test
        #self.tst_btn.pack(side="bottom")

    def record_action(self):
        self.rcd_mouse_btn["text"] = "press 'a' to stop record"
        self.update()
        self.mouse_events.start_record()
        keyboard.wait("a")
        self.mouse_events.stop_record()
        self.rcd_mouse_btn["text"] = "start record"
    def save_record(self):
        filename = filedialog.asksaveasfilename(title='Select an evt file to save', filetypes=[('evt', '*.evt'), ('All Files', '*')])
        self.mouse_events.saveEvents(filename+'.evt')
     
    def load_record(self):
        filename=filedialog.askopenfilename(title='Select an evt file to load', filetypes=[('evt', '*.evt'), ('All Files', '*')])
        self.mouse_events.loadEvents(filename)
    def zip_events(self):
        zipped = []
        events = self.mouse_events.events
        for i,evt in enumerate(events):
            current_class = type(evt).__name__
            if current_class == "MoveEvent":
                cmdstr = "move(" + str(evt.x)+ " , " + str(evt.y) +")"
            elif current_class == "ButtonEvent":
                if evt.event_type == 'up':
                    cmdstr = "button up"
                if evt.event_type == 'down':
                    cmdstr = "button down"
            if i == 0:
                zipped.append(evt)
            else:
                last_event=events[i-1]
                if current_class =="ButtonEvent":
                    if type(last_event).__name__ =="MoveEvent":
                        zipped.append(last_event)
                    zipped.append(evt)
                elif i == len(events)-1 :
                    if type(last_event).__name__=="ButtonEvent":
                        zipped.append(last_event)
                    zipped.append(evt)
        self.mouse_events.events = zipped.copy()        
                
            
    def play_zip(self):
        
        unzip = []
        
        class Node():
        
            def __init__(self,x,y,time):
                self.x = x
                self.y = y
                self.time = time

            def addmv(self,node1,node2):
                speed = 300 #dots per sec
                dt = 0.1

                x0 = node1.x
                y0 = node1.y
                x1 = node2.x
                y1 = node2.y
                t0 = node1.time
                t1 = node2.time
                d = pow((x1-x0)**2+(y1-y0)**2 , 0.5)
                sin = (y1-y0)/d
                cos = (x1-x0)/d
                steps = int((t1-t0)/dt)
                step_size = d/steps
                for i in range(steps):
                    x = x0 + i*step_size*cos
                    y = y0 + i*step_size*sin
                    t = t0+i*dt
                    if t == t1: t=t1-0.01
                    if t == t0: t = t0+0.01
                    unzip.append(mouse.MoveEvent(x,y,t))
                
        last_node = None
        zipped_events = self.mouse_events.events
        
        for i,e in enumerate(zipped_events):
            unzip.append(e)
            if type(e).__name__ == "MoveEvent":
                last_node = Node(e.x,e.y,e.time)
            if type(e).__name__ == "ButtonEvent":
                last_node.time = e.time # update the time by button events
                
            if i+1 < len(zipped_events):
                e1 = zipped_events[i+1] # e1 is next event
                if type(e1).__name__ == "MoveEvent":
                    last_node.addmv(last_node,Node(e1.x,e1.y,e1.time))
                elif type(e1).__name__ == "ButtonEvent":
                    pass
            else: # last element
                pass

        #for e in unzip:print(e)
        mouse.play(unzip)
            



root = tk.Tk()
app = Application(master=root)
app.mainloop()