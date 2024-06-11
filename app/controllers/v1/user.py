from fastapi import Request
from app.controllers.v1.base import new_router
from app.models.schema import RegisterResponse, RegisterParams
from app.services import user
from app.utils import utils

# 认证依赖项
# router = new_router(dependencies=[Depends(base.verify_token)])
router = new_router()


@router.get("/register", response_model=RegisterResponse, summary="Create an account for the user")
def register(request: Request, body: RegisterParams):
    print(f"register{body}")
    account = user.register({
        "username": body.username,
        "password": body.password,
        "email": body.email
    })
    response = {
        "account": account
    }
    return utils.get_response(200, response)
