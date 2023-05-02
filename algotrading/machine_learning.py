from datetime import datetime
from sklearn.model_selection import train_test_split
import MetaTrader5 as mt5
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
import numpy as np

pd.set_option('display.max_columns', 500)  # número de colunas mostradas
pd.set_option('display.width', 1500)  # max. largura máxima da tabela exibida

# estabelecemos a conexão ao MetaTrader 5
mt5.initialize()

# obtemos o número de transações no histórico
from_date = datetime(2022, 1, 1)
to_date = datetime.now()

# obtemos no intervalo especificado as transações com base em símbolos cujos nomes contenham "*GBP*"
deals = mt5.history_deals_get(from_date, to_date, group="*GBPUSD*")




# exibimos essas transações como uma tabela usando pandas.DataFrame

df = pd.DataFrame(list(deals), columns=deals[0]._asdict().keys())
print(df)


#df['time'] = pd.to_datetime(df['time'], unit='s')
#df['time_msc'] = pd.to_datetime(df['time_msc'], unit='ns')
print(df)
print("")

# Limpando o DataFrame

colunas_selecionadas = ['time', 'time_msc', 'type', 'entry', 'reason', 'price', 'profit']
df_limpo = df.filter(items=colunas_selecionadas)
print(df_limpo[68:])
print(df_limpo)
df = df_limpo.query('profit != 0')
print(df)
df.to_csv('HistoricoMT5.csv', index=True)

df['result_ml'] = np.where(df['profit'] > 0, 1, 0)

df = df.drop('profit', axis=1)
print(df)



#Criando variaveis preditoras e variaveis alvo

y = df['result_ml']
x = df.drop('result_ml', axis=1)


x_treino, x_teste, y_treino, y_teste = train_test_split(x, y, test_size=0.3)

modelo = ExtraTreesClassifier()
modelo.fit(x_treino, y_treino)

resultado = modelo.score(x_teste, y_teste)
print('Acuracia: ', resultado)
print(x_teste[:])
previsoes = modelo.predict(x_teste[:])
print(f'As Minhas previsoes sao: {previsoes}')
print(f'As verdadeiras sao : {y_teste[:]}')