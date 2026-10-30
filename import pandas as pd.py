import pandas as pd
from IPython.display import display

df = pd.read_csv(
    "likage.csv",
    sep=";",           # замените на нужный разделитель
    encoding="utf-8",  # например, "cp1251", если файл в этой кодировке
    decimal=".",       # если десятичный разделитель — запятая
)

display(df)