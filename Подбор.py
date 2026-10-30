import pandas as pd                 # Импорт необходимых библиотек
import numpy as np

#   Получение данных из файлов
roller=pd.read_csv('C:/TMP/Подбор/roller.csv', sep=';', encoding='utf-8', header=0, index_col=False)
sleeve=pd.read_csv('C:/TMP/Подбор/sleeve.csv', sep=';', encoding='utf-8', header=0, index_col=False)
ring=pd.read_csv('C:/TMP/Подбор/ring.csv', sep=';', encoding='utf-8', header=0, index_col=False)

#   Формирование входных данных в виде датафреймов (УИН, размер, номер детали)
roller['No'] = roller['УИН'] % 1000000000
sleeve['No'] = sleeve['УИН'] % 1000000000
ring['No'] = ring['УИН'] % 1000000000

roller.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'}, inplace=True)
sleeve.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'}, inplace=True)
ring.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'}, inplace=True)


#   Ввод критериев подбора
#   1. Параметры зазора: delta_min, delta_max
delta_min = float(input('Введите минимальный зазор: '))
delta_max = float(input('Введите максимальный зазор: '))
limit = int(input('Введите количество вариантов подбора: '))

#   Создание  датафрейма сборки
#   Объединение данных из трех файлов в один датафрейм
likage = pd.DataFrame(columns=['Ring_No', 'Sleeve_No', 'Roller_No'])        #   Датафрейм для хранения результатов подбора
#for i in range(len(ring)):
for i in range(0, limit):
    #for j in range(len(sleeve)):
    for j in range(0, limit):
        #for k in range(len(roller)):
        for k in range(0, limit):
            delta = ring.loc[i, 'Size'] - (sleeve.loc[j, 'Size'] + 2 * roller.loc[k, 'Size'])
            if delta_min <= delta <= delta_max:
                #likage = likage.append({'Ring_No': ring.loc[i, 'No'], 
                #                        'Sleeve_No': sleeve.loc[j, 'No'], 
                #                        'Roller_No': roller.loc[k, 'No']}, ignore_index=True)
                likage.loc[len(likage)] = [ring.loc[i, 'No'], sleeve.loc[j, 'No'], roller.loc[k, 'No']]
print('Количество найденных вариантов подбора:', len(likage))
likage.to_csv('C:/TMP/Подбор/likage.csv', sep=';', encoding='utf-8', index=False)