from fastapi import Request, Response
from app.controllers.v1.base import new_router
from app.models.schema import RegisterResponse, RegisterRequest, LoginRequest, TaskListResponse, TaskHistoryRequest
from app.services import user
from app.utils import utils
from app.utils.mysql import UsingMysql, get_uid
import math
from loguru import logger


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

@router.post("/logout", summary="Logout the user account")
def logout(res: Response):
    res.delete_cookie("token")
    return utils.get_response(200, "logout successfully")

@router.post("/tasks_history",response_model=TaskListResponse, summary="Get the user account information")
def task_history(res: Response,request: Request, body: TaskHistoryRequest):
    page_size = body.page_size or 10
    offset = body.offset or 1
    
    uid = get_uid(request=request)
    if not uid:
        return utils.get_response(401, "Unauthorized")
    with UsingMysql() as um:
        sql = f"select * from ai_task_video_gen where uid = {uid} order by created_at desc limit {page_size} offset {offset-1}"
        count = f"select count(vid_id) from ai_task_video_gen where uid = {uid}"
        total = um.get_count(count, count_key="count(vid_id)")
        logger.info(f"query: {sql}")
        tasks = um.fetch_all(sql)
      
        logger.info(f"tasks: {tasks}")
        res = {
            "list": tasks,
            "page_size": page_size,
            "offset": offset,
            "total": total,
            "total_page": math.ceil(total/page_size)
        }
    return utils.get_response(200, res)