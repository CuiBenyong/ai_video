
from urllib.request import Request

from app.models.schema import RegisterParams


def register(body: RegisterParams):
   print(body)
   