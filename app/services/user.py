
import hashlib
from app.models.schema import RegisterRequest
from app.utils.mysql import UsingMysql
from app.utils.utils import generate_token


def register(phone: str, username: str, password: str):
   print(f"body: {phone} {username} {password}")
   with UsingMysql(log_time=True) as um:
      sql = "INSERT INTO `ai_user` (`username`, `phone`, `password`) VALUES (%s, %s, %s)"
      md5_hash = hashlib.md5(password.encode('utf-8')).hexdigest()

      um.cursor.execute(sql, username, phone, md5_hash)
      if um.cursor.rowcount == 1:
         user = um.fetch_one("SELECT * FROM `ai_user` WHERE `phone` = %s", phone)
         token = generate_token()
         um.cursor.execute("INSERT INTO `ai_user_token` (`uid`, `token`) VALUES (%s, %s)", user.uid, token)
         if  um.cursor.rowcount == 1:
            return {"code": 0, "msg": "注册成功", "token": token }
         return {"code": 1, "msg": "注册失败"}
      if um.cursor.rowcount == 0:
        return {"code": 1, "msg": "注册失败"}
   return {"code": 0, "msg": "注册成功"}