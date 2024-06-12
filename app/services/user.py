
import hashlib
from app.models.schema import RegisterRequest
from app.utils.mysql import UsingMysql
from app.utils.utils import generate_token
from loguru import logger


def register(phone: str, username: str, password: str):
   print(f"body: {phone} {username} {password}")
   with UsingMysql(log_time=True) as um:
      has = um.fetch_one("SELECT * FROM `ai_user` WHERE `phone` = %s OR `username` = %s", (phone, username))
      if has:
         return {"code": 1, "msg": "用户已存在"}
      sql = "INSERT INTO `ai_user` (`username`, `phone`, `password`) VALUES (%s, %s, %s)"
      md5 = hashlib.md5()
      md5.update(password.encode())
      md5_hash = md5.hexdigest()
      um.cursor.execute(sql, (username, phone, md5_hash))
      if um.cursor.rowcount == 1:
         user = um.fetch_one("SELECT * FROM `ai_user` WHERE `phone` = %s", phone)
         token = generate_token()
         logger.info(f"register user {user} token {token}")
         logger.info(f"INSERT INTO `ai_user_tokens` (`uid`, `token`) VALUES ({user['uid']}, {token})")
         um.cursor.execute("INSERT INTO `ai_user_tokens` (`uid`, `token`) VALUES (%s, %s)", (user['uid'], token))
         if  um.cursor.rowcount == 1:
            return {"code": 0, "msg": "注册成功", "token": token }
         return {"code": 1, "msg": "注册失败"}
      if um.cursor.rowcount == 0:
         return {"code": 1, "msg": "注册失败"}
   return {"code": 0, "msg": "注册成功"}

def login(phone: str, password: str):
   with UsingMysql(log_time=True) as um:
      md5 = hashlib.md5() 
      md5.update(password.encode())
      md5_hash = md5.hexdigest()
      user = um.fetch_one("SELECT * FROM `ai_user` WHERE `phone` = %s AND `password` = %s", (phone, md5_hash))
      if user:
         um.cursor.execute("DELETE FROM `ai_user_tokens` WHERE `uid` = %s", user['uid'])
         token = generate_token()
         um.cursor.execute("INSERT INTO `ai_user_tokens` (`uid`, `token`) VALUES (%s, %s)", (user['uid'], token))
         if  um.cursor.rowcount == 1:
            return {"code": 0, "msg": "登录成功", "token": token }
         return {"code": 1, "msg": "登录失败"}
      return {"code": 1, "msg": "账号或密码错误"}