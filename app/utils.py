from config import settings


def get_scene_image_url(filename):
    if settings.in_cloud:
        # TODO: pull from a config setting
        return f"https://{settings.s3_bucket_name_media}.s3.amazonaws.com/{filename}"
    else:
        return f'/static/img/scenes/{filename}'

