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
    with UsingMysql(log_time=True) as um:
        videos = um.fetch_all("select * from ai_task_video_gen")
        logger.info(f"videos: {videos}")
        
            
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
    
    return res["data"]["taskId"]

def get_images(task_id: str):
    return {
        "style": "油画",
        "taskId": 1798207147175732651,
        "imgUrls": [
            {
                "image": "http://bj.bcebos.com/v1/ai-picture-creation/watermark/60d1e8cc4f6406c4dffdfa2976150872ex.jpg?authorization=bce-auth-v1%2FALTAKBvI5HDpIAzJaklvFTUfAz%2F2024-03-20T11%3A10%3A07Z%2F86400%2F%2F17ec73c2d89b68746f656a7f74beba2cab7de026ba30ab0ab7ca4fe980bf19ad",
                "img_approve_conclusion": "paas"
            }
        ],
        "text": "睡莲",
        "status": 1,
        "createTime": "2024-03-20 19:09:49",
        "img": "http://bj.bcebos.com/v1/ai-picture-creation/watermark/60d1e8cc4f6406c4dffdfa2976150872ex.jpg?authorization=bce-auth-v1%2FALTAKBvI5HDpIAzJaklvFTUfAz%2F2024-03-20T11%3A10%3A07Z%2F86400%2F%2F17ec73c2d89b68746f656a7f74beba2cab7de026ba30ab0ab7ca4fe980bf19ad",
        "waiting": "0",
        "path": f"{task_id}.jpg"
    }


if __name__ == "__main__":
    print("ls")