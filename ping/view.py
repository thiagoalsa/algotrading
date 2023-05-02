from typing import Dict
from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/ping",
    summary="It return an empty dictionary",
    response_description="It return an empty dictionary to check if the service is working",
    response_model=Dict,
)
def ping() -> Dict:
    """
    This endpoint return an empty dictionary if every thing works as expected.
    Returns:
        It returns an empty dictionary.
    """

    return {}