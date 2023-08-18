from pandas import DataFrame, read_csv
from numpy import Inf
from os import path
from pandas import DataFrame
from numpy import percentile

ROOT_DIR = path.dirname(path.dirname(path.abspath(__file__)))

container = 'daytrader'
metrics = ['rt_jmeter', 'pods']
experiments = ['pk1m', 'pkl1m', 'ml1m', 'pk3m', 'pkl3m', 'ml3m', 'pk5m', 'pkl5m', 'ml5m']

df = {}

for exp in experiments:
    for m in metrics:
        df[container + exp + m] = []

for m in metrics:
    df[m + '_min'] = Inf
    df[m + '_max'] = 0

path = ROOT_DIR + '/results/' + container + "/"
for exp in experiments:
    for m in metrics:
        data = read_csv(path + exp + '/train.csv')
        df[container + exp + m].append(data[m].to_numpy())

        if df[m + '_min'] >= min(df[container + exp + m][0]):
            df[m + '_min'] = min(df[container + exp + m][0])

        if df[m + '_max'] <= max(df[container + exp + m][0]):
            df[m + '_max'] = max(df[container + exp + m][0])

df2 = DataFrame.from_dict(df)

data = {}
for i_exp in range(0, len(experiments)):
    data[experiments[i_exp]] = {}

    for m in metrics:
        c = [0] * len(df[container + experiments[i_exp] + m][0])
        pm = df[container + experiments[i_exp] + m]
        c = [a + b for a, b in zip(c, *pm)]

        if m == 'pods':
            data[experiments[i_exp]][m] = c
        else:
            data[experiments[i_exp]][m] = df[container + experiments[i_exp] + m][0]

max_podss = []
erross_max = []

for i in data:
    max_podss.append(max(data[i]['pods']))
    erross_max.append(percentile(data[i]['rt_jmeter'], 95))

pods_max = len(data[i]['rt_jmeter']) * max(max_podss)
erros_max = max(erross_max)

csv_data = []

for experiment in ['pk1m', 'pk3m', 'pk5m', 'ml1m', 'ml3m', 'ml5m']:
    V = percentile(data[experiment]['rt_jmeter'], 95) / erros_max
    C = sum(data[experiment]['pods'])
    csv_data.append(
        [experiment[:-2], experiment[-2:], percentile(data[experiment]['rt_jmeter'], 95), erros_max, C, pods_max,
         (V * 0.5) + (0.5 * (C / pods_max))])

DataFrame(csv_data,
          columns=['Strategy', 'Forecasting Horizon', 'Performance (V)', 'Vmax', 'C', 'Cmax', 'AE0.5']).to_csv(
    ROOT_DIR + '/results/'+container+'/summary.csv', index=False)
