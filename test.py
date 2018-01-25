import pandas as pd
from os import listdir
from os.path import isfile, join, splitext
from numpy import genfromtxt

# python -m pip install pandas

# data = genfromtxt('/home/mack/workspace/mirai/flows/argus/ack-argus.csv', delimiter=',', dtype=None)

argus_path = 'flows/argus/'
csv_files = [file for file in listdir(argus_path) if isfile(join(argus_path, file)) and '.csv' in splitext(file)]
print(csv_files)

df = pd.read_csv(join(argus_path, 'ack-argus.csv'), sep=',')
for file in csv_files:
    df2 = pd.read_csv(join(argus_path, file), sep=',')
    filename, ext = splitext(file)
    df2['Label'] = 'filename'
    df.append(df2)
