from typing import List, Union

import numpy as np
from fastapi import APIRouter
from requests import Response
from sklearn.ensemble import ExtraTreesClassifier

router = APIRouter()

modelo = ExtraTreesClassifier()


@router.get(
    "/predict",
    response_model= str,
)
def predict(x_teste: dict) -> str:
    """
    Returns:
    """
    previsoes = modelo.predict(x_teste["x_test"])

    return f"{previsoes}"


@router.get(
    "/train",
    response_model=str,

)
def train(data: dict) -> str:
    """
    Returns:
    """
    # print(data["x_treino"], data["y_treino"])
    modelo.fit(data["x_treino"], data["y_treino"])
    return "Model training"


