from fastapi import Request
from app.controllers.v1.base import new_router
from app.models.schema import RegisterResponse, RegisterRequest
from app.services import user
from app.utils import utils

# 认证依赖项
# router = new_router(dependencies=[Depends(base.verify_token)])
router = new_router()


@router.get("/register", response_model=RegisterResponse, summary="Create an account for the user")
def register(request: Request, req: RegisterRequest):
    print(f"register {request}")
    body = req.dict()
    name = body['username'] or utils.generate_random_username_weighted()
    if not body['phone']:
        return utils.get_response(400, "phone is required")
    if not body['password']:
        return utils.get_response(400, "password is required")
    response = user.register(phone=body['phone'], password=body['password'], username=name)
    return utils.get_response(200, response)
