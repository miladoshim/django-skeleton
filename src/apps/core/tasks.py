# import os
# import ffmpeg
from celery import shared_task

from apps.core.services.sms_service import Kavenegar

# from easy_thumbnails.files import generate_all_aliases
# from celery.signals import task_prerun, task_postrun
# from zeal import setup, teardown
# from django.conf import settings


@shared_task(bind=True, max_retries=3)
def send_comment_approved_notification(self, user: str):
    try:
        msg = f"{user.get_full_name} عزیز \n دیدگاه شما مورد تایید قرار گرفت. \n کوکوند"
        return Kavenegar.send_sms(receptor=user.mobile, message=msg)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# @shared_task
# def generate_thumbnails(model, pk, field):
#     instance = model._default_manager.get(pk=pk)
#     fieldfile = getattr(instance, field)
#     generate_all_aliases(fieldfile, include_global=True)


# @shared_task
# def process_video_task(post_id, file_path, resolution):
#     """Process video using FFmpeg."""
#     output_file = f"media/videos/{post_id}_{resolution}.mp4"
#     try:
#         ffmpeg.input(file_path).output(
#             output_file, vf=f"scale=-2:{480 if resolution == '480p' else 720}"
#         ).run()
#         print(f"{resolution} video processed: {output_file}")
#         Video.objects.create(
#             post_id=post_id,
#             file_name=output_file,
#             file_path=f"/{output_file}",
#             video_format=resolution,
#         )
#     except Exception as e:
#         print(f"Failed to process {resolution} video: {e}")


# @shared_task
# def process_image_task(post_id, file_path):
#     """Process image to create WebP and JPG formats."""
#     output_dir = "media/images"
#     os.makedirs(output_dir, exist_ok=True)
#     base_name = os.path.splitext(os.path.basename(file_path))[0]

#     for format in ["webp", "jpg"]:
#         output_file = os.path.join(output_dir, f"{base_name}.{format}")
#         try:
#             ffmpeg.input(file_path).output(
#                 output_file,
#                 **({"compression_level": 6} if format == "webp" else {"q:v": 85}),
#             ).run()
#             print(f"Image processed: {output_file}")
#         except Exception as e:
#             print(f"Failed to process image to {format}: {e}")


# @shared_task
# def process_audio_task(post_id, file_path):
#     """Process audio to normalize and adjust bitrate."""
#     output_file = f"media/audio/{post_id}.aac"
#     try:
#         ffmpeg.input(file_path).output(
#             output_file, acodec="aac", audio_bitrate="128k", af="volume=0.8"
#         ).run()
#         print(f"Audio processed: {output_file}")
#     except Exception as e:
#         print(f"Failed to process audio: {e}")


# @task_prerun.connect()
# def setup_zeal(*args, **kwargs):
#     setup()


# @task_postrun.connect()
# def teardown_zeal(*args, **kwargs):
#     teardown()
