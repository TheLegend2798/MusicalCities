import tkinter as tk
from tkinter import messagebox,PhotoImage
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from array import array
from time import sleep
import time
from mpl_toolkits.basemap import Basemap
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.collections import PolyCollection
import pygame
from pygame.mixer import Sound, get_init, pre_init
import math

#This class will be playing the note required
class Note(Sound):
    #This is the constructor and will define the initial conditions for the waves
    def __init__(self, frequency, volume=.5):
        self.frequency = frequency
        Sound.__init__(self, self.build_samples())
        self.set_volume(volume)

    #The sound engine uses samples of data to turn the sample input into sound
    def build_samples(self):
        sample_rate = pygame.mixer.get_init()[0]
        period = int(round(sample_rate / self.frequency))
        amplitude = 2 ** (abs(pygame.mixer.get_init()[1]) - 1) - 1
        
        #Gnerates the value for each point on the sin wave to create the sound wave
        def frame_value(i):
            return amplitude * np.sin(2.0 * np.pi * self.frequency * i / sample_rate)
        values=np.array([frame_value(x) for x in range(0, period)])
        return values.astype(np.int16)

# open the file
readFile = open('GBplaces.csv','r');

# create a variable to determine whether it is the first line or not
processTheLine = 0;
#This will hold the first line
firstLine=''
#Will hold the unsorted array
unsortedArray=[]
#Will hold the sorted array
sortedArray=[]
# read in the file line by line
for line in readFile:
    if processTheLine:
        # split the input line based on a comma
        splitUp = line.split(',');
        unsortedArray.append([splitUp[0],splitUp[1],int(splitUp[2]),splitUp[3],splitUp[4]])
    else:
        firstLine=line
    processTheLine = 1
    
# close the file
readFile.close();

# sort the array
sortedArray= sorted(unsortedArray,key=lambda unsortedArray: unsortedArray[2]);

# write the data out to a different file

# open a file to write to
writeFile = open('sortedGBplaces.csv','w');
writeFile.write(firstLine);

for i in sortedArray:
    # write a line to the file
    writeFile.write('%s,%s,%d,%s,%s'%(i[0],i[1],i[2],i[3],i[4]))

# close the file when we're finished
writeFile.close();

# open the file
readFile = open('sortedGBplaces.csv','r');

# create a variable to determine whether it is the first line or not
processTheLine = 0;
#This will hold the first line
firstLine=''
#Will hold the places array
placesArray=[]
latitude=[]
longitude=[]
names=[]
population=[]
rotatedNames=[]
frequencies=[]
types=[]

n=0
# read in the file line by line
for line in readFile:
    if processTheLine:
        # split the input line based on a comma
        splitUp = line.split(',');
        splitUp[4]=splitUp[4].replace('\n','')
        names.append(splitUp[0])
        population.append(float(splitUp[2]))
        latitude.append(float(splitUp[3]))
        longitude.append((float(splitUp[4])))
        types.append(splitUp[1])
        #frequencies.append(float(splitUp[2])/1000)
        frequencies.append(float(263.79+(2**((n-49)/12)*44)))
        placesArray.append([splitUp[0],splitUp[1],int(splitUp[2]),splitUp[3],splitUp[4]])
    else:
        firstLine=line
    n+=1
    processTheLine = 1

#This is just needed to convert the names to upper letters to look better
for name in names:
    rotatedNames.append(name.upper())
    
# close the file
readFile.close();

#This is the class containing the bulk of the GUI
class View(tk.Frame):
   #This global variable will show the sound wave on it
    img=0

    """
    The following function plays the note depending on which key on the piano
    was pressed. It then draws the sound wave onto the plot and als updates the data
    shown in the data text box.
    """
    def playNote(self,event):
         pre_init(44100, -16, 1, 1024)
         pygame.init()
         a=Note(frequencies[int(event.widget.message)]).play(-1)
         self.currentKey=int(event.widget.message)
         sleep(0.4)
         a.stop()
         #self.canvas2.delete("all")
         self.after_cancel(self.redraw)
         #global img
         #self.canvas2.create_image((300/2, 300/2), image=img, state="normal")
         self.sine_wave_anim()
         self.waveText.configure(state='normal')
         self.waveText.delete(1.0,tk.END)
         self.waveText.insert(tk.INSERT,"Name: %s\nPopulation: %d People\nCorresponding Frequency Generated: %3.2fHz\nLatitude: %3.6f\nLongitude: %3.6f\nType: %s"%(names[self.currentKey],population[self.currentKey],frequencies[self.currentKey],latitude[self.currentKey],longitude[self.currentKey],types[self.currentKey]))
         self.waveText.configure(state='disabled')
      
    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    """
    The following function creates the animated sine wave representing the sound wave
    It is basically calling itself over and over and the wave that it is plotting is a function of time
    """
    def sine_wave_anim(self):
        # Update sine wave
        frequency = frequencies[self.currentKey]/100
        amplitude = 100 # in px
        speed = 1
        
        # We create a blank area for what where we are going to draw
        color_table = [["#000000" for x in range(0, 400)] for y in range(0, amplitude*2)]
        
        # And draw on that area
        for x in range(0, 400):
            y = int(amplitude + amplitude*math.sin(frequency*((float(x)/400)*(2*math.pi) + (speed*time.time()))))
            color_table[y][x] = "#ffff00"

        global img
        img.put(''.join("{" + (" ".join(str(color) for color in row)) + "} " for row in color_table), (0, int(400/2 - amplitude)))
        # Continue the animation as fast as possible. A value of 0 (milliseconds), blocks everything.
        self.redraw=self.after(1, self.sine_wave_anim)

    """
    This is the constructor method where most of the GUI components are defined,designed...etc
    """
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        
        #This canvas holds all the piano keys
        self.canvas = tk.Canvas(root,background="orange",width=self.master.winfo_screenwidth(),height="300")
        self.frame = tk.Frame(self.canvas, background="orange")
        #This is the scrollbar needed to show all the keys
        self.hsb = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.hsb.set)

        self.canvas.pack(side="top", fill="x")
        self.hsb.pack(side="top", fill="x")
        self.canvas.create_window((2,2), window=self.frame, anchor="center",tags="self.frame")
        #Needed to update the frame when moving the bar
        self.frame.bind("<Configure>", self.onFrameConfigure)

        #Fills all the buttons in the canvas and colours them accordingly
        for i in range(100):
            
            self.b = tk.Button(self.frame,text=rotatedNames[i],wraplength="1",compound="left",width=2,height=20)
            self.b.message = str(i)
            self.b.bind('<Button-1>', self.playNote)
            self.b.grid(row=0, column=i, sticky='NW',padx=2, pady=5)
            if(types[i]=='Town'):
                self.b.configure(background="red",foreground="black")
            else:
                self.b.configure(background="blue",foreground="white")
        
        #This is the map plot of the UK with the cities on it
        self.fig= plt.figure("1",figsize=(6,4))
        self.ax = self.fig.gca(projection='3d')
        self.m = Basemap(resolution='i',lat_0=54.5, lon_0=-4.36,llcrnrlon=-6., llcrnrlat= 49.5, urcrnrlon=2., urcrnrlat=58.5,fix_aspect=False,ax=self.ax)

        self.ax.set_zlim(0., 12.)
        self.ax.set_xlabel(u'Longitude')
        self.ax.set_ylabel(u'Latitude')
        self.ax.set_zlabel(u'Population/Millions')
        extent = [49.5,58.5,-6.,2.]
        # Add meridian and parallel gridlines
        lon_step = 0.1
        lat_step = 0.1
        meridians = np.arange(extent[0], extent[1]+lon_step, lon_step)
        parallels = np.arange(extent[2], extent[3]+lat_step, lat_step)        
        self.ax.set_yticks(parallels)
        self.ax.set_yticklabels(parallels)
        self.ax.set_xticks(meridians)
        self.ax.set_xticklabels(meridians)
        
        self.ax.azim = -149
        self.ax.dist = 10
        self.ax.elev=29
        polys = []
        for polygon in self.m.landpolygons:
            polys.append(polygon.get_coords())
            
            
        lc = PolyCollection(polys, edgecolor='black',
                            facecolor='#DDDDDD', closed=True)
            
        self.ax.add_collection3d(lc)
        self.ax.add_collection3d(self.m.drawcoastlines(linewidth=0.25))
        self.ax.add_collection3d(self.m.drawcountries(linewidth=0.35))
        x1=np.array(longitude)
        y1=np.array(latitude)
        pop=[]
        for s in np.array(population):
            pop.append(s/100000)
        x,y= self.m(x1,y1)
        self.fig.tight_layout()
        #This is where the 3D bars are drawn onto the map
        self.ax.bar3d(x, y,np.zeros(len(x)), 0.1, 0.1, pop, color= 'r',alpha=0.8)
        self.dataPlot = tkagg.FigureCanvasTkAgg(self.fig,master=root)
        self.dataPlot.show()
        self.dataPlot.get_tk_widget().pack(side="left",fill="both")
        #This is the canvas holding the img which displays the 
        #Animated sound wave
        self.canvas2 = tk.Canvas(root,width=400, height=300, bg="#000000")
        global img
        img = PhotoImage(width=400, height=300)
        self.canvas2.create_image((400/2, 300/2), image=img, state="normal")
        #self.canvas2.show()
        self.canvas2.pack(side="left", fill="both", expand=True)
        self.currentKey=0
        self.sine_wave_anim()
        #This text area contains important information about the place and the wave formed
        self.waveText = tk.Text(root, borderwidth=3, relief="sunken",width=40)
        self.waveText.insert(tk.INSERT,"Name:\nPopulation:\nCorresponding Frequency Generated:\nLatitude:\nLongitude:\nType:")
        self.waveText.config(font=("arial bold", 11), wrap='word',background="orange",state="disabled")
        self.waveText.pack(side="left",fill="both")
        
        
if __name__ == "__main__":
    #Main window of program
    root = tk.Tk()
    #Call to GUI class
    view = View(root)
    view.master.configure(background='orange')
    #A message Box for instructions
    messagebox.showinfo("Welcome", "INSTRUCTIONS: \nWelcome to this interactive piano.\nEach key is a city or town from GB.\nRed keys are towns, blue keys are cities.\nThey are ordered in ascending order of population.\nThe leftmost key has the lowest population and therefore the lowest frequency.\nThe graph to the left shows where the places are in the GB according to latitude and longitude. The graph to the right shows the wave for the note you just played.\nHave fun!")
    root.mainloop()

