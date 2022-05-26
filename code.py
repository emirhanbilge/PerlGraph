# -*- coding: utf-8 -*-
"""
Created on Sun May 22 15:43:17 2022

@author: EBB
"""

import pandas as pd 
import graphviz
import os
from flask import  render_template,request , Flask
import matplotlib.pyplot as plt
import time

class Vertex():
    
    def __init__(self , Number):
        self.Number = Number
        self.outcameEdges = set()
        self.incameEdge = set()
        
    def addIncameEdge(self, edge): # outcame edge
        self.incameEdge.add(edge)
    
    def addOutCameEdge(self, edge):
        self.outcameEdges.add(edge)

    def __str__(self):
        temp = "Out Come Edges : \n"
        for i in self.outcameEdges:
            temp += i.__str__() + "\n"
        temp += "Income Edges : \n"
        for i in self.incameEdge:
            temp += i.__str__()+" \n"
        return "Number : "  + self.Number +" \n" + temp
     
class Edge():
    
    def __init__(self, startVertex , finishVertex):
        self.startVertex = startVertex
        self.finishVertex = finishVertex
        self.startTime = 0
        self.FinishTime = 0
        self.workName = ""
        self.elasticStartTime = 0
        self.elasticFinishTime = 0
        self.criticalPath = False
        self.workTime = 0
        
    def setDuration(self , startTime , FinishTime):
        self.startTime = startTime
        self.FinishTime = FinishTime
    
    def setWorkName(self , workName):
        self.workName = workName
        
    
    def setElasticTime(self, elasticStartTime , elasticFinishTime):
        self.elasticStartTime = elasticStartTime
        self.elasticFinishTime = elasticFinishTime
    
    def setWorkTime(self,workTime):
        self.workTime = workTime
    
    def __str__(self):
        return "Start Node " + self.startVertex.Number +" "+ self.workName +" Finish Node : " + self.finishVertex.Number +" Start Time " + str(self.startTime)+ " Finish Time " + str(self.FinishTime) +" Duration : " + str(self.workTime)+"\n" +"Elastic Start : " + str(self.elasticStartTime) +" Elastic Finish : " + str(self.elasticFinishTime)   
        
class Graph():
    
    def __init__(self):
        self.edges = []
        self.vertex=[]
    
    def addEdge(self,startVertex , finishVertex , startTime=0 ,workTime=0, FinishTime=0,workName="" ):

        sn = startVertex
        fn = finishVertex
        e = Edge(sn , fn)
        e.setDuration(startTime, FinishTime)
        e.setWorkName(workName)
        e.setWorkTime(workTime)
        sn.addOutCameEdge(e)
        fn.addIncameEdge(e)
        self.edges.append(e)
        return e
    
    def addVertex(self, Number):
        v = Vertex(Number)
        self.vertex.append(v)
        return v
    
    def findFinishVertex(self,e):
        for i in self.edges:
            if i.workName == e:
                return i.finishVertex

    def findBeforeTime(self,v):
        maxTime = 0
        for i in v.incameEdge:
            if maxTime < i.FinishTime :
                maxTime = i.FinishTime
        return maxTime
    
    def outcameMaxTimeFinder(self,v): # başlangıç vertexi v olan edge içerisindeki en düşük başlangıcı al
        minN = 9999
        node = None
        for i in self.edges:
            if i.startVertex.Number == v and minN > i.elasticStartTime:
                minN = i.elasticStartTime
                node = i.startVertex
        return node , minN
    
    def allParentsofVertex(self,v):
        parentList = []
        for i in self.edges:
            if i.finishVertex == v:
                parentList.append(i.startVertex)
        return parentList    
    
    def getFinishNodeEdge(self,v):
        arr = []
        for i in self.edges:
            
            if i.finishVertex == v:
                arr.append(i)
        return arr
    def getVertexwithName(self,Number):
        for i in self.vertex:
            if i.Number == Number :
                return i
    
def smartEbbCalculator(df):
    ebbList = []
    controlList = []
    dropList = []
    while(len(ebbList) != len(df['Pre'])): ## her birinde dataframein indexine göre dropla ve forun en aşağında olacak
        for j in range(len(df['Pre'])):
            if j not in dropList:
                i = df.iloc[j]
                if i['Pre'] == "-":
                    ebbList.append(i)
                    controlList.append(i['Activity'])
                    dropList.append(j)
                else:
                    tempList = i['Pre'].split(";")
                    if len(tempList) == 1 and tempList in controlList:
                        ebbList.append(i)
                        controlList.append(i['Activity'])
                        dropList.append(j)
                    else:
                        flag = True
                        for q in tempList:
                            if q not in controlList:
                                flag = False
                                break
                        if flag:
                            ebbList.append(i)
                            controlList.append(i['Activity'])
                            dropList.append(j)
                    
    return ebbList , controlList
    
def graphCreator(fileName):
    
    global brcx
    visualEdgeCounter = 0
    g = Graph()

    dataframe = pd.read_csv(fileName,delimiter=",")
    ## başlangıç vertex oluşturma
    count = 1
    gse = g.addVertex(str(count))
    brcx,ebbx = smartEbbCalculator(dataframe)
    for i in brcx :
        if i[2] == '-':
            count += 1
            fn = g.addVertex(str(count))
            e = g.addEdge(gse,fn ,startTime=0,FinishTime=i[1], workTime=i[1] , workName=i[0])
            fn.addIncameEdge(e)
            gse.addOutCameEdge(e)
        else:
            temp = i[2].split(";")
            if len(temp) ==1:
                count +=1
                sv = g.findFinishVertex(i[2])
                sttime = g.findBeforeTime(sv)
                fn = g.addVertex(str(count))
                e = g.addEdge(sv,fn ,startTime=sttime,FinishTime= sttime+i[1], workTime=i[1] , workName=i[0])
                fn.addIncameEdge(e)
                sv.addOutCameEdge(e)
            else:
                maxTime = 0
                for q in temp:
                    sv = g.findFinishVertex(q)
                    sttime = g.findBeforeTime(sv)
                    if maxTime < sttime:
                        maxTime = sttime
                count +=1    
                visualEdgeCounter +=1
                fn = g.addVertex(str(count))
                for q in temp:
                    sv = g.findFinishVertex(q)
                    e = g.addEdge(sv,fn , workName="Visual Edge"+str(visualEdgeCounter),startTime=maxTime,FinishTime= maxTime)
                    e.elasticStartTime = maxTime
                    e.elasticFinishTime = maxTime
                    fn.addIncameEdge(e)
                    sv.addOutCameEdge(e)
                count +=1
                sv = g.findFinishVertex("Visual Edge"+str(visualEdgeCounter))
                sttime = maxTime
                fn = g.addVertex(str(count))
                e = g.addEdge(sv,fn , startTime=sttime,FinishTime= sttime+i[1], workTime=i[1] , workName=i[0])
                fn.addIncameEdge(e)
                sv.addOutCameEdge(e)
    count += 1
    finalStateVertex = []
    maxTime = 0
    for i in g.vertex:
        if len(i.outcameEdges) == 0:
            finalStateVertex.append(i)
            elem = i.incameEdge.pop()
            if elem.FinishTime> maxTime:
                maxTime = elem.FinishTime
            i.incameEdge.add(elem)
    fn = g.addVertex(str(count))
    for i in finalStateVertex:
        sv = i
        e = g.addEdge(sv,fn , workName="Finish Edge",startTime=maxTime,FinishTime= maxTime)
        e.setElasticTime(maxTime, maxTime)
        fn.addIncameEdge(e)
        sv.addOutCameEdge(e)
    return g

def backTrackAlgorithmHelper(g):
    
    finalState = g.vertex[-1]
    mytemp = set(g.allParentsofVertex(finalState))
    ff = set()
    tempr = set(g.allParentsofVertex(finalState))
    ll = 0
    ordervertexMap = dict()
    for i in tempr:
        ordervertexMap[i.Number] = i
        ll += 1
    while(len(ff) != len(g.vertex)-1):
        for i in mytemp:
            tempr = tempr.union(set( g.allParentsofVertex(i)))
            for i in tempr:
                try:
                    trs = ordervertexMap[i.Number]
                except:
                    flag = True
                    for m in i.outcameEdges:
                        if m.finishVertex not in ordervertexMap.values():
                            flag = False
                    if flag:
                        ordervertexMap[i.Number] =i 
                        ll += 1
        mytemp = mytemp.union(tempr)
        ff = ff.union(tempr)
        mytemp = set()
        mytemp = mytemp.union(tempr)
        tempr = set()
    lastarr = []
    for i in ordervertexMap.keys() :
        lastarr.append( i)
    return lastarr
        
def backTrackAlgorithm(G, nodelist):
    
    for i in nodelist:
        try:
            currentNode,newFinish = (G.outcameMaxTimeFinder(i))
            updateEdge = G.getFinishNodeEdge(currentNode)
            if len(updateEdge) == 1:
                updateEdge = updateEdge[0]
                updateEdge.elasticFinishTime = newFinish
                updateEdge.elasticStartTime = newFinish- updateEdge.workTime
            else:
                for m in updateEdge:     
                    m.elasticFinishTime = newFinish
                    m.elasticStartTime = newFinish- m.workTime
        except:
            pass

def createGraphVisual(G):
    f = graphviz.Digraph('Software Project Management Pert Diagram',directory="\\Users\\EBB\\Desktop\\UIgraph\\static", filename='fsm' , format='png')
    f.attr(rankdir='LR', size='10,5')
    f.attr('node', shape='circle')
    
    fileTable = open("outputTable.csv","a")
    fileTable.write("Work,Start Time,Finish Time,Elastic Start Time,Elastic Finish Time,Critical Path\n")
    for i in G.vertex:
        f.node(str(i.Number))
    for i in G.vertex:
        for j in i.outcameEdges:
            # style="dashed"
            if "Visual Edge" in j.workName or "Finish Edge" in j.workName :
               
                f.edge(str(j.startVertex.Number) , str(j.finishVertex.Number) , label=(j.workName + "("+ str(j.startTime)+","+str(j.FinishTime) +")") ,xlabel=(j.workName + "("+ str(j.elasticStartTime)+","+str(j.elasticFinishTime) +")") ,style="dashed"  ,fontcolor="Red")
            else:
                if j.startTime == j.elasticStartTime :
                    j.criticalPath = True
                    xstr = (j.workName+","+str(j.startTime)+","+str(j.FinishTime)+"," +str(j.elasticStartTime)+","+str(j.elasticFinishTime)+",Yes\n")
                    fileTable.write(xstr)
                    f.edge(str(j.startVertex.Number) , str(j.finishVertex.Number) , label=(j.workName + "("+ str(j.startTime)+","+str(j.FinishTime) +")") , xlabel=(j.workName + "("+ str(j.elasticStartTime)+","+str(j.elasticFinishTime) +")")  ,color="blue" )
                else:
                    xstr = (j.workName+","+str(j.startTime)+","+str(j.FinishTime) +","+str(j.elasticStartTime)+","+str(j.elasticFinishTime)+",No\n")
                    fileTable.write(xstr)
                    f.edge(str(j.startVertex.Number) , str(j.finishVertex.Number) , label=(j.workName + "("+ str(j.startTime)+","+str(j.FinishTime) +")") , xlabel=(j.workName + "("+ str(j.elasticStartTime)+","+str(j.elasticFinishTime) +")")   )
    fileTable.close()
    
    df = pd.read_csv("outputTable.csv",delimiter=",")
    
    
    
    fig, ax =plt.subplots(1,1)
    data=df.to_numpy()
    
    column_labels=["Work,Start Time,Finish Time,Elastic Start Time,Elastic Finish Time,Critical Path".split(",")]
    df=pd.DataFrame(data,columns=column_labels)
    ax.axis('tight')
    ax.axis('off')
    ax.table(cellText=df.values,colLabels=df.columns,loc="center")
    
    
    
    plt.savefig('\\Users\\EBB\\Desktop\\UIgraph\\static\\mytable.png' , dpi=320)
    f.view()
    os.remove("outputTable.csv")
    for i in G.vertex:
        print(i)

###### Test 
def performanceTest(fileName):
    start = time.time()
    ourgraph = graphCreator(fileName) 
    listofbertex = backTrackAlgorithmHelper(ourgraph)
    backTrackAlgorithm(ourgraph,listofbertex)
    createGraphVisual(ourgraph)
    end = time.time()
    print("Total Time: " , end - start , " Vertex Number: " , len(ourgraph.vertex) ," Edge Number : ", len(ourgraph.edges))

def makeTest():
    fileNames = ["example1.csv","example2.csv", "example3.csv"]
    for i in fileNames:
        performanceTest(i)





app = Flask(__name__,static_url_path='/static')
UPLOAD_FOLDER = '\\Users\\EBB\\Desktop\\UIgraph'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(f.filename)
      ourgraph = graphCreator(f.filename) 
      listofbertex = backTrackAlgorithmHelper(ourgraph)
      backTrackAlgorithm(ourgraph,listofbertex)
      createGraphVisual(ourgraph)
      return render_template("results.html")
      #return send_file("fsm.gv.pdf", as_attachment=True)
   
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

#makeTest()












