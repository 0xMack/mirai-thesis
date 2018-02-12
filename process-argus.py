import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from os import listdir
from os.path import isfile, join, splitext

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
features = ['Label', 'Dur', 'Proto', 'Sport', 'Dport', 'RunTime', 'Mean', 'Sum', 'Min', 'Max', 'sTos', 'TotPkts', 'SrcPkts',
            'DstPkts', 'sTtl', 'TotAppByte', 'TotBytes', 'SrcBytes', 'SAppBytes', 'DstBytes', 'DAppBytes', 'Load',
            'SrcLoad', 'DstLoad', 'Loss', 'SrcLoss', 'DstLoss', 'Rate', 'sMeanPktSz', 'dMeanPktSz', 'sMaxPktSz',
            'sMinPktSz']
X = alldf[features]

print(X[X.isnull().any(axis=1)][features])
X_faulty = X[X.isnull().any(axis=1)][features].index.values.tolist()
X = X.drop(X_faulty)
print(X[X.isnull().any(axis=1)][features])

# Suffles data and resets dataframe indices (drop=true prevents creating new index for old indices)
# sample(frac=1) returns a random sample of the whole dataset (effectively just a shuffle)
X = X.sample(frac=1).reset_index(drop=True)

X.to_csv('6attack-argus.csv', sep=',', index=False)

# Split the labels from the rest of the data
y = X["Label"]
X = X.drop("Label", 1)


from sklearn.model_selection import KFold
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
graph.write_png('img/argus_dtree.png')
