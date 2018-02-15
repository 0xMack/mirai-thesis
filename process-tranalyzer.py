import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from os import listdir
from os.path import isfile, isdir, join, splitext

# Read files in and pre-process csv
tranalyzer_path = 'flows/tran/'
csv_dirs = [folder for folder in listdir(tranalyzer_path) if isdir(join(tranalyzer_path, folder))]
print(csv_dirs)

dfs = []
for dir_name in csv_dirs:
    df_temp = pd.read_csv(join(tranalyzer_path, dir_name + "/" + dir_name + "_flows.txt"), sep='\t')
    print(dir_name + ' has ' + str(len(df_temp)) + ' records')
    df_temp['Label'] = dir_name + '-tran'
    print(df_temp.head(5))
    dfs.append(df_temp)

alldf = pd.concat(dfs, ignore_index=True)


# Features which will not be used
pointless_features = ['dstPort', 'srcPort', 'dstIP4', 'srcIP4', 'unixTimeFirst', 'unixTimeLast']
hex_features = ['flowStat', 'srcMac_dstMac_numP', 'tcpFStat', 'ipTOS', 'ipFlags', 'ipOptCpCl_Num', 'tcpAggrFlags',
                'tcpAggrAnomaly', 'tcpAggrOptions', 'tcpStates', 'icmpStat', 'icmpTCcnt', 'icmpBFType_Code',
                'icmptmgtw']
string_features = ['%dir', 'hdrDesc', 'srcManuf_dstManuf', 'dstPortClass', 'srcIPCC', 'dstIPCC']
nan_features = []


# Features we will use
features = ['Label', 'flowInd', 'duration', 'numHdrDesc', 'numHdrs',
            'ethVlanID', 'l4Proto', 'macPairs', 'dstPortClassN', 'numPktsSnt', 'numPktsRcvd',
            'numBytesSnt', 'numBytesRcvd', 'minPktSz', 'maxPktSz', 'avePktSize', 'stdPktSize', 'pktps', 'bytps',
            'pktAsm', 'bytAsm', 'ipMindIPID', 'ipMaxdIPID', 'ipMinTTL', 'ipMaxTTL', 'ipTTLChg', 'ipOptCnt',
            'tcpPSeqCnt', 'tcpSeqSntBytes', 'tcpSeqFaultCnt', 'tcpPAckCnt', 'tcpFlwLssAckRcvdBytes', 'tcpAckFaultCnt',
            'tcpInitWinSz', 'tcpAveWinSz', 'tcpMinWinSz', 'tcpMaxWinSz', 'tcpWinSzDwnCnt', 'tcpWinSzUpCnt',
            'tcpWinSzChgDirCnt', 'tcpOptPktCnt', 'tcpOptCnt', 'tcpMSS', 'tcpWS', 'tcpTmS', 'tcpTmER', 'tcpEcI',
            'tcpBtm', 'tcpSSASAATrip', 'tcpRTTAckTripMin', 'tcpRTTAckTripMax', 'tcpRTTAckTripAve',
            'tcpRTTAckTripJitAve', 'tcpRTTSseqAA', 'tcpRTTAckJitAve', 'icmpTCcnt', 'icmpEchoSuccRatio', 'icmpPFindex',
            'connSip', 'connDip', 'connSipDip', 'connSipDprt', 'connF']


X = alldf[features]

print(X[X.isnull().any(axis=1)][features])
X_faulty = X[X.isnull().any(axis=1)][features].index.values.tolist()
X = X.drop(X_faulty)
print(X[X.isnull().any(axis=1)][features])

# Suffles data and resets dataframe indices (drop=true prevents creating new index for old indices)
# sample(frac=1) returns a random sample of the whole dataset (effectively just a shuffle)
X = X.sample(frac=1).reset_index(drop=True)

X.to_csv('6attack-tran.csv', sep=',', index=False)

# Split the labels from the rest of the data
y = X["Label"]
X = X.drop("Label", 1)




from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import confusion_matrix as cfmat
kf = KFold(n_splits=10)
kf.get_n_splits(X)
fold_num = 1

# 10-Fold Cross-Validation of Decision Tree Classifier
for train_index, test_index in kf.split(X):
    print("\nResults for Fold #", fold_num)
    print("TRAIN:", train_index, "   TEST:", test_index)
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    dtree = DecisionTreeClassifier()
    dtree.fit(X_train, y_train)
    y_predict = dtree.predict(X_test)
    print("Accuracy Score: ", dtree.score(X_test, y_test))
    print(cfmat(y_test, y_predict))
    fold_num += 1

# Now that dataset has been validated, train model and test on a 66/33 spit
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=1)
dtree = DecisionTreeClassifier()
dtree.fit(X_train, y_train)
y_predict = dtree.predict(X_test)
print("\nResults for Training/Test Split -- 66%/33%")
print("---------------------------------------------\n")
print("Accuracy Score: ", dtree.score(X_test, y_test))
print(cfmat(y_test, y_predict))


from sklearn.externals.six import StringIO
# from IPython.display import Image, display
from sklearn.tree import export_graphviz
import pydotplus
dot_data = StringIO()
export_graphviz(dtree, out_file=dot_data,
                filled=True, rounded=True,
                special_characters=True,
                feature_names=features,
                class_names=y)

graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
graph.write_png('img/tranalyzer_dtree_python.png')
