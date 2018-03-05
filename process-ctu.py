import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from os import listdir
from os.path import isfile, join, splitext
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import confusion_matrix as cfmat


def balance_partition(X):
    # Takes combined 6-attack and ctu datasets and produces balanced train/test partition based on lowest common
    # denominator class (botnet traffic only has 901 flows, so only 800 samples from each class are used in training)
    train, test = [], []
    class_counts = pd.value_counts(X['Label'].values)
    for label in class_counts.index.tolist():
        count = class_counts[label]
        temp_X = X.loc[X['Label'] == label]
        temp_train, temp_test = train_test_split(temp_X, train_size=800, random_state=1)
        train.append(temp_train), test.append(temp_test)
    train = pd.concat(train, ignore_index=True)
    test = pd.concat(test, ignore_index=True)
    return train, test


# Read files in and pre-process csv
argus_path = 'flows/argus/'
csv_files = [file for file in listdir(argus_path) if isfile(join(argus_path, file)) and '.csv' in splitext(file)]
print(csv_files)

dfs = []
for file in csv_files:
    df_temp = pd.read_csv(join(argus_path, file), sep=',')
    filename, ext = splitext(file)
    df_temp['Label'] = filename
    dfs.append(df_temp)

alldf = pd.concat(dfs, ignore_index=True)

# Load CTU-46 dataset
ctu_df = pd.read_csv('flows/ctu/ctu46_argus.csv')

# Features which will not be used
pointless_features = ['SrcAddr', 'DstAddr', 'SrcMac', 'DstMac', 'Sport', 'Dport']
string_features = ['Dir', 'State', 'Flgs', 'StartTime']
nan_features = ['SIntPkt', 'SIntPktAct', 'SIntPktIdl', 'DIntPkt', 'DIntPktAct', 'SrcJitter', 'DstJitter',
                'dTtl', 'dTos', 'dMaxPktSz', 'dMinPktSz']

# Features we will use
features = ['Label', 'Dur', 'Proto', 'RunTime', 'Mean', 'Sum', 'Min', 'Max', 'sTos', 'TotPkts', 'SrcPkts',
            'DstPkts', 'sTtl', 'TotAppByte', 'TotBytes', 'SrcBytes', 'SAppBytes', 'DstBytes', 'DAppBytes', 'Load',
            'SrcLoad', 'DstLoad', 'Loss', 'SrcLoss', 'DstLoss', 'Rate', 'sMeanPktSz', 'dMeanPktSz', 'sMaxPktSz',
            'sMinPktSz']

X = alldf[features]
ctu_X = ctu_df[features]

# Get rid of background data - keep only bot and normal traffic
ctu_X = ctu_X[ctu_X.Label.str.match('^(?!.*(Background)).*$')]
ctu_X['Label'] = ctu_X['Label'].str.replace(r'^.*(Botnet).*$', 'Botnet')
ctu_X['Label'] = ctu_X['Label'].str.replace(r'^.*(Normal).*$', 'Normal')

print("The following rows contain null values and will be removed")
print(X[X.isnull().any(axis=1)][features])
print(ctu_X[ctu_X.isnull().any(axis=1)][features])
X_faulty = X[X.isnull().any(axis=1)][features].index.values.tolist()
ctu_X_faulty = ctu_X[ctu_X.isnull().any(axis=1)][features].index.values.tolist()
X = X.drop(X_faulty)
ctu_X = ctu_X.drop(ctu_X_faulty)


# Shuffles data and resets dataframe indices (drop=true prevents creating new index for old indices)
# sample(frac=1) returns a random sample of the whole dataset (effectively just a shuffle)
X = X.sample(frac=1).reset_index(drop=True)
ctu_X = ctu_X.sample(frac=1).reset_index(drop=True)
combined_X = pd.concat([X, ctu_X], ignore_index=True)

# Get counts for each class in the datasets
class_counts = pd.value_counts(X['Label'].values)
ctu_class_counts = pd.value_counts(ctu_X['Label'].values)
with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(class_counts)
    print(ctu_class_counts)


X.to_csv('processed/6attack-argus.csv', sep=',', index=False)
ctu_X.to_csv('processed/ctu-processed.csv', sep=',', index=False)
combined_X.to_csv('processed/mixed_unbalanced.csv', sep=',', index=False)

# Split the labels from the rest of the data
y = X["Label"]
X = X.drop("Label", 1)
ctu_y = ctu_X["Label"]
ctu_X = ctu_X.drop("Label", 1)

balanced_train, balanced_test = balance_partition(combined_X)
balanced_train.to_csv('processed/mixed_balanced_train.csv', sep=',', index=False)
balanced_test.to_csv('processed/mixed_balanced_test.csv', sep=',', index=False)

bal_y_train, bal_y_test = balanced_train["Label"], balanced_test["Label"]
bal_X_train, bal_X_test = balanced_train.drop("Label", 1), balanced_test.drop("Label", 1)


dtree = DecisionTreeClassifier()
dtree.fit(bal_X_train, bal_y_train)
y_predict = dtree.predict(bal_X_test)
print("\nResults for Training/Test Split - 800/remaining")
print("---------------------------------------------\n")
print("Accuracy Score: ", dtree.score(bal_X_test, bal_y_test))
print(cfmat(bal_y_test, y_predict))

