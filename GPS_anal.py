# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 01:22:03 2017

@author: Nishant
"""
import csv
import numpy as np
import math 

measures=[]
measures1=[]
measures2=[]

def read_data():
    
    with open('Master.csv', newline='') as csvfile:
         spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
         spamreader=list(spamreader)
         for row in spamreader:
            measures.append(row[0].split(','))
            
    with open('Rover_1.csv', newline='') as csvfile:
         spamreader1 = csv.reader(csvfile, delimiter=' ', quotechar='|')
         spamreader1=list(spamreader1)
         for row in spamreader1:
            measures1.append(row[0].split(','))

    with open('Rover_2.csv', newline='') as csvfile:
         spamreader2 = csv.reader(csvfile, delimiter=' ', quotechar='|')
         spamreader2=list(spamreader2)
         for row in spamreader2:
            measures2.append(row[0].split(','))
    return measures,measures1,measures2


def mean_loc(measure):
    la=0
    lo=0
    for m in measure:
        la+=int(float(m[1])/100)+(float(m[1])-100*int(float(m[1])/100))/60
        lo+=int(float(m[3])/100)+(float(m[3])-100*int(float(m[3])/100))/60
    return la/len(measure),lo/len(measure)

def deg(n):
    return int(float(n)/100)+(float(n)-100*int(float(n)/100))/60

def normalize(measure,mean):
    laerr=[]
    loerr=[]
    for m in measure:
        laerr.append(mean[0]-deg(m[1]))
        loerr.append(mean[1]-deg(m[3]))
    
    return [laerr,loerr]
        
def deg_2_m(ms,mns):
    err1=[]
    err2=[]
    for u in range(len(ms)):
        e1,e2=geo_dist(mns[0],deg(ms[u][1]),mns[1],deg(ms[u][3])) 
        err1.append(e1)
        err2.append(e2)
    return [err1,err2]


def geo_dist(Lat1,Lat2,Lon1,Lon2):
  
    latMid = (Lat1+Lat2 )/2.0;  # or just use Lat1 for slightly less accurate estimate
    
    
#    m_per_deg_lat = 111132.954 - 559.822 * math.cos( 2.0 * latMid*math.pi/180 ) + 1.175 * math.cos( 4.0 * latMid*math.pi/180);
#    m_per_deg_lon = (3.14159265359/180 ) * 6367449 * math.cos ( latMid *math.pi/180);
#    
    m_per_deg_lat = 111131.77741377673104 / (1 + 0.0033584313098335197297*math.cos(2*latMid*math.pi/180 ))**(3/2) 
    m_per_deg_lon = 111506.26354049367285 * math.cos(latMid*math.pi/180) / (1 + 0.0033584313098335197297*math.cos(2*latMid*math.pi/180))**(1/2) 
      
    deltaLat = abs(Lat1 - Lat2);
    deltaLon = abs(Lon1 - Lon2);
    
    dist_m_la =  (deltaLat * m_per_deg_lat)
    dist_m_lo =  (deltaLon * m_per_deg_lon ) 
    return dist_m_la,dist_m_lo
    
# Question 5a
measures,measures1,measures2=read_data()
measures.pop(0)
measures1.pop(0)
measures2.pop(0)

mla,mlo=mean_loc(measures)
print('Master station Mean Latitude:{0} , Mean Longitude: {1}'.format(mla,mlo))

la1,lo1=mean_loc(measures1)
print('Rover 1 station Mean Latitude:{0} , Mean Longitude: {1}'.format(la1,lo1))

la2,lo2=mean_loc(measures2)
print('Rover 2 station Mean Latitude:{0} , Mean Longitude: {1}'.format(la2,lo2))

# Question 5b
merror=normalize(measures,[mla,mlo])
error1=normalize(measures1,[la1,lo1])
error2=normalize(measures2,[la2,lo2])

merror_meters=deg_2_m(measures,[mla,mlo])
error1_meters=deg_2_m(measures1,[la1,lo1])
error2_meters=deg_2_m(measures2,[la2,lo2])

mstd=[np.std(merror_meters[0]),np.std(merror_meters[1])]
std1=[np.std(error1_meters[0]),np.std(error1_meters[1])]
std2=[np.std(error2_meters[0]),np.std(error2_meters[1])]

print('\nMaster station std err Latitude:{0} , std err Longitude: {1}'.format(mstd[0],mstd[1]))
print('Rover 1 std err Latitude:{0} , std err Longitude: {1}'.format(std1[0],std1[1]))
print('Rover 2 std err Latitude:{0} , std err Longitude: {1}'.format(std2[0],std2[1]))

# Question 5b
dist1=geo_dist(mla,la1,mlo,lo1)
dist2= geo_dist(mla,la2,mlo,lo2)

print('\nRover 1 is at {} m from Master stn'.format(np.sqrt(dist1[0]**2 + dist1[1]**2)))
print('Rover 2 is at {} m from Master stn'.format(np.sqrt(dist2[0]**2 + dist2[1]**2)))

# Question 5c
corr1=[]
corr2=[]
for m in range(len(measures)):
    for i in range(len(measures1)):
        if float(measures[m][0])==float(measures1[i][0]):
            corr1.append([error1_meters[0][i]-merror_meters[0][m],error1_meters[1][i]-merror_meters[1][m]])
    for i in range(len(measures2)):
        if float(measures[m][0])==float(measures1[i][0]):
            corr2.append([error2_meters[0][i]-merror_meters[0][m],error2_meters[1][i]-merror_meters[1][m]])

print('\nRover 1: Std Corrected errors for latitude={}'.format(np.std([t[0] for t in corr1])))
print('Rover 1: Std Corrected errors for longitude={}'.format(np.std([t[1] for t in corr1])))

print('\nRover 2: Std Corrected errors for latitude={}'.format(np.std([t[0] for t in corr2])))
print('Rover 2: Std Corrected errors for longitude={}'.format(np.std([t[1] for t in corr2])))




