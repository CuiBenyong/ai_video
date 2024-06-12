from fastapi import Request, Response
from app.controllers.v1.base import new_router
from app.models.schema import RegisterResponse, RegisterRequest, LoginRequest
from app.services import user
from app.utils import utils

# 认证依赖项
# router = new_router(dependencies=[Depends(base.verify_token)])
router = new_router()


@router.post("/register", response_model=RegisterResponse, summary="Create an account for the user")
def register(res: Response, req: RegisterRequest):

    body = req.dict()
    name = body['username'] or utils.generate_random_username_weighted()
    if not body['phone']:
        return utils.get_response(400, "phone is required")
    if not body['password']:
        return utils.get_response(400, "password is required")
    response = user.register(phone=body['phone'], password=body['password'], username=name)
    res.set_cookie("token", response['token'], httponly=True, max_age=60*60*24*7)
    return utils.get_response(200, response)

@router.post("/login", response_model=RegisterResponse, summary="Login to the user account")
def login(res: Response, req: LoginRequest):
    print(f"login {res}")
    body = req.dict()
    if not body['phone']:
        return utils.get_response(400, "phone is required")
    if not body['password']:
        return utils.get_response(400, "password is required")
    response = user.login(phone=body['phone'], password=body['password'])
    res.set_cookie("token", response['token'], httponly=True, max_age=60*60*24*7)
    return utils.get_response(200, response)