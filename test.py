import numpy as np
import requests

ping = requests.get(f"http://127.0.0.1:8000/ping")
print("ping", ping.json())


o_que_voce_quer_prever = [[2], [4], [6], [8]]

x_dado_passado = [[1], [2], [3], [4]]
y_resultado_do_dado_passado = [10, 20, 30, 40]

train = requests.get(f"http://127.0.0.1:8000/train", json={"x_treino": x_dado_passado, "y_treino": y_resultado_do_dado_passado})
print("train", train.text)

predict = requests.get(f"http://127.0.0.1:8000/predict", json={"x_test": o_que_voce_quer_prever})
print("predict", np.array(predict.text))