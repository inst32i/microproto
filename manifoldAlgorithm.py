#!/usr/bin/env python
# coding: utf-8

# 微分流行算法需要用到的函数均放于此
# 1. getLabel 通过文件名获取数据集中数据的列名

import pandas as pd
from sklearn import preprocessing
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import decimal
import math
import numpy as np
from numpy.linalg import *
import datetime
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

def getLabel(filename):
    csvdata = pd.read_csv(filename, header = 0)
    labels = csvdata.columns.tolist()
    labels[0] = 'index'
    return labels

# 无量纲化处理
def process_table(tables):
    tables = np.array(tables)
    scaler = MinMaxScaler()
    scaler.fit(tables.astype(float))
    table_scaled2 = scaler.transform(tables)
    return table_scaled2

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
    Labels = ["Source IP", "Source Port", "Destination IP", "Destination Port", "Protocol", "Timestamp", "Flow Duration"]
    values, times, T = calRisk(filename,Labels)
    print [values, times, T]
        
