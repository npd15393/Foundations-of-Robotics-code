# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 15:17:51 2017

@author: Nishant
"""
import math
import csv
import numpy as np
import matplotlib.pyplot as plt

def stats(reads):
    mu=sum(reads)/len(reads)
    sq=[x*x for x in reads]
    sig=sum(sq)/len(sq)-mu*mu
    return mu,sig

def sample_from_gaussian(pdf,x):
    pow=-1/2*(x-pdf[0])*(x-pdf[0])/(pdf[1])
    return (1/np.sqrt(2*math.pi*pdf[1]))*np.exp(pow)

def sample_exp_decay(xs):
    return 0.05*np.exp(-0.05*xs)

x_measures=[]
x_estimates=[]
v_estimates=[]
sigx=[]
sigv=[]
T=[0]

def get_mixture_probs(xp,xs):
    return [0.8*sample_from_gaussian([xp[0][0],0.001],xs),0.2*sample_exp_decay(xs)]


def KF(xm,xs,P,R,A,q,n,td):

    b=np.array([[+(td**3)*0.01*(0.1**3)-(0.1**3)*0.01*(0.1**3), (td**2)*0.01*(0.1**2)-(0.1**2)*0.01*(0.1**2)],[(td**2)*0.01*(0.1**2)-(0.1**2)*0.01*(0.1**2),(td)*0.01*(0.1)-(0.1)*0.01*(0.1)]])
    c=np.array([[0,(td-1)*0.1],[0,0]])

    A=np.array(A)-np.array(c)
    q=np.array(q)+np.array(b)

    x_predicted=A*xm
    Pn=np.dot(A,P*np.transpose(A))+q
    H=np.asmatrix([1,0])

    a=np.dot(H,(Pn*np.transpose(H))+R)
    K=Pn*np.transpose(H)/a
    #K=np.reshape(np.array([K[0][0],K[1][0]]),(2,1))

    if n==1:
        x_posterior=x_predicted+K*(xs-H*x_predicted)
        P_posterior=(np.identity(2)-K*H)*Pn

        T.append(T[-1]+0.1)
    elif n==2:
        x_temp=x_predicted+K*(xs-H*x_predicted)
        P_temp=(np.identity(2)-K*H)*Pn
        delta=xs-float(x_temp[0])
        inno=np.dot(H,(P_temp*np.transpose(H)))
        var=delta*delta/inno
        if var<9:
            x_posterior=x_predicted+K*(xs-H*x_predicted)
            P_posterior=(np.identity(2)-K*H)*Pn
            T.append(T[-1]+0.1*td)
            td=1

        else:
            td+=1
            return np.array([]),np.array([]),td

    elif n==3:
        x_temp=x_predicted+K*(xs-H*x_predicted)
        p=get_mixture_probs(x_temp,xs)

        if p[0]>p[1]:
            x_posterior=np.array(x_predicted)+np.array(K)*(xs-np.dot(H,x_predicted))
            P_posterior=(np.identity(2)-K*H)*Pn
            T.append(T[-1]+0.1*td)
            td=1
        else:
            td+=1
            return np.array([]),np.array([]),td

    return x_posterior,P_posterior,td

def estimate(n):
    P0=np.array([[0.01, 0],[0, 0.01]])
    x0=np.asmatrix([25.30,.1]).T
    R=0.001
    Q=[[0.01*0.1*0.1*0.1, 0.01*0.1*0.1],[0.01*0.1*0.1,0.01*0.1]]
    A=[[1,-0.1],[0,1]]
    t=1
    for i in x_measures:
        xm=i
        xt,Pt,t=KF(x0,xm,P0,R,A,Q,n,t)
        if xt.tolist()!=[] and Pt.tolist()!=[]:
            x_estimates.append(float(xt[0])*100)
            v_estimates.append(float(xt[1])*100)
            sigx.append(Pt.tolist()[0][0]*10000)
            sigv.append(Pt.tolist()[1][1]*10000)
            x0=np.asmatrix(xt)
            P0=np.asmatrix(Pt)




#Script starts from here
#Reading data file and queuing data
with open('RBE500-F17-100ms-Constant-Vel.csv', newline='') as csvfile:
 spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
 spamreader=list(spamreader)
 for row in spamreader:
    x_measures.append(float(row[0])/100)

# Input the following numbers as arguments to estimate() for the corresponding postprocessing/filtering of KF estimates
# 1: Conventional KF   2: KF with object rejection (innovation)  3: KF with object rejection (mixture model)
estimate(2)
# Plot data
sigx1=[]
for i in sigx:
    sigx1.append(i)
estimate(3)

# T.remove(0)
# print(len(x_estimates))
# plt.scatter(T,x_estimates)
# plt.xlabel('Time')
# plt.ylabel('Range estimates')
# plt.show()
#
# plt.scatter(T,v_estimates)
# plt.xlabel('Time')
# plt.ylabel('Velocity estimates')
# plt.show()
#
# plt.scatter(T,sigx)
# plt.xlabel('Time')
# plt.ylabel('Range Estimate Uncertainty')
# plt.show()
#
# plt.scatter(T,sigv)
# plt.xlabel('Time')
# plt.ylabel('Velocity Estimate Uncertainty')
# plt.show()
