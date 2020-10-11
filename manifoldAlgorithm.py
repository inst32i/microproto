#!/usr/bin/env python
# coding: utf-8

# 微分流行算法需要用到的函数均放于此
# 1. getLabel 通过文件名获取数据集中数据的列名

import pandas as pd
from sklearn import preprocessing
import sys
import importlib
importlib.reload(sys)
# reload(sys)
# sys.setdefaultencoding('utf-8')
import decimal
import math
import numpy as np
from numpy.linalg import *
import datetime
import os
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

def getLabel(filename):
    csvdata = pd.read_csv(filename, header=0)
    labels = csvdata.columns.tolist()
    labels[0] = 'index'
    labels1 = labels[8:]
    dosData = csvdata.values.tolist()
    dosStartRow = 1
    dosEndRow = len(dosData)
    dosStartCol = 8
    dosEndCol = len(dosData[0])
    dosTables = getContent(dosData, dosStartRow, dosEndRow, dosStartCol, dosEndCol)
    dosNoDemTable = process_table(dosTables)
    dosNoDemTable_var = np.var(dosNoDemTable, axis=0)
    for i in range(len(dosNoDemTable_var) - 1):
        for j in range(i + 1, len(dosNoDemTable_var)):
            if dosNoDemTable_var[i] < dosNoDemTable_var[j]:
                dosNoDemTable_var[i], dosNoDemTable_var[j] = dosNoDemTable_var[j], dosNoDemTable_var[i]
                labels1[i], labels1[j] = labels1[j], labels1[i]
    return labels, labels1[0:10]

# 无量纲化处理
def process_table(tables):
    tables = np.array(tables)
    scaler = MinMaxScaler()
    scaler.fit(tables.astype(float))
    table_scaled2 = scaler.transform(tables)
    return table_scaled2

# 获取指标对
def pairsOfIp(filename):
    data = pd.read_csv(filename)
    pair = data[["Source IP", "Destination IP"]]
    countS = pair["Source IP"].value_counts() > 6
    countD = pair["Destination IP"].value_counts() > 6
    srIpList = countS[countS].keys().tolist()
    desIpList = countD[countD].keys().tolist()
    pair1 = pair[pair["Source IP"].isin(srIpList)]
    pair2 = pair1[pair1["Destination IP"].isin(desIpList)]
    pair3 = pair2.drop_duplicates()
    datalist = np.array(pair3).tolist()
    
    totalList = srIpList+desIpList
    lenList = len(totalList)
    ipIdx = {}
    for i in range(lenList):
        ipIdx[totalList[i]] = i
    
    pi = 3.1416
    ipLocByIdx = []
    for i in range(lenList):
        ipLocByIdx.append([i,(2 * pi * i) / lenList])

    pairs = []
    for i in range(len(datalist)):
        pairs.append([ipIdx[datalist[i][0]], ipIdx[datalist[i][1]]])
    
    ipIdxList = []
    for ip in ipIdx:
        ipIdxList.append([ip,ipIdx[ip]])
    
    return ipIdxList, ipLocByIdx, pairs

# 选取Top K 个指标
# 根据指标变化率，求出变化率最大的K个指标的指标值
def selectTopKIndex(tables,top):
    trowlen = len(tables)
    tcollen = len(tables[0])
    list = []
    res = []
    tmp = []
    for i in range(0,tcollen):
        tmp.append(1.0)
    list.append(tmp)
    for i in range(0,trowlen-1):
        for j in range(0,tcollen):
            app = []
            t = float(tables[i][j])
            t1 = float(tables[i+1][j])
            if(t==0):
                mul = t1-t
            else:
                mul = (t1-t)/t
            app.append(mul)
        list.append(app)
    for i in range(0,len(list)):
        row = list[i]
        rowlen = len(row)
        tableRow = tables[i]
        for j in range(0,rowlen-1):
            for k in range(j+1,rowlen):
                if(row[j]<row[k]):
                    t = row[j]
                    row[j] = row[k]
                    row[k] =t
                    t = tableRow[j]
                    tableRow[j] = tableRow[k]
                    tableRow[k] =t
        tableRow = tableRow[0:top]
        res.append(tableRow)
    return res

def getContent(table,startRow,endRrow,startCol,endCol):
    list = []
    for rownum in range(startRow,endRrow):
        excel_row=[]
        for colnum in range(startCol,endCol):
            s = table[rownum][colnum]
            if(str(s).strip()!=''):
                cell_value = table[rownum][startCol]
                if(cell_value=="Infinity"):
                    cell_value = 1e9
                if(cell_value=="NaN"):
                    cell_value = 0.0
                excel_row.append(str(cell_value).encode('utf-8'))
        if len(excel_row)>0:
            list.append(excel_row)
    return list

# 计算网络活动风险
def calculateDos(dosNoDemTable):
    dosNoDemTable = selectTopKIndex(dosNoDemTable, 4)
    endRow = len(dosNoDemTable)
    endCol = len(dosNoDemTable[0])
    sum = 0.0
    for i in range(0, endRow - 1):
        for j in range(0, endCol):
            t1 = dosNoDemTable[i][j]
            t2 = dosNoDemTable[i + 1][j]
            # t = t2-t1
            t = (t1 + t2) / 2.0
            # t = 1
            sum += math.fabs(t1) * math.fabs(t2) * math.exp(math.fabs(t))
    return endRow, round(sum, 4)

# calculate risk by minute
def calRisk(filename, Labels):
    normalEffect = 42546.1833
    normalRows = 529918           #经计算得到的
    newdata = pd.read_csv(filename)
    Time = set(newdata['Timestamp'])
    Labels.append('Timestamp')
    newdata = newdata[Labels]

    datachunk = []
    T = []
    for time in Time:
        T.append(time)
    T.sort()
    for t in T:
        datachunk.append(newdata[newdata['Timestamp'] == t])
    values = []
    times = []
    for data in datachunk:
        data.drop('Timestamp', axis = 1)
        dosData = data.values.tolist()
        dosStartRow = 1
        dosEndRow = len(dosData)
        dosStartCol = 0
        dosEndCol = len(dosData[0])
        dosTables = getContent(dosData, dosStartRow,dosEndRow,dosStartCol,dosEndCol)
        dosNoDemTable = process_table(dosTables)
        dosRows, dosEffect = calculateDos(dosNoDemTable)
        size = str(normalEffect).index('.')
        n = pow(10, size)
        normalizedNormal = round(normalEffect / n, 4)
        normaliedDos = round(dosEffect * (normalRows * 1.0 / dosRows) / n, 4)
        beishu = round(normaliedDos / normalizedNormal, 4)
        values.append(normaliedDos)
        times.append(beishu)
    return values, times, T
    
if __name__ == '__main__':
    filename = 'testData.csv'
    Labels = getLabel(filename)
    Labels = Labels[10:20]
    print (Labels)
    values, times, T = calRisk(filename,Labels)
    print ([values, times, T])
        
