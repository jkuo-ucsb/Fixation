 #!/usr/local/bin/python
# -*- coding: utf-8 -*  -

from __future__ import absolute_import, division
from psychopy import visual
from psychopy.data import TrialHandler, importConditions
from psychopy import locale_setup,gui,core,data,event,logging 
from psychopy.iohub import ioHubExperimentRuntime
from psychopy.tools.filetools import fromFile, toFile
from psychopy.iohub import (EventConstants, EyeTrackerConstants, ioHubExperimentRuntime, module_directory, getCurrentDateTimeString)
from psychopy.iohub import launchHubServer
import pylink as pl 
import random
import numpy, random, csv
from win32api import GetSystemMetrics
import numpy
import os
import sys

try: #tries to get a previous paramters file
    expInfo = fromFile('lastParams.pickle')
except : #if file doesn't exist, use default set 
    expInfo = {'Observer': 'Initials', 'SessionNum' :0, "Date": data.getDateStr()[:-5]}


#present dialogue box to change parameters
dbox = gui.DlgFromDict(expInfo, title = 'TestExperiment',order=["Observer", "SessionNum", "Date"])
if dbox.OK:
    toFile('lastParams.pickle', expInfo) 
else:
    core.quit() 
fileName = expInfo["Observer"] + expInfo["Date"]
answerFile = open(fileName+'.csv', 'w+')

def isTarget(stimName):
    return "target" in stimName   

class ExperimentRuntime(ioHubExperimentRuntime):
    '''Create an experiment using psychopy and the ioHub framework by extending 
    the ioHubExperimentRuntime class and implementing the run() method.
    '''
    def run(self, *args):
        ###---Set up the iohub events for monitoring---###
    # Get some iohub devices for future access.
        keyboard = self.hub.devices.keyboard
        display = self.hub.devices.display
        tracker = self.hub.devices.tracker
        mouse = self.hub.devices.mouse
        res = display.getPixelResolution()
        sys_width = GetSystemMetrics(0)
        sys_height = GetSystemMetrics(1)
        #r = tracker.runSetupProcedure()
        clock = core.Clock() 

      
        #create window
        win = visual.Window(res, 
                            monitor=display.getPsychopyMonitorName(),
                            units=display.getCoordinateType(),
                            fullscr=True,
                            allowGUI=True,
                            screen= display.getIndex()
                            )
                            
        win.mouseVisible = False
        #create text prompt
        text_stim = visual.TextStim(win,
                                     text='WAS THE TARGET PRESENT?\nPRESS "Y" FOR YES OR "N" FOR NO.',
                                     pos= (0,184), 
                                     height=30,
                                     color='white',
                                     alignHoriz='center',
                                     alignVert='center',
                                     )
        ppd = display.getPixelsPerDegree()[0]
        
        gaze_dot = visual.GratingStim(win,
                                      tex=None, 
                                      mask='gauss',
                                      pos=(0, 0),
                                      size=(66, 66),
                                      color='green',
                                      units='pix',
                                      )
                                      
        '''stime = clock.getTime()
        while clock.getTime() -stime < 5.0:
            print(keyboard.getEvents())'''
        
        stimList = []
        targetPresent = []
        for i in range (1,11):
            addedAlready = False  
            for j in range (1,11):
                try:
                    stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(j))+".png")
                except:
                    stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(j))+"_TARGET.png")
                    targetPresent.append(True)
                    addedAlready = True
                print(stim)
                stimList.append(stim)
            if addedAlready == False:
                targetPresent.append(False)

        
        #theseKeys = event.getKeys(keyList=['left', 'right', 'space', 'q', 'esc', 'y', 'n','a', 'd'])                                   
        def free_fix(stimList, trialtime, textList, drawEye = True, add_text = False, drawFix = True):
            self.hub.clearEvents('all') #clear events in iohub
            
            #START TRACKING THE EYE
            flip_time = win.flip()
            self.hub.sendMessageEvent(text = "CONDITION_TIME_"+str(trialtime), sec_time = flip_time)
            tracker.setRecordingState(True)
            t = tracker.isReportingEvents()
            #Welcome screen             
            welcome_stim = visual.TextStim(win,
                                     text='PRESS ANY KEY TO BEGIN.',
                                     pos= (0,184), 
                                     height=30,
                                     color='white',
                                     alignHoriz='center',
                                     alignVert='center',
                                     )
            welcome_stim.draw()
            win.flip()
            continueKey = keyboard.waitForPresses() #pauses until space
            #loop through free fixation stimuli 
            for i in range(1, 11): #i number of trials
                targetInTrial = targetPresent[i]
                print("i :" + str(i))
                self.hub.sendMessageEvent(text='START_TRIAL_' + str(i))
                win.flip()
                trial_stim = visual.TextStim(win,
                                     text='TRIAL ' + str(i) ,
                                     pos= (0,184), 
                                     height=30,
                                     color='white',
                                     alignHoriz='center',
                                     alignVert='center',
                                     )
                trial_stim.draw()
                win.flip()
                core.wait(2.0)
                stimNum = 1
                stime = clock.getTime()
                #quit_and_save() #allow subject to exit if needed
                #recalibrate() #allow subject to recalibrate if need be
                #set up variables to make sure subject is looking into the gaze okay region 
                #gpos = tracker.getLastGazePosition() 
                subjectReport = False
                keylists = []
                while subjectReport is False: 
                    keylists = []
                    keylists = event.getKeys()
                    try:
                        stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(stimNum))+"_TARGET.png")
                    except:
                        stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(stimNum))+".png")
                    stim.draw()
                    
                    if 'q' in keylists:
                        print("Q Manual Exit")
                        tracker.setConnectionState(False)
                        self.hub.sendMessageEvent(text='EXPERIMENT_MANUAL_EXIT')
                        core.quit() 
                    if "escape" in keylists:   
                        print("ESC Manual Exit")
                        tracker.setConnectionState(False)
                        self.hub.sendMessageEvent(text='EXPERIMENT_MANUAL_EXIT')
                        core.quit()                  
                        
                    if "left" in keylists and stimNum > 1:
                        print("Switching Left To " + str(stimNum-1))
                        stimNum-=1
                        self.hub.sendMessageEvent(text='LEFT')                        
                        try:
                            stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(stimNum))+"_TARGET.png")
                        except:
                            stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(stimNum))+".png")
                        stim.draw()
               
                    if "right" in keylists and stimNum < 10:
                        print("Switching Right To "+ str(stimNum+1))
                        stimNum+=1
                        self.hub.sendMessageEvent(text='RIGHT')                                                
                        try:
                            stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(stimNum))+"_TARGET.png")
                        except:
                            stim = visual.ImageStim(win, image = ("stim")+ str(int(i))+"_"+str(int(stimNum))+".png")
                        stim.draw()
                        
                    if "y" in keylists:#'y' in event.getKeys():
                        print("Report Y")
                        #self.hub.sendMessageEvent(text='RESPONSE_Y')
                        subjectReport = True
                        if (targetInTrial==True):
                            answerFile.write("HIT\n")
                        if (targetInTrial==False):
                            answerFile.write("FA\n")
                        break

                    if "n" in keylists:#'n' in event.getKeys():
                        print("Report N")
                        #self.hub.sendMessageEvent(text='RESPONSE_N')
                        subjectReport = True
                        if (targetInTrial==True):
                            answerFile.write("MISS\n")
                        if (targetInTrial==False):
                            answerFile.write("CR\n")
                        break
                    
                     #this is for the added pressure constraint of time   
                    if clock.getTime()-stime>=trialtime:
                        win.flip()
                        self.hub.sendMessageEvent(text='TRIAL_TIME_OUT')
                        for t in textList:
                            t.draw()
                        win.flip()
                        
                        print("here once")
                        
                        while subjectReport is False:
                            keylists = event.getKeys() #idk why, but you have to call this again here
                            for t in textList:
                                t.draw()
                            win.flip()
                            
                            if "y" in keylists:#'y' in event.getKeys():
                                print("Report Y")
                                #self.hub.sendMessageEvent(text='RESPONSE_Y')
                                subjectReport = True
                                if (targetInTrial==True):
                                    answerFile.write("HIT\n")
                                if (targetInTrial==False):
                                    answerFile.write("FA\n")
                                break
        
                            if "n" in keylists:#'n' in event.getKeys():
                                print("Report N")
                                #self.hub.sendMessageEvent(text='RESPONSE_N')
                                subjectReport = True
                                if (targetInTrial==True):
                                    answerFile.write("MISS\n")
                                if (targetInTrial==False):
                                    answerFile.write("CR\n")
                                break
                                
                            if 'q' in keylists:
                                print("Q Manual Exit")
                                tracker.setConnectionState(False)
                                self.hub.sendMessageEvent(text='EXPERIMENT_MANUAL_EXIT')
                                core.quit() 
                            if "escape" in keylists:   
                                print("ESC Manual Exit")
                                tracker.setConnectionState(False)
                                self.hub.sendMessageEvent(text='EXPERIMENT_MANUAL_EXIT')q
                                core.quit()                  
                            #subjectReport = False    
                        print("out here once")
                    del keylists[:]

                    gpos = tracker.getLastGazePosition() 
                    valid_gaze_pos = isinstance(gpos, (tuple, list))
    
                    #should subject eye position be drawn on screen? 
                    if (valid_gaze_pos is True) & (drawEye is True): 
                        gaze_dot.pos = gpos 
                        gaze_dot.draw()
                    win.flip()
                    #end while loop
                self.hub.sendMessageEvent(text='END_TRIAL_' + str(i))
            #end i level loop
           # print("end i level")
        #experiment done
            tracker.setRecordingState(False)
            flip_time = win.flip()
            self.hub.sendMessageEvent(text ="FREE_FIX_EXIT", sec_time = flip_time)
            
            
        # Run introTrial.....
        free_fix(stimList, 40, [text_stim], drawEye = True, add_text = False)
        self.hub.clearEvents('all')
      
        

runtime=ExperimentRuntime(module_directory(ExperimentRuntime.run), "iohub_config.yaml")
runtime.start()      