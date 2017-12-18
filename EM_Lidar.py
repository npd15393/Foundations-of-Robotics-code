__author__ = 'Nishant'
import csv
import math
import numpy as np

measures=[]
sensor_max=4000
sensor_min=5
count_sus_max=0
count_sus_min=0
wall_read=[]
object_reads=[]
bag=[]
mix={'Gmu':0,'Gsig':8000000,'lambda':0.001,'del':0.1};

def mixture_model(z):
    actual=(1/np.sqrt(2*math.pi*mix['Gsig'])) * np.exp(-((z-mix['Gmu'])*(z-mix['Gmu']))/(2*mix['Gsig']))
    obj=(1/(1-np.exp(-mix['lambda']*mix['Gmu'])))*mix['lambda']*np.exp(-mix['lambda']*z) if z<mix['Gmu'] else 0
    out_range=1/mix['del'] if (z<=sensor_max and z>=sensor_max-mix['del']) else 0
    noise=1/3995 if (z>=5 and z<=sensor_max) else 0

    return [actual,obj,out_range,noise]


def EM():
    e=[]
    for i in range(50):
        s=[0,0,0,0]
        z=[0,0,0,0]
        for m in range(len(measures)-1):
            if len(e)<=m+1:
                e.append([])
            p=mixture_model(measures[m])
            den=sum(p)
            e[m].append(p[0]/den)
            e[m].append(p[1]/den)
            e[m].append(p[2]/den)
            e[m].append(p[3]/den)


            s[0]+=  p[0]/den
            s[1]+=  p[1]/den
            s[2]+=  p[2]/den
            s[3]+=  p[3]/den

        z[0]=s[0]/len(measures)
        z[1]=s[1]/len(measures)
        z[2]=s[2]/len(measures)
        z[3]=s[3]/len(measures)

        newsig=np.sqrt(sum([e[r][0]*(measures[r]-mix['Gmu'])*(measures[r]-mix['Gmu']) for r in range(len(e)-1)])/s[0])
        newlam=s[1]/sum([e[r][1]*measures[r] for r in range(len(e)-1)])

        mix['Gsig']=newsig
        mix['lambda']=newlam
    return [z,mix['Gsig'],mix['lambda']]


def stats(reads):
    mu=sum(reads)/len(reads)
    sq=[x*x for x in reads]
    sig=sum(sq)/len(sq)-mu*mu
    return mu,sig
with open('LIDAR_100ms_Wander.csv', newline='') as csvfile:
 spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
 spamreader=list(spamreader)
 for row in spamreader:
    # print(', '.join(row))

    measures.append(max(5,min(float(row[0]),4000)))
    if float(row[0])>4000:
        count_sus_max+=1
    if float(row[0])<5:
        count_sus_min+=1
    if float(row[0])>3000 and float(row[0])<4000:
        reset=True
        if len(bag)>0:
            object_reads.append(bag)
            bag=[]
        wall_read.append(float(row[0]))
    if float(row[0])>5 and float(row[0]) <3000:
        if reset==True:
            bag=[]
            bag.append(float(row[0]))
            reset=False
        else:
            bag.append(float(row[0]))

# 1a
print('Probability of suspiciously out of range measurement={0}'.format(count_sus_max/len(spamreader)))

# 1b
print('Probability of suspiciously minimum range measurement={0}'.format(count_sus_min/len(spamreader)))

# 1c
wall_mu,wall_sig=stats(wall_read)
mix['Gmu']=wall_mu
print('Statistics of wall readings: Mean={0} and Standard Deviation={1}'.format(wall_mu,math.sqrt(wall_sig)))

# 1d
print('The number of objects detected={0}'.format(len(object_reads)))
reals=[i for i in object_reads if len(i)>10]
vel=[abs(x[-1]-x[0])/(len(x)-1)/0.1 if len(x)>1 else 0 for x in reals]
print('Max Velocity is {0} cm/s for object {1}'.format(max(vel),np.argmax(vel)+1))

obj_measures=sum([len(r) for r in object_reads])
real_measures=sum([len(r) for r in reals])
print('Probability of measurement being an object and not wall={0}\n'.format((real_measures)/(len(measures)-count_sus_max-count_sus_min)))

# 2
[weights,Sigma,Lambda]=EM()
print('Weights of components of mixture for distributions in order [P(hit),P(short),P(max),P(rand)]=')
print('{0}; \nSigma={1}; Lambda={2}'.format(weights,Sigma,Lambda))
input()