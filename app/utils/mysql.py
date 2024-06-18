# -*- coding: utf-8 -*-
# @Time : 2023/7/27 4:41 下午
# @Project : mysqlUtil
# @File : mysqlUtil.py
# @Version: Python3.9.8

import pymysql
from timeit import default_timer
from fastapi import Request, Depends, Path, BackgroundTasks, UploadFile, Cookie
from app.controllers import base
from app.models.exception import HttpException
from loguru import logger


host = 'mysql'
port = 3306
db = 'ai_video'
user = 'root'
password = '123456'

# 用PyMySQL操作数据库
def get_connection():
    print(f"mysql {user}@{host}:{port}:{password}")
    conn = pymysql.connect(host=host, port=port, db=db, user=user, password=password)
    return conn

# 使用with优化代码
class UsingMysql(object):
    def __init__(self, commit=True, log_time=True, log_label='总用时'):
        """
        :param commit: 是否在最后提交事务(设置为False的时候方便单元测试)
        :param log_time: 是否打印程序运行总时间
        :param log_label: 自定义log的文字
        """
        self._log_time = log_time
        self._commit = commit
        self._log_label = log_label

    def __enter__(self):
        # 如果需要记录时间
        if self._log_time is True:
            self._start = default_timer()
        # 在进入的时候自动获取连接和cursor
        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        conn.autocommit = False
        self._conn = conn
        self._cursor = cursor
        return self

    def __exit__(self, *exc_info):
        # 提交事务
        if self._commit:
            self._conn.commit()
        # 在退出的时候自动关闭连接和cursor
        self._cursor.close()
        self._conn.close()

        if self._log_time is True:
            diff = default_timer() - self._start
            print('-- %s: %.6f 秒' % (self._log_label, diff))

    # 一系列封装的业务方法
    # 返回count
    def get_count(self, sql, params=None, count_key='count(id)'):
        self.cursor.execute(sql, params)
        data = self.cursor.fetchone()
        if not data:
            return 0
        return data[count_key]

    def fetch_one(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchone()

    def fetch_all(self, sql, params=None):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def fetch_by_pk(self, sql, pk):
        self.cursor.execute(sql, (pk,))
        return self.cursor.fetchall()

    def update_by_pk(self, sql, params=None):
        self.cursor.execute(sql, params)

    @property
    def cursor(self):
        return self._cursor

def check_it():
    """
    """
    with UsingMysql(log_time=True) as um:
        um.cursor.execute("select count(id) as total from Product")
        data = um.cursor.fetchone()
        print("-- 当前数量: %d " % data['total'])


if __name__ == '__main__':
    check_it()


def get_uid(request: Request):
  request_id = base.get_task_id(request)
  logger.info(f"request {request} {request.cookies.keys()} {'token' in request.cookies.keys()}")
  if not request.cookies or 'token' not in request.cookies:
      raise HttpException(task_id=None, status_code=401, message=f"{request_id}: Unauthorized")
  token =request.cookies["token"]

  with UsingMysql() as ms:
      userToken = ms.fetch_one("SELECT uid FROM ai_user_tokens WHERE token = %s", (token))
      if not userToken:
          logger.error(f"token {token} is invalid.")
          raise HttpException(task_id=None, status_code=401, message=f"{request_id}: Unauthorized")
      uid = userToken["uid"]
  return uid