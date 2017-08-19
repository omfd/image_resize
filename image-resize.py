from __future__ import print_function
import boto3
import os
import sys
import uuid

from PIL import Image
import PIL.Image
from resizeimage import resizeimage
import smartcrop

COVER_SIZE = [200, 150]
PROFILE_SIZE = [200, 200]

MOBILE_COVER_SIZE = [300, 100]
WEB_COVER_SIZE = [850, 250]
THUMBNAIL_SIZE = [200, 200]
SMART_THUMBNAIL_SIZE = [150, 150]
s3_client = boto3.client('s3')


def web_cover(image_source_path, resized_cover_path, img_type):
    sc_mobile = smartcrop.SmartCrop()
    crop_options = smartcrop.DEFAULTS
    imgWidth = WEB_COVER_SIZE[0]
    imgHeight = WEB_COVER_SIZE[1]
    imgResizeFactor = imgWidth / 100
    crop_options['width'] = 100
    crop_options['height'] = int(imgHeight / imgResizeFactor)
    crop_options['file_type'] = img_type
    img = Image.open(image_source_path)
    ret = sc_mobile.crop(img, crop_options)
    box = (ret['topCrop']['x'],
           ret['topCrop']['y'],
           ret['topCrop']['width'] + ret['topCrop']['x'],
           ret['topCrop']['height'] + ret['topCrop']['y'])
    img = Image.open(image_source_path)
    img2 = img.crop(box)
    img2.thumbnail((imgWidth, imgHeight), Image.ANTIALIAS)
    img2.save(resized_cover_path, crop_options['file_type'], quality=crop_options['save_quality'])


def mobile_cover(image_source_path, resized_cover_path, img_type):
    sc_mobile = smartcrop.SmartCrop()
    crop_options = smartcrop.DEFAULTS
    imgWidth = MOBILE_COVER_SIZE[0]
    imgHeight = MOBILE_COVER_SIZE[1]

    imgResizeFactor = imgWidth / 100
    crop_options['width'] = 100
    crop_options['height'] = int(imgHeight / imgResizeFactor)
    crop_options['file_type'] = img_type
    img = Image.open(image_source_path)
    ret = sc_mobile.crop(img, crop_options)
    box = (ret['topCrop']['x'],
           ret['topCrop']['y'],
           ret['topCrop']['width'] + ret['topCrop']['x'],
           ret['topCrop']['height'] + ret['topCrop']['y'])
    img = Image.open(image_source_path)
    img2 = img.crop(box)
    img2.thumbnail((imgWidth, imgHeight), Image.ANTIALIAS)
    img2.save(resized_cover_path, crop_options['file_type'], quality=crop_options['save_quality'])


def image_cover(image_source_path, resized_cover_path):
    with Image.open(image_source_path) as image:
        cover = resizeimage.resize_cover(image, COVER_SIZE)
        cover.save(resized_cover_path, image.format)


def image_profile(image_source_path, resized_cover_path):
    with Image.open(image_source_path) as image:
        profile = resizeimage.resize_cover(image, PROFILE_SIZE)
        profile.save(resized_cover_path, image.format)


def image_thumbnail(image_source_path, resized_cover_path, img_type):
    with Image.open(image_source_path) as image:
        thumbnail = resizeimage.resize_thumbnail(image, THUMBNAIL_SIZE)
    thumbnail.save(resized_cover_path, image.format)


def smart_thumbnail(image_source_path, resized_cover_path, img_type):
    sc_mobile = smartcrop.SmartCrop()
    crop_options = smartcrop.DEFAULTS
    imgWidth = SMART_THUMBNAIL_SIZE[0]
    imgHeight = SMART_THUMBNAIL_SIZE[1]

    imgResizeFactor = imgWidth / 100.0
    crop_options['width'] = 100
    crop_options['height'] = int(imgHeight / imgResizeFactor)
    crop_options['file_type'] = img_type
    img = Image.open(image_source_path)
    ret = sc_mobile.crop(img, crop_options)
    box = (ret['topCrop']['x'],
           ret['topCrop']['y'],
           ret['topCrop']['width'] + ret['topCrop']['x'],
           ret['topCrop']['height'] + ret['topCrop']['y'])
    img = Image.open(image_source_path)
    img2 = img.crop(box)
    img2.thumbnail((imgWidth, imgHeight), Image.ANTIALIAS)
    img2.save(resized_cover_path, crop_options['file_type'], quality=crop_options['save_quality'])


def handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)
        upload_path_cover = '/tmp/resized-{}'.format(key)
        upload_path_profile = '/tmp/resized-{}'.format(key)
        upload_path_thumbnail = '/tmp/resized-{}'.format(key)


        response = s3_client.get_object(Bucket=bucket, Key=key)
        img_type = response['ContentType'].split('/')[1].upper()
        s3_client.download_file(bucket, key, download_path)

        print("UPLOADING THE MOBILE COVER\n")
        mobile_cover(download_path, upload_path_cover, img_type)
        suffix = 'x'.join(map(str, MOBILE_COVER_SIZE))
        s3_client.upload_file(upload_path_cover, '{bucket_name}-lambda'.format(bucket_name=bucket),
                              '{suffix}_{key}'.format(key=key, suffix=suffix))

        print("UPLOADING THE WEBSITE COVER\nN")
        suffix = 'x'.join(map(str, WEB_COVER_SIZE))
        web_cover(download_path, upload_path_cover, img_type)
        s3_client.upload_file(upload_path_cover, '{bucket_name}-lambda'.format(bucket_name=bucket),
                              '{suffix}_{key}'.format(key=key, suffix=suffix))

        print("UPLOADING THE THUMBNAIL\n")
        suffix = 'x'.join(map(str, THUMBNAIL_SIZE))
        image_thumbnail(download_path, upload_path_thumbnail, img_type)
        s3_client.upload_file(upload_path_thumbnail, '{bucket_name}-lambda'.format(bucket_name=bucket),
                              '{suffix}_{key}'.format(key=key, suffix=suffix))

        print("UPLOADING THE SMART THUMBNAIL\n")
        suffix = 'x'.join(map(str, SMART_THUMBNAIL_SIZE))
        smart_thumbnail(download_path, upload_path_thumbnail, img_type)
        s3_client.upload_file(upload_path_thumbnail, '{bucket_name}-lambda'.format(bucket_name=bucket),
                              '{suffix}_{key}'.format(key=key, suffix=suffix))
