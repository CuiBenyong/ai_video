import json
import os
import random
from urllib.parse import urlencode
import polling
import math
import time
import asyncio

from loguru import logger

from app.config import config
from app.models import const
from app.models.schema import VideoParams, VideoConcatMode, VideoAspect

from app.services import llm, material, voice, video, subtitle
from app.services import state as sm
from app.utils import utils
from app.services.access_token import getAccessToken
from app.utils.mysql import UsingMysql

import requests
from typing import List
from moviepy.editor import *


def merge_image_to_video_moviepy(image, base_dir, duration):
    fps = 1
    clip1 = ImageClip(image, duration=duration)
    videocct = concatenate_videoclips([clip1])
    videoPath = f"{image}.mp4"
    videocct.write_videofile(videoPath, codec="libx264", fps=fps)
    return videoPath

def generate_images(task_id: str,
                    text: str,
                    style: str,
                    video_aspect: VideoAspect = VideoAspect.portrait,
                    num: int = 1,):
    images = []
    access_token = getAccessToken()
    url  = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2imgv2?access_token=" + access_token
    # url = 'http://192.168.10.106:3000/generateImage'
    logger.info(f"generate_images: {url}")  
    params = json.dumps({
        "prompt": text,
        "image_num": num,
        "width": 720,
        "height": 1280,
    })
        
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    logger.info(f"generate_images params: {params}")
    response = requests.request("POST", url, headers=headers, data=params)
    
    logger.info(f"generate_images response: {response.text}")
    res = json.loads(response.text)
    logger.info(f"generate_images: {res}")
    if "data" in res:
        log_id = res["log_id"]
        taskId = res["data"]["task_id"]
        with UsingMysql(log_time=True) as um:
            video = um.fetch_one("select * from ai_task_video_gen where task_id = %s", task_id)
            if video:
                sql = f"insert into ai_task_img_gen (vid_id, text_content, style, resolution, log_id, taskId) values (%s, %s, %s, %s, %s, %s)"
                logger.info(f"generate_images task_id: {task_id}")
                um.cursor.execute(sql, (video["vid_id"], text, style, video_aspect.value, log_id, taskId))
            else:
                raise Exception("video not found")
        return res["data"]["task_id"]
    else:
        with UsingMysql(log_time=True) as um:
          # video = um.fetch_one("select * from ai_task_video_gen where task_id = %s", task_id)
          um.cursor.execute(f"update ai_task_video_gen set status = {const.TASK_STATE_FAILED} where task_id = '{task_id}'")
        return None

def get_images(logId: str, task_id: str):
    
    #1.先看目录下有没有已经下载好的图片，若有则直接返回图片路径
    
    file_path = os.path.join(utils.task_dir(task_id), f"{logId}.jpg")
    if os.path.exists(file_path):
        return {
            "path": file_path
        }
    
    #2。请求接口查询生成状态
    #   若已生成，则下载图片并返回图片路径 
    #   若未生成，则根据接口返回的预计等待时间，等待后再次请求接口查询生成状态
    
    
    access_token = getAccessToken()
    # The line `# url  = "https://aip.baidubce.com/rpc/2.0/wenxin/v1/basic/getImg?access_token=" +
    # access_token` is a commented-out line of code in the Python script. It seems to be a placeholder
    # or a reference to an API endpoint for getting images using the Baidu AI platform.
    url  = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/getImgv2?access_token=" + access_token
    # url = 'http://192.168.10.106:3000/result'
    logger.info(f"generate_images: {url} {access_token}")  
    params = json.dumps({
       "task_id": logId
    })
        
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    # response = requests.request("POST", url, headers=headers, data=params)
    # logger.info(f"generate_images response.text: {response.text}")
    # res = json.loads(response.text)
    
    result = polling.poll(
        lambda: requests.request("POST", url, headers=headers, data=params).json(),
        check_success=lambda res: res["data"] and res["data"]["task_progress"] == 1,
        step=2,
        ignore_exceptions=(requests.exceptions.ConnectionError,),
        poll_forever=True
        )
    
    logger.info(f"generate_images result: {result}")
    
    if "data" in result:
        imgurl = result["data"]["sub_task_result_list"][0]['final_image_list'][0]['img_url']
        img = requests.get(imgurl)
        with open(file_path, "wb") as f:
            f.write(img.content)
            sql = f"update ai_task_img_gen set status = '{const.TASK_STATE_COMPLETE}', finished_at = '{time.time()}', data = '{imgurl}' where taskId = '{task_id}'"
            logger.info(f"generate_images update sql: {sql}")
            with UsingMysql(log_time=True) as um:
                um.cursor.execute(sql)
            return {
                "path": file_path
            }
    else:
        return {
            "path": None
        }

async def reGet(logId, task_id):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(get_images(logId, task_id))
    loop.close()
    if result["path"]:
        return result
    await asyncio.sleep(10)
    return reGet(logId, task_id=task_id)

if __name__ == "__main__":
    print("ls")
