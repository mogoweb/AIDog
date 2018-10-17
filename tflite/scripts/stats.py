# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style='white')

df = pd.read_csv('results.txt', sep='_', names=['label', 'p1', 's1', 'p2', 's2', 'p3', 's3'])

# Top 1 3 5 分类正确率
df['accuracy'] = df['label'] == df['p1']
print('Top 1 分类正确率：%f' % (np.sum(df['accuracy']) / len(df)))
df['accuracy3'] = (df['label'] == df['p1']) | (df['label'] == df['p2']) | (df['label'] == df['p3']) 
print('Top 3 分类正确率：%f' % (np.sum(df['accuracy3']) / len(df)))

# 每种狗狗分类正确率
accuracies = df.groupby('label')['accuracy'].sum() / df.groupby('label')['accuracy'].count()
accuracies.sort_values(inplace=True)
print('正确率后五：')
for i in range(5):
	print('-', accuracies.index[i], accuracies[i])
print('正确率前五：')
for i in range(5):
	print('-', accuracies.index[len(accuracies) - 1 - i], accuracies[len(accuracies) - 1 - i])
plt.figure(figsize=(6, 6))
sns.barplot(accuracies.values, accuracies.index)
plt.yticks([])
plt.ylabel('')
sns.despine(top=True, right=True, bottom=True, left=True)
plt.savefig('Top1分类正确率.pdf')

# 一种狗狗被错误分类为另一种狗狗的数量
dogs = list(df['label'].sort_values().unique())
errors = {}
for i in range(len(df)):
	label = df['label'][i]
	pred = df['p1'][i]
	if label != pred:
		key = label + '_' + pred
		errors[key] = errors.get(key, 0) + 1 
errors = sorted(errors.items(), key=lambda x:x[1], reverse=True)
print(errors[:10])

# 热力图
counts = {di:{dj:0 for dj in dogs} for di in dogs}
for i in range(len(df)):
	label = df['label'][i]
	pred = df['p1'][i]
	counts[label][pred] += 1
matrix = pd.DataFrame({di:[counts[di][dj] for dj in dogs] for di in dogs})
matrix.index = dogs
f, ax = plt.subplots(figsize=(8, 8))
sns.heatmap(matrix, cmap=sns.diverging_palette(220, 10, as_cmap=True), vmax=10, center=0, square=True, linewidths=.5, cbar=False, xticklabels=False, yticklabels=False)
plt.savefig('不同类别狗狗分类热力图.pdf')
