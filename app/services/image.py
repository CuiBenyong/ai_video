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

def generate_images(task_id: str,
                    text: str,
                    style: str,
                    video_aspect: VideoAspect = VideoAspect.portrait,
                    num: int = 1,):
    with UsingMysql(log_time=True) as um:
        videos = um.fetch_all("select * from ai_task_video_gen")
        logger.info(f"videos: {videos}")
        
            
    images = []
    access_token = getAccessToken()
    # url  = "https://aip.baidubce.com/rpc/2.0/ernievilg/v1/txt2img?access_token=" + access_token
    url = 'http://192.168.10.102:3000/generateImage'

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
    
    return res["data"]["taskId"]

async def get_images(task_id: str):
    access_token = getAccessToken()
    url  = "http://192.168.10.102:3000/result" + access_token

    params = {
        "taskId": task_id,
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=params)
    res = json.loads(response.text)
    
    waiting = res["data"]["waiting"]
    
    if waiting == 0:
        return res["data"]
    else:
        await asyncio.sleep(waiting)
        return get_images(task_id)

if __name__ == "__main__":
    print("ls")