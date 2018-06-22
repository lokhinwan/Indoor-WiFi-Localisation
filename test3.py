import time
import csv
import math
import operator
from sklearn.svm import SVC
from shapely.geometry import LineString

def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False     

def euclidean(p1, p2, length):
    d = 0
    for i in range(length):
        d += pow(p1[i]-p2[i], 2)
    return math.sqrt(d)

def getNeighbours(trainingSet, testInstance, k):
    distances = []
    length = len(testInstance)
    for x in range(len(trainingSet)):
        dist = euclidean(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbours = []
    for x in range(k):
        neighbours.append(distances[x][0])
    return neighbours

def getLocation(neighbours, snr):
    votes = {} #find the mode in the dataset
    p=[]
    for x in range(len(neighbours)):
        for key, signal in snr.items():
            if neighbours[x] in signal:
                location = key
        if location in votes:
            votes[location] += 1
        else:
            votes[location] = 1
    sortedVotes = sorted(votes.items(), key=operator.itemgetter(1), reverse=True)
    for i in range(len(sortedVotes)):
        for j in range(sortedVotes[i][1]+1):
            p.append(tuple(map(int, sortedVotes[j][0].split(","))))
    centroid=LineString(p).centroid.wkt
    
    #return the location with the highest votes, and the % accuracy
    return [sortedVotes[0][0],
            round(float(votes[sortedVotes[0][0]])/len(neighbours)*100.0, 2),
            centroid]

y=[]
data=[]
snr={}
temp=[]
pos=[100,100,100,100]
is_running=True
k=7


ofilename = input("What is the offline file name?") or 'onlinephase.csv'
print ('The offline file name is:', ofilename)

ifilename = input("What is the online file name?") or "test0 - Copy.csv"
print ("The online file name is:", ifilename)

try:
    with open(ofilename, 'r') as csvfile:
        file_read = csv.reader(csvfile, delimiter=',', quotechar='"')

        for row in file_read:
            key=row[0]
            for x in range(1,len(row)):
                #split cell, remove empty list, map string into int, add to snr
                temp.append(list(map(int, filter(None, row[x].split(",")))))
                snr[key] = list(filter(None, temp))
            for i in range(len(snr[key])):
                y.append(key)
            data += filter(None, temp)
            
            temp = []   

    clf=SVC()
    clf.fit(data,y)

            
    while is_running:
        with open(ifilename, 'r') as csvfile2:
            inread = csv.reader(csvfile2, delimiter=',')

            for row in inread:                              
                for x in range(1,4):
                    if isint(row[x])==True:
                        temp=int(row[x])
                        pos[x-1]=abs(temp)
                    elif row[x]=='n/a':
                        pos[x-1]=100
                print ('Position:', pos)

                neighbours=getNeighbours(data,pos,k)
                #print ('Neighbours: ', neighbours)

                decision = getLocation(neighbours, snr)
                print ('\n kNN: \n Location:', decision[0], '\n Confidence:', decision[1],'%')
                print('\n SP Centroid:', decision[2])

                if len(pos)==3:
                    pos.append(0)
                    #print('\n svm_pos:', svm_pos)
                print('\n SVM:', clf.predict([pos]), '\n')
                
        #the code to clear file
        with open(ifilename, 'w+') as csvfile3:
            csvfile3.close() #clear the file by writing nothing to the file
        
        time.sleep(1.5)

except IOError:
    print("Offline file does not exist")

except KeyboardInterrupt:
    print("Keyboard Interrupt")
    
print("Program Terminates")
