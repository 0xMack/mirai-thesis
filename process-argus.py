import pandas as pd
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from os import listdir
from os.path import isfile, join, splitext
import math
import subprocess

# python -m pip install pandas

# data = genfromtxt('/home/mack/workspace/mirai/flows/argus/ack-argus.csv', delimiter=',', dtype=None)

# Read files in and pre-process csv
argus_path = 'flows/argus/'
csv_files = [file for file in listdir(argus_path) if isfile(join(argus_path, file)) and '.csv' in splitext(file)]
print(csv_files)

dfs = []
for file in csv_files:
    df_temp = pd.read_csv(join(argus_path, file), sep=',')
    filename, ext = splitext(file)
    print(filename + ' has ' + str(len(df_temp)) + ' records')
    df_temp['Label'] = filename
    dfs.append(df_temp)

alldf = pd.concat(dfs, ignore_index=True)


# Features which will not be used
pointless_features = ['SrcAddr', 'DstAddr', 'SrcMac', 'DstMac']
string_features = ['Dir', 'State', 'Flgs', 'StartTime']
nan_features = ['SIntPkt', 'SIntPktAct', 'SIntPktIdl', 'DIntPkt', 'DIntPktAct', 'SrcJitter', 'DstJitter',
                'dTtl', 'dTos', 'dMaxPktSz', 'dMinPktSz']

# Features we will use
features = ['Dur', 'Proto', 'Sport', 'Dport', 'RunTime', 'Mean', 'Sum', 'Min', 'Max', 'sTos', 'TotPkts', 'SrcPkts',
            'DstPkts', 'sTtl', 'TotAppByte', 'TotBytes', 'SrcBytes', 'SAppBytes', 'DstBytes', 'DAppBytes', 'Load',
            'SrcLoad', 'DstLoad', 'Loss', 'SrcLoss', 'DstLoss', 'Rate', 'sMeanPktSz', 'dMeanPktSz', 'sMaxPktSz',
            'sMinPktSz']
y = alldf["Label"]
X = alldf[features]

print(X[X.isnull().any(axis=1)][features])
X_faulty = X[X.isnull().any(axis=1)][features].index.values.tolist()
X = X.drop(X_faulty)
y = y.drop(X_faulty)
print(X[X.isnull().any(axis=1)][features])
# print(X.loc[[88423]])


dtree = DecisionTreeClassifier()
dtree.fit(X, y)

# X.to_csv('testing.csv', sep='\t')

from sklearn.externals.six import StringIO
from IPython.display import Image, display
from sklearn.tree import export_graphviz
import pydotplus
dot_data = StringIO()
export_graphviz(dtree, out_file=dot_data,
                filled=True, rounded=True,
                special_characters=True)
graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
display(Image(graph.create_png()))
