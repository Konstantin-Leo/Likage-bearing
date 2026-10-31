import pandas as pd                 # Импорт необходимых библиотек
import numpy as np
import sys                          #   Для корректного выхода из программы

#   Подпрограмма отбора уникальных значений по критерию К.

def selection(frame_in, K):
    test_out = frame_in[K].value_counts()       #   Подсчёт количества уникальных значений в столбце K
    ddd = test_out.sort_values()                #   Сортировка значений по возрастанию, чтобы создать список,
                                                #   в котором на первом месте будет дефицитная деталь
    if ddd.empty:                               #   куда будут записаны те K, у которых минимальная частота
        return frame_in.iloc[0:0]
    result_K = []                              
    result_K.append(ddd.index[0])
    for i in range(1, len(ddd)):
        if ddd.iloc[i] != ddd.iloc[i - 1]:
            break
        result_K.append(ddd.index[i])
    result_s = frame_in[frame_in[K].isin(result_K)]
    return result_s


#   Получение данных из файлов
roller=pd.read_csv('C:/TMP/Подбор/roller.csv', sep=';', encoding='utf-8', header=0, index_col=False)
sleeve=pd.read_csv('C:/TMP/Подбор/sleeve.csv', sep=';', encoding='utf-8', header=0, index_col=False)
ring=pd.read_csv('C:/TMP/Подбор/ring.csv', sep=';', encoding='utf-8', header=0, index_col=False)

#   Формирование входных данных в виде датафреймов (УИН, размер, номер детали)

#   Переименовываем столбцы для корректной работы с датафреймом
roller.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'}, inplace=True)
sleeve.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'}, inplace=True)
ring.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'}, inplace=True)

#   Определяем уникальный номер детали (No) как остаток от деления УИН на 1 000 000 000
roller['No'] = roller['ID'] % 1000000000
sleeve['No'] = sleeve['ID'] % 1000000000
ring['No'] = ring['ID'] % 1000000000

#   Ввод критериев подбора и количества сборок (0 - для подбора всех вариантов сборок)
#   1. Параметры зазора: delta_min, delta_max
delta_min = float(input('Введите минимальный зазор: '))
delta_max = float(input('Введите максимальный зазор: '))
#   2. Количество сборок (0 - для подбора всех вариантов сборок)
n_builds = int(input('Введите количество сборок (0 - для подбора всех вариантов): '))

print('\n')
print('Зазор: ', delta_min, ' - ', delta_max)
if n_builds == 0:
    print('Количество запрашиваемых сборок: все варианты', '\n')
else:
    print('Количество запрашиваемых сборок: ', n_builds, '\n')

#   Создание  датафрейма сборок, удовлетворяющих критериям подбора
#   Delta = ring_size - (sleeve_size + 2 * roller_size)

roller_sizes = roller['Size'].to_numpy()
sleeve_sizes = sleeve['Size'].to_numpy()
ring_sizes = ring['Size'].to_numpy()

result = []

for ring_index, ring_size in enumerate(ring_sizes):
    for sleeve_index, sleeve_size in enumerate(sleeve_sizes):
        delta = ring_size - (sleeve_size + 2 * roller_sizes)
        roller_indices = np.flatnonzero(
            (delta_min <= delta) & (delta <= delta_max)
        )

        for roller_index in roller_indices:
            result.append({
                'Ring_No': ring.loc[ring_index, 'No'],
                'Sleeve_No': sleeve.loc[sleeve_index, 'No'],
                'Roller_No': roller.loc[roller_index, 'No'],
 #               'Delta': delta[roller_index]  #   Лишний столбец, будет мешать при удалении строк, т.к. хочет учавствовать в сравнении.
            })

#  Датафрейм сборки с найденными вариантами подбора
likage = pd.DataFrame(result)

if len(likage) == 0:
    print('Нет вариантов подбора, удовлетворяющих критериям зазора.')
    sys.exit()
#   Вывод информации о найденных вариантах подбора
#print('\n')
print('Количество найденных вариантов подбора:', len(likage))
#   Сохранение результатов в CSV-файл  (для проверки корректности работы алгоритма)
#likage.to_csv('C:/TMP/Подбор/likage.csv', sep=';', encoding='utf-8', index=False)

#   Небольшой анализ (предварительный вывод)
unic_sborka = likage[[ 'Ring_No','Sleeve_No','Roller_No' ]].nunique()
print('Количество уникальных сборок, не более:', unic_sborka.min(), '\n')
print('Количество уникальных колец:', unic_sborka.iloc[0])
print('Количество уникальных втулок:', unic_sborka.iloc[1])
print('Количество уникальных роликов:', unic_sborka.iloc[2])

#   Определение порядка подбора деталей
#   Начинаем с самой дефицитной детали; заканчиваем самой массовой деталью.
#   При прочих равных высший приоритет - Ring; ниже - Sleeve; самый низкий - Roller.
if unic_sborka.iloc[2] < unic_sborka.iloc[1] and unic_sborka.iloc[2] < unic_sborka.iloc[0]:
    K1 = 'Roller_No'
    if unic_sborka.iloc[1] < unic_sborka.iloc[0]:
        K2 = 'Sleeve_No'
        K3 = 'Ring_No'
    else:
        K2 = 'Ring_No'
        K3 = 'Sleeve_No'
elif unic_sborka.iloc[1] <= unic_sborka.iloc[2] and unic_sborka.iloc[1] < unic_sborka.iloc[0]:
    K1 = 'Sleeve_No'
    if unic_sborka.iloc[2] < unic_sborka.iloc[0]:
        K2 = 'Roller_No'
        K3 = 'Ring_No'
    else:
        K2 = 'Ring_No'
        K3 = 'Roller_No'
elif unic_sborka.iloc[0] <= unic_sborka.iloc[2] and unic_sborka.iloc[0] <= unic_sborka.iloc[1]:
    K1 = 'Ring_No'
    if unic_sborka.iloc[2] < unic_sborka.iloc[1]:
        K2 = 'Roller_No'
        K3 = 'Sleeve_No'
    else:
        K2 = 'Sleeve_No'
        K3 = 'Roller_No'

print('\n', 'K1 =', K1, 'K2 =', K2, 'K3 =', K3, '\n')

#   Начальные условия для цикла подбора
flag = True                                 #   Флажек, для обработки при 0-длине фрейма
n_builds_counter = 0                        #   Счетчик сборок
in_likage = likage.copy()                   #   Входной датафрейм сборок
out_likage = pd.DataFrame(columns=['Ring_No', 'Sleeve_No', 'Roller_No'])    #, 'Delta'])    #   Выходной датафрейм сборок-подборок

#print('тест входного фрейма ', '\n', in_likage, '\n')

#   Цикл подбора. Создание выходного датафрейма сборок.
#   
while flag and (n_builds == 0 or n_builds_counter < n_builds):

    result_s1 = selection(in_likage, K1)          #   Подбор по критерию K1
    if len(result_s1) == 0:
        flag = False
        break
    result_s2 = selection(result_s1, K2)        #   Подбор по критерию K2
    if len(result_s2) == 0:
        flag = False
        break
    result_s3 = selection(result_s2, K3)        #   Подбор по критерию K3
    if len(result_s3) == 0:
        flag = False
        break

        #   Однозначный выбор сборки, если критерии K1, K2, K3
        #   не дали однозначного результата.
        #   Выбираем самую старую деталь (самый маленький номер детали)
        #   из всех найденных вариантов подбора К3.

    result_out = result_s3.sort_values(by=K3, ascending=True)
#    result_out = result_out.drop(columns=['Delta'])
    out_likage = pd.concat([out_likage, result_out.iloc[[0]]], ignore_index=True)

        #   Удаление выбранной сборки из входного датафрейма сборок.

#   Перый вариант удаления строк из likage 
#   (удаляет только одну строку с найденой сборкой)
#    likage_temp = in_likage[~(in_likage.eq(out_likage.iloc[-1])).any(axis=1)]
#    in_likage = likage_temp.copy()      #   Обновление входного датафрейма сборок

#   Второй вариант удаления строк из likage
    selected = out_likage.iloc[-1]
    in_likage = in_likage.loc[~in_likage.eq(selected, axis="columns").any(axis=1)]

    n_builds_counter += 1
        
#   Конец цикла подбора.


#   Вывод информации о выбранной сборке.
name_builds = str(n_builds)
if n_builds == 0:
    name_builds = 'All'
name_outfile = 'C:/TMP/Подбор/out_likage_' + str(int(delta_min * 1000)) + \
    '_' + str(int(delta_max * 1000)) + '_' + str(name_builds) + '.csv'
#print(name_outfile)
out_likage.to_csv(name_outfile, sep=';', encoding='utf-8', index=False)
#out_likage.to_csv('C:/TMP/Подбор/out_likage.csv', sep=';', encoding='utf-8', index=False)
print('Выбранные сборки: ', '\n', out_likage, '\n')
print('Количество сборок: ', len(out_likage))
print('Результат подбора сохранен в файле: ', name_outfile, '\n')

#   ???     Вывод информации о сборках в начальном формате (13 знаков)
#   ???     и информации о зазорах (если необходимо)

                    # Преобразуем значения out_likage в set (множество) для ускорения поиска
                    # Для начала - Ring.
search_set = set(out_likage.loc[:, 'Ring_No'].astype(str))
                    # Проверяем каждую строку исходного датафрейма:
                    # есть ли хоть одно значение из search_set внутри строки
mask = ring.iloc[:, 0].astype(str).apply(
    lambda x: any(term in x for term in search_set)
)
result_K1 = ring[mask]
result_K1 = result_K1.drop(columns=['No'])  # Удаляем лишние столбцы.

                    #   Далее - Sleeve.
search_set = set(out_likage.loc[:, 'Sleeve_No'].astype(str))
mask = sleeve.iloc[:, 0].astype(str).apply(
    lambda x: any(term in x for term in search_set)
)
result_K2 = sleeve[mask]
result_K2 = result_K2.drop(columns=['No'])  # Удаляем лишние столбцы.

                    #   Наконец - Roller.
search_set = set(out_likage.loc[:, 'Roller_No'].astype(str))
mask = roller.iloc[:, 0].astype(str).apply(
    lambda x: any(term in x for term in search_set)
)
result_K3 = roller[mask]
result_K3 = result_K3.drop(columns=['No'])  # Удаляем лишние столбцы.

result_K = pd.concat([result_K1, result_K2, result_K3], axis=1, ignore_index=True)
print(result_K)