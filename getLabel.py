import pandas as pd

def getLabel(filename):
    csvdata = pd.read_csv(filename, header = 0)
    labels = csvdata.columns.tolist()
    labels[0] = 'index'
    return labels

if __name__ == '__main__':
    filename = 'testData.csv'
    r = getLabel(filename)
    print(r)