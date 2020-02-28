#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import h5py
import matplotlib.pyplot as plt
import numpy as np
import random, csv, math
#panda 3d??? 
'''
Vestigial issues: why are we dropping the first fixation before saccade? fix(0) = saccade(0)-1
'''
f = h5py.File('free_fix_events_fixed.hdf5', 'r')
temp1 = f["data_collection"]
#print(list(temp1["events"]))
messages = temp1["events"]["experiment"]["MessageEvent"]
fix_end = temp1["events"]["eyetracker"]["FixationEndEvent"]
fix_start = temp1["events"]["eyetracker"]["FixationStartEvent"]
sac_end = temp1["events"]["eyetracker"]["SaccadeEndEvent"]
sac_start = temp1["events"]["eyetracker"]["SaccadeStartEvent"]
mes_text_list = []
distancesTotal = []

plotData = {
        "condition40" : {"x":[], "y":[], "fixtime":[], "distance":[], "direction":[], "dirtime":[]},        
        "condition20" : {"x":[], "y":[], "fixtime":[], "distance":[], "direction":[], "dirtime":[]},        
        }

mes_time_list = { 
        1 : {"fixtime" : [], "direction":[], "dirtime":[]},        
        2 : {"fixtime" : [], "direction":[], "dirtime":[]},        
        }

def getTargetSlice(targetNum): #Given trial num, return target slice 
    coordFile= open("coordFile.txt","r")
    data = ""
    for i in range(targetNum):
        data=coordFile.readline()
    data = data.split("#")
    return int(data[4])

def findDistance(targetNum,x,y): #Given target trial, x and y arrays, return distances as a list
    coordFile= open("coordFile.txt","r")
    data = ""
    distances = []
    for i in range(targetNum):
        data=coordFile.readline()
    data = data.split("#")
    print(data)
    x1=float(data[0]); y1=float(data[1]);x2=float(data[2]);y2=float(data[3])
    xc = round((float(x1)+float(x2))/2); yc = round((float(y1)+float(y2))/2)
    for i in range(0,len(x)):
        distance = 10000000
        dx=x[i]-x1; dx=dx*dx; dy=y[i]-y1; dy=dy*dy; dval=dx+dy; dval=math.sqrt(dval)
        if dval < distance:
            distance = dval
        dx=x[i]-x2; dx=dx*dx; dy=y[i]-y2; dy=dy*dy; dval=dx+dy; dval=math.sqrt(dval)
        if dval < distance:
            distance = dval
        dx=x[i]-xc; dx=dx*dx; dy=y[i]-yc; dy=dy*dy; dval=dx+dy; dval=math.sqrt(dval)
        if dval < distance:
            distance = dval
        distances.append(distance)
    distancesTotal.append(distances)    
    return distances

def getCurrentSlice(s_time, sac_time, condition):
    currentslice = 1;
    for i in range(0, len(mes_time_list[condition]["dirtime"])):   
        time = mes_time_list[condition]["dirtime"][i]
        #if time > sac_time:
        #    break
        if s_time <= time and time <= sac_time:
            if "RIGHT" in mes_time_list[condition]["direction"][i]:
                currentslice +=1
            if "LEFT" in mes_time_list[condition]["direction"][i]:
                currentslice -=1
    #print(currentslice)
    return currentslice

session_max = 1
for sac in sac_end: 
    sess = sac["session_id"]
    if sess > session_max:
        session_max = sess
        
cond1_sessions = []; cond2_sessions = []; dirList = []; dirTimeList = []
for mes in messages: 
    mestest = mes["text"]
    mestest = mestest.decode('UTF-8')
    if mes["session_id"] == 2: #40 sec condition 
        if "START_TRIAL" in mestest or "END_TRIAL" in mestest:
            mes_time_list[2]["fixtime"].append(mes["time"])
        if "RIGHT" in mestest:
            mes_time_list[2]["direction"].append("RIGHT")
            mes_time_list[2]["dirtime"].append(mes["time"])
        if "LEFT" in mestest:
            mes_time_list[2]["direction"].append("LEFT")
            mes_time_list[2]["dirtime"].append(mes["time"])
            
    if mes["session_id"] == 1: #20 sec condition 
        if "START_TRIAL" in mestest or "END_TRIAL" in mestest:
            mes_time_list[1]["fixtime"].append(mes["time"])
        if "RIGHT" in mestest:
            mes_time_list[1]["direction"].append("RIGHT")
            mes_time_list[1]["dirtime"].append(mes["time"])
        if "LEFT" in mestest:
            mes_time_list[1]["direction"].append("LEFT")
            mes_time_list[1]["dirtime"].append(mes["time"])

    if "40" in mestest: #probably? should only append once since the message is once per session LOL
        cond2_sessions.append(mes["session_id"])
    if "20" in mestest:
        cond1_sessions.append(mes["session_id"])

for session in range(1,session_max+1): #Loops every session
    trial = 1; i = 0; sac_count = 0; fix_count = 0
    while i < len(mes_time_list[session]["fixtime"]):
        #print(i)
        s_time = mes_time_list[session]["fixtime"][i]
        e_time = mes_time_list[session]["fixtime"][i+1]
        targetslice = getTargetSlice(trial)
        sac_x=[];sac_y=[];fix_dur=[];
        
        for sac in range(sac_count,len(sac_end)):
            if (sac_end[sac]["session_id"] == session):    
                sactime = sac_end[sac]["time"]
                if sactime > e_time:
                    break
                if s_time <= sactime and sactime <= e_time:
                    if (getCurrentSlice(s_time,sactime,session)) == targetslice:
                        sac_x.append(sac_end[sac]["end_gaze_x"])
                        sac_y.append(sac_end[sac]["end_gaze_y"])
                        sac_count=sac

        for fix in range (fix_count, len(fix_end)):  
            if (fix_end[fix]["session_id"] == session):                
                fixtime = fix_end[fix]["time"]
                if int(getCurrentSlice(s_time,fixtime, session)) == int(targetslice): 
                    if s_time <= fixtime and fixtime <= e_time:
                        fix_dur.append(fix_end[fix]["duration"])
                        fix_count=fix

        for x in range(len(sac_y)):
            sac_x[x]+=1280/2
            sac_y[x]+=1024/2
        if session == 2:
            #print(str(i) + " cond2")
            #print(sac_x)
            plotData["condition40"]["x"].append(sac_x)
            plotData["condition40"]["y"].append(sac_y)
            plotData["condition40"]["fixtime"].append(fix_dur)
            plotData["condition40"]["distance"].append(findDistance(trial,sac_x,sac_y))
        
        if session == 1:
            plotData["condition20"]["x"].append(sac_x)
            plotData["condition20"]["y"].append(sac_y)
            plotData["condition20"]["fixtime"].append(fix_dur)
            plotData["condition20"]["distance"].append(findDistance(trial,sac_x,sac_y))
                     
        i+=2; trial+=1;

graphnum = 1
for i in range(0, len(plotData["condition20"]["x"])): #for i from 0-10
    fig, (axs1, axs2) = plt.subplots(1,2)
    
    mark1 = [200*x for x in plotData["condition20"]["fixtime"][i]] #Marker sizes
    mark2 = [200*x for x in plotData["condition40"]["fixtime"][i]]

    alphas1 = np.linspace(0.1, 1, len(plotData["condition20"]["x"][i]))
    rgba_colors1 = np.zeros((len(plotData["condition20"]["x"][i]),4))
    rgba_colors1[:,2] = 0.5 #Columns for RGB values
    rgba_colors1[:, 3] = alphas1 #Alpha values

    alphas2 = np.linspace(0.1, 1, len(plotData["condition40"]["x"][i]))
    rgba_colors2 = np.zeros((len(plotData["condition40"]["x"][i]),4))
    rgba_colors2[:,2] = 0.5 #Columns for RGB values
    rgba_colors2[:, 3] = alphas2 #Alpha values
    
    fig.suptitle("TRIAL " + str(graphnum), x=1.0)
    axs1.scatter(plotData["condition20"]["x"][i], 
                 plotData["condition20"]["y"][i], s=mark1,color = rgba_colors1)
    axs2.scatter(plotData["condition40"]["x"][i], 
                 plotData["condition40"]["y"][i], s=mark2,color = rgba_colors2)
    axs1.set_xlim([0,1280]); axs1.set_ylim([0,1024]); axs1.set_xlabel("Width"); axs1.set_ylabel("Height")
    axs1.text(x= 1000, y = -150, s="Fixations: " + str(len(plotData["condition20"]["fixtime"][i])))    
    axs2.text(x= 1000, y = -150, s="Fixations: " + str(len(plotData["condition40"]["fixtime"][i])))        
    axs1.set_title("20s Condition")
    axs2.set_xlim([0,1280]); axs2.set_ylim([0,1024]); axs2.set_xlabel("Width"); axs2.set_ylabel("Height")
    axs2.set_title("40s Condition")    
    plt.subplots_adjust(right = 2.0, wspace=0.5)    
    graphnum+=1

    #plot image behind 
    #np.linalg.norm

