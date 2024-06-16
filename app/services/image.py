import json
import os
import random
from urllib.parse import urlencode

import math
import re
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
    clip1 = ImageClip(os.path.join(utils.task_dir(), image), duration=duration)
    videocct = concatenate_videoclips([clip1])
    videoPath = f"{base_dir}/{image}.mp4"
    videocct.write_videofile(videoPath, codec="libx264", fps=fps)
    return videoPath

def generate_images(task_id: str,
                    text: str,
                    style: str,
                    video_aspect: VideoAspect = VideoAspect.portrait,
                    num: int = 1,):
    images = []
    access_token = getAccessToken()
    # url  = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2img?access_token=" + access_token
    url = 'http://192.168.10.102:3000/generateImage'
    logger.info(f"generate_images: {url} {access_token}")  
    params = {
        "text": text,
        "style": style,
        "num": num,
        "resolution": video_aspect.value,
    }
        
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=params)
    res = json.loads(response.text)
    
    if "data" in res:
        log_id = res["log_id"]
        taskId = res["data"]["taskId"]
        with UsingMysql(log_time=True) as um:
            video = um.fetch_one("select * from ai_task_video_gen where task_id = %s", task_id)
            if video:
                sql = f"insert into ai_task_img_gen (vid_id, text_content, style, resolution, log_id, taskId) values (%s, %s, %s, %s, %s, %s)"
                um.execute(sql, video["vid_id"], text, style, video_aspect.value, log_id, taskId)
            else:
                raise Exception("video not found")
            
    return res["data"]["taskId"]

async def get_images(taskId: str):
    
    #1.先看目录下有没有已经下载好的图片，若有则直接返回图片路径
    
    file_path = os.path.join(utils.task_dir("images"), f"{taskId}.jpg")
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
    url  = "https://aip.baidubce.com/rpc/2.0/wenxin/v1/basic/getImg?access_token=" + access_token
    # url = 'http://192.168.10.102:3000/generateImage'
    logger.info(f"generate_images: {url} {access_token}")  
    params = {
       "taskId": taskId
    }
        
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=params)
    res = json.loads(response.text)
    
    if "data" in res:
        waiting = res["data"]["waiting"]
        if waiting:
            await asyncio.sleep(waiting)
            return get_images(taskId)
        else:
            img = res["data"]["img"]
            img = requests.get(img)
            with open(file_path, "wb") as f:
                f.write(img.content)
            return {
                "path": file_path
            }
    else:
        return {
            "path": None
        }


if __name__ == "__main__":
    print("ls")
