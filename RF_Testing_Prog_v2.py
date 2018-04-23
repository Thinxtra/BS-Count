# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 09:50:47 2017

@author: Tam
"""

import tkinter as tk
import os
import os.path
import sys

import SigfoxAPIFunctions as SFapi
from pandas.io.json import json_normalize

TITLE_FONT = ("Helvetica", 18, "bold")
BTEXT_FONT = ("Helvetica", 14, "bold")
STEXT_FONT = ("Helvetica", 12, "normal")

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)


class SampleApp(tk.Toplevel):

    def __init__(self, master=None):
        tk.Toplevel.__init__(self)
        self.title("X-kit Testing program")
#        self.wm_iconbitmap('Thinxtra.ico')
        
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.masterData = []        
        
        self.frames = {}
        F = StartPage
        page_name = F.__name__
        frame = F(parent=self.container, controller=self)
        self.frames[page_name] = frame

        # put all of the pages in the same location;
        # the one on the top of the stacking order
        # will be the one that is visible.
        frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
#        frame.__init__(self.container, self)


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        gadgetLoc = 0
        columnDUT = 0
        columnRef = 2
        
        label = tk.Label(self, text="Thinxtra RF Test Tool", font=TITLE_FONT)
        label.grid(row=gadgetLoc, columnspan=4)
        gadgetLoc = gadgetLoc + 1

        tk.Label(self, text = 'DUT ID:', font=BTEXT_FONT).grid(row=gadgetLoc, column=columnDUT, sticky='w')
        tk.Label(self, text = 'Ref ID (3E7F69):', font=BTEXT_FONT).grid(row=gadgetLoc, column=columnRef, sticky='w')
        
        self.ID_DUT = tk.Entry(self, font=STEXT_FONT)
        self.ID_DUT.grid(row=gadgetLoc, column=columnDUT+1, sticky='w')
        self.ID_Ref = tk.Entry(self, font=STEXT_FONT)
        self.ID_Ref.grid(row=gadgetLoc, column=columnRef+1, sticky='w')
#        self.ID.insert(0, '')
        gadgetLoc = gadgetLoc + 1
        
        tk.Label(self, text='Choose Zone', font = STEXT_FONT).grid(row=gadgetLoc,column=columnDUT, sticky='w')
        
        OPTIONS = ['AU', 'NZ', 'HK']
        
        self.zoneChoicesDUT = tk.StringVar(self)
        self.zoneChoicesDUT.set('AU')
        self.zoneDUT = tk.OptionMenu(self, self.zoneChoicesDUT, *OPTIONS)
        self.zoneDUT.grid(row=gadgetLoc,column=columnDUT+1, sticky='w')

        tk.Label(self, text='Choose Zone', font = STEXT_FONT).grid(row=gadgetLoc,column=columnRef, sticky='w')
            
        self.zoneChoicesRef = tk.StringVar(self)
        self.zoneChoicesRef.set('AU')
        self.zoneRef = tk.OptionMenu(self, self.zoneChoicesRef, *OPTIONS)
        self.zoneRef.grid(row=gadgetLoc,column=columnRef+1, sticky='w')

        gadgetLoc = gadgetLoc + 1        
        
        tk.Label(self, text = 'Start time (e.g., 30 Mar 17 20 00 00):', font=STEXT_FONT).grid(row=gadgetLoc, column=columnDUT, sticky='w')
        self.sTime_DUT = tk.Entry(self, font=STEXT_FONT)
        self.sTime_DUT.grid(row=gadgetLoc, column=columnDUT+1, sticky='w')
        self.sTime_DUT.insert(0, '')
        tk.Label(self, text = 'Start time (e.g., 30 Mar 17 20 00 00):', font=STEXT_FONT).grid(row=gadgetLoc, column=columnRef, sticky='w')
        self.sTime_Ref = tk.Entry(self, font=STEXT_FONT)
        self.sTime_Ref.grid(row=gadgetLoc, column=columnRef+1, sticky='w')
        self.sTime_Ref.insert(0, '')
        gadgetLoc = gadgetLoc + 1
        
        tk.Label(self, text = 'End time (e.g., 30 Mar 17 20 00 00):', font=STEXT_FONT).grid(row=gadgetLoc, column=columnDUT, sticky='w')
        self.eTime_DUT = tk.Entry(self, font=STEXT_FONT)
        self.eTime_DUT.grid(row=gadgetLoc, column=columnDUT+1, sticky='w')
        self.eTime_DUT.insert(0, '')
        tk.Label(self, text = 'End time (e.g., 30 Mar 17 20 00 00):', font=STEXT_FONT).grid(row=gadgetLoc, column=columnRef, sticky='w')
        self.eTime_Ref = tk.Entry(self, font=STEXT_FONT)
        self.eTime_Ref.grid(row=gadgetLoc, column=columnRef+1, sticky='w')
        self.eTime_Ref.insert(0, '')
        gadgetLoc = gadgetLoc + 1

        tk.Button(self, text="Get Data", command=self.getData_DUT, font = STEXT_FONT).grid(row=gadgetLoc, column=columnDUT+1, sticky='w')
        tk.Button(self, text="Get Data", command=self.getData_Ref, font = STEXT_FONT).grid(row=gadgetLoc, column=columnRef+1, sticky='w')
        gadgetLoc = gadgetLoc + 1     
        
        tk.Button(self, text="Count", command=self.toAnalyze_DUT, font = STEXT_FONT).grid(row=gadgetLoc, column=columnDUT, sticky='e')
        self.count_DUT = tk.Entry(self, font=STEXT_FONT)
        self.count_DUT.grid(row=gadgetLoc, column=columnDUT+1, sticky='w')
        tk.Button(self, text="Count", command=self.toAnalyze_Ref, font = STEXT_FONT).grid(row=gadgetLoc, column=columnRef, sticky='e')
        self.count_Ref = tk.Entry(self, font=STEXT_FONT)
        self.count_Ref.grid(row=gadgetLoc, column=columnRef+1, sticky='w')
        gadgetLoc = gadgetLoc + 1
        
        tk.Button(self, text="Compare", command=self.toCompare, font = STEXT_FONT).grid(row=gadgetLoc, column=columnDUT+1, sticky='e')
        self.compare = tk.Entry(self, font=STEXT_FONT)
        self.compare.grid(row=gadgetLoc, column=columnRef, sticky='w')
        
    def getData_DUT(self):
        self.dataDUT = self.getData(SFapi.toEpoch(self.sTime_DUT.get()), SFapi.toEpoch(self.eTime_DUT.get()), self.ID_DUT.get(), self.zoneChoicesDUT.get())
        print(self.dataDUT)
        
    def getData_Ref(self):
        self.dataRef = self.getData(SFapi.toEpoch(self.sTime_Ref.get()), SFapi.toEpoch(self.eTime_Ref.get()), self.ID_Ref.get(), self.zoneChoicesRef.get())    
    
    def toAnalyze_DUT(self):
        output = self.dataDUT['numBS'].mean()        
        self.count_DUT.insert(0, str(output))
        
    def toAnalyze_Ref(self):
        output = self.dataRef['numBS'].mean()        
        self.count_Ref.insert(0, str(output))

            
    def getData(self, sTime, eTime, id_sf, Zone):
        ids = [substring.strip() for substring in id_sf.split(',')]
        print (sTime)
        print (eTime)
        print (id_sf)
        data = []
        for idsf in ids: 
            data = data + SFapi.get_messages_by_id_and_time(idsf, tstart = sTime, tend = eTime, zone=Zone)
        
        data = SFapi.decodeMessage(data, platform = None)
        masterData = json_normalize(data)
        
        masterData = masterData[masterData['oob']==False]
        masterData['frame'] = masterData['rinfos'].apply(lambda x : self.sumFrame(x))
        
        return masterData
        
    def sumFrame(self, x):
        frame = 0
        for item in x:
            frame = frame + item['rep']
        return frame
    
    def toCompare(self):
        
        self.compare.insert(0, str(float(self.count_DUT.get())/float(self.count_Ref.get())))
    
def doQuit():
    root.destroy()        

if __name__ == "__main__":
              
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', doQuit)
    root.withdraw()
#    root.geometry("800x600")
    app = SampleApp(master=root)
    app.protocol('WM_DELETE_WINDOW', doQuit)
    root.mainloop()

#import nunpy as np    
#first = np.random.normal(3,2,10)
#second = np.random.normal(5,2,10)
#x = stats.ttest_ind(first, second, axis=0, equal_var=True)
#alpha = 0.05
#if (x.pvalue/2 <= alpha):
#    if (x.statistic > 0):
#        print('First is NOT greater than Second with the confident level of ' + str(1-alpha) + '%')
#    else:
#        print('First is NOT smaller than Second with the confident level of ' + str(1-alpha) + '%')
#else:
#    print('No conclusion with the confident level of ' + str(1-alpha) + '%')