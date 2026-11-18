import pandas as pd                 # Импорт необходимых библиотек
import numpy as np
import sys                          #   Для корректного выхода из программы
import datetime                     # Для вычисления продолжительности работы программы

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

#       Получение данных из файлов (первая часть данных ввиде чисел)
roller=pd.read_csv('roller.csv', sep=';', encoding='utf-8', header=0, index_col=False)
sleeve=pd.read_csv('sleeve.csv', sep=';', encoding='utf-8', header=0, index_col=False)
ring=pd.read_csv('ring.csv', sep=';', encoding='utf-8', header=0, index_col=False)
#       Переименовываем столбцы для корректной работы с датафреймом
roller = roller.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'})   #, inplace=True)
sleeve = sleeve.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'})   #, inplace=True)
ring = ring.rename(columns={'УИН': 'ID', 'РезИзмерения': 'Size'})       #, inplace=True)
#       Определяем короткий номер детали (No) yymmddnnn (9 знаков)
roller['No'] = roller['ID'] % 1000000000
sleeve['No'] = sleeve['ID'] % 1000000000
ring['No'] = ring['ID'] % 1000000000
#       Получение данных из файлов (вторая часть: УИН (ID) - текст, 15 знаков)
roller['ID'] = pd.read_csv('roller.csv', 
                            dtype={'УИН': str}, sep=';', encoding='utf-8', header=0, index_col=False)['УИН']
sleeve['ID'] = pd.read_csv('sleeve.csv',
                            dtype={'УИН': str}, sep=';', encoding='utf-8', header=0, index_col=False)['УИН']
ring['ID'] = pd.read_csv('ring.csv',
                          dtype={'УИН': str}, sep=';', encoding='utf-8', header=0, index_col=False)['УИН']

#   Ввод критериев подбора и количества сборок (0 - для подбора всех вариантов сборок)

#       1. Параметры зазора: delta_min, delta_max
delta_min = float(input('Введите минимальный зазор: '))
delta_max = float(input('Введите максимальный зазор: '))
#       2. Количество сборок (0 - для подбора всех вариантов сборок)
n_builds = int(input('Введите количество сборок (0 - для подбора всех вариантов): '))

x1 = datetime.datetime.now()

#   Вывод заданных условий подбора сборок (для удобства)
print('\n', '\n')
print('Зазор: ', delta_min, ' - ', delta_max)
if n_builds == 0:
    print('Количество запрашиваемых сборок: все варианты', '\n')
else:
    print('Количество запрашиваемых сборок: ', n_builds, '\n')
#   Подсчёт общего количества вариантов подбора деталей.
total_combinations = len(ring) * len(sleeve) * len(roller)
print('Общее количество вариантов подбора деталей: ', total_combinations, '\n')

#   Создание  датафрейма сборок, удовлетворяющих критериям подбора
#   Delta = ring_size - (sleeve_size + 2 * roller_size)

#       Преобразуем значения в массивы numpy для ускорения вычислений
roller_sizes = roller['Size'].to_numpy()
sleeve_sizes = sleeve['Size'].to_numpy()
ring_sizes = ring['Size'].to_numpy()
#       Собственно, сам перебор по всем вариантам подбора деталей (тройки Ring, Sleeve, Roller)
result = []         #   Результирующий список numpy

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
#       Датафрейм сборки с найденными вариантами подбора
likage = pd.DataFrame(result)

#   Вывод информации о найденных вариантах подбора

if len(likage) == 0:
    print('Нет вариантов подбора, удовлетворяющих критериям зазора.')
    sys.exit()
#print('\n')
print('Количество найденных вариантов подбора:', len(likage))

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
out_likage = pd.DataFrame(columns=['Ring_No', 'Sleeve_No', 'Roller_No'])    #   Выходной датафрейм сборок-подборок
                                                                            #   Пока - пустой.

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
    out_likage = pd.concat([out_likage, result_out.iloc[[0]]], ignore_index=True)

        #   Удаление выбранной сборки из входного датафрейма сборок.

    selected = out_likage.iloc[-1]
    in_likage = in_likage.loc[~in_likage.eq(selected, axis="columns").any(axis=1)]

    n_builds_counter += 1
        
#   Конец цикла подбора.

#   Преобразование датафрейма сборок с короткими номерами деталей в строковые значения,
#   т.к. далее арифметика номеров будет мешать.
out_likage = out_likage.astype(str)

print('Выбранные сборки: ', '\n', out_likage, '\n')
print('Количество сборок: ', len(out_likage))

#       Выбор (поиск) УИН (ID) найденных деталей в исходном файле Колец.

ring_id = ring["ID"].astype("string")
parts = []

for ring_no in out_likage["Ring_No"].dropna().astype(str):
    if ring_no:  # пустая строка совпала бы с любым ID
        mask = ring_id.str.contains(ring_no, regex=False, na=False)
        parts.append(ring.loc[mask])

ring_filtered = (
    pd.concat(parts, ignore_index=True)
    if parts
    else ring.iloc[0:0].copy()
)
ring_filtered = ring_filtered.drop(columns=["No"])

#       Выбор (поиск) УИН (ID) найденных деталей в исходном файле Втулок (внутренних колец).
#
#   Из-за нарушения технологии маркировки, а именно - отсутствия сквозной маркировки
#   для двух разных видов внутренних колец, короткие номера, полученные из исходного
#   файла могут быть не уникальными. Это не приводит к краху работы программы, но
#   нарушает принцип "дефицитности" подбора деталей. Подбор дубликатов может быть не точным.

sleeve_id = sleeve["ID"].astype("string")
parts = []

for sleeve_no in out_likage["Sleeve_No"].dropna().astype(str):
    if sleeve_no:  # пустая строка совпала бы с любым ID
        mask = sleeve_id.str.contains(sleeve_no, regex=False, na=False)
        mask1 = mask & ~(mask & (mask.cumsum() > 1)) #   Добавка для удаления дубликатов в маске
        if mask1.sum() < mask.sum():
            print('Внимание! В исходном файле обнаружены дубликаты' \
            ' короткого номера внутренних колец:')
            print(sleeve.loc[mask].copy())
            print('Подбор по критериям может быть не точным.', '\n')
        parts.append(sleeve.loc[mask1].copy())

sleeve_filtered = (
    pd.concat(parts, ignore_index=True)
    if parts
    else sleeve.iloc[0:0].copy()
)
sleeve_filtered = sleeve_filtered.drop(columns=["No"])

#       Выбор (поиск) УИН (ID) найденных деталей в исходном файле Роликов.

roller_id = roller["ID"].astype("string")
parts = []

for roller_no in out_likage["Roller_No"].dropna().astype(str):
    if roller_no:  # пустая строка совпала бы с любым ID
        mask = roller_id.str.contains(roller_no, regex=False, na=False)
        parts.append(roller.loc[mask])

roller_filtered = (
    pd.concat(parts, ignore_index=True)
    if parts
    else roller.iloc[0:0].copy()
)
roller_filtered = roller_filtered.drop(columns=["No"])

#   ???     Вывод информации о сборках в начальном формате (15 знаков)
#   ???     и информации о зазорах (если необходимо)

result_K = pd.concat([ring_filtered, sleeve_filtered, roller_filtered], axis=1, )     # ignore_index=True

#   Вывод информации о выбранной сборке.
name_builds = str(n_builds)
if n_builds == 0:
    name_builds = 'All'
name_outfile = 'out_likage_' + str(int(delta_min * 1000)) + \
    '_' + str(int(delta_max * 1000)) + '_' + str(name_builds) + '.csv'

result_K.to_csv(name_outfile, sep=';', encoding='utf-8', index=False)
print('Результат подбора сохранен в файле: ', name_outfile, '\n')
#result_K.to_excel('out_file.xlsx', index=False, )          # Такое себе, для анализа
print(result_K, '\n')
x2 = datetime.datetime.now()
x_delta = x2 - x1
print('Время поиска комбинаций ',
      'без учёта чтения исходников и ввода условий: ', x_delta)