import asyncio
import os
from pathlib import Path
from worker import generate_list_image

import redis

from config import settings
from sql_app.models import List
from sql_app.schemas import CreateListImageRequest

redis_url = settings.redis_url
redis_client = redis.from_url(redis_url)

current_directory = Path(__file__).parent
root_directory = current_directory.parent
images_path = (root_directory / 'static/img/scenes').as_posix()
print(f'images_path={images_path}')



class ListImageService:
    @classmethod
    def get_prompt_template_output(cls, content: str, title: str, aesthetic: str):
        return content.format(
            book_title=title,
            aesthetic=aesthetic.title
        )

    @classmethod
    def generate_list_image(cls, db, list_image_request: CreateListImageRequest):
        print('creating generate_list_image task')
        task = generate_list_image.delay(
            list_id=list_image_request.list_id,
            images_path=images_path,
        )
        redis_client.set(task.id, 'init')
        return task.id, 'Task created'
        