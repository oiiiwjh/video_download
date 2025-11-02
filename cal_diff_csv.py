
import pandas as pd
import os
csv_list = os.listdir('/share/wjh/csv_share')
csv_200 = [csv for csv in csv_list if 'total_done_sample_200' in csv]
csv_500 = [csv for csv in csv_list if 'total_done_sample_500' in csv]
print(len(csv_200), len(csv_500))
print(csv_500)
total_csv_200 = pd.concat([pd.read_csv(f'/share/wjh/csv_share/{csv}') for csv in csv_200], ignore_index=True)
# total_csv_500 = pd.concat([pd.read_csv(f'/share/wjh/csv_share/{csv}') for csv in csv_500], ignore_index=True)
total_csv_500 = pd.read_csv(f'/share/wjh/csv_share/{csv_500[2]}')
print(total_csv_200.shape, total_csv_500.shape)
ids_200 = total_csv_200['id'].tolist()
ids_500 = total_csv_500['id'].tolist()
print(len(ids_200), len(ids_500))
# list做差集
ids_diff = list(set(ids_500) - set(ids_200))
print(len(ids_diff))

for i in range(len(csv_200)):
    pd_temp = pd.read_csv(f'/share/wjh/csv_share/{csv_200[i]}')
    ids_temp = pd_temp['id'].tolist()
    # ids_temp, ids_500
    # ids_diff = list(set(ids_temp) - set(ids_500))
    # 集合做交集
    ids_diff = list(set(ids_temp) & set(ids_500))
    if len(ids_diff) != 0:
        print(f'{csv_200[i]}: {len(ids_diff)}')
        print(len(ids_diff))
        print(ids_diff)
