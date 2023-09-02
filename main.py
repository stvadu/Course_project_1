import requests
import yadisk
import json
from tqdm import tqdm
from time import sleep
from datetime import datetime
from yadisk import yadisk


def unixtime(ts):

    return datetime.utcfromtimestamp(int(ts)).strftime('%Y-%m-%d_%H:%M:%S')

def sort_dict(dict):
    sorted_dict = {}
    sorted_keys = sorted(dict, key=dict.get, reverse=True)

    for w in sorted_keys:
        sorted_dict[w] = dict[w]

    return sorted_dict


def backup_vk_yadisk(vk_id, photos_count = 5) :
    with open('vk-tok.txt', 'r') as file_object:
        vk_token = file_object.read().strip()
    with open('ya-tok.txt', 'r') as file_object:
        ya_token = file_object.read().strip()

    URL_VK = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': vk_id,
        'album_id': 'profile',
        'access_token': vk_token,
        'v':'5.131',
        'extended': '1'
    }
    res = requests.get(URL_VK, params=params)

    alldata = res.json()

    photo_dict = {}

    for photos in alldata['response']['items']:
        photo_data = photos['sizes']
        max_quality_photo = photo_data[-1]
        likes_count = photos['likes']['count']
        photo_date = unixtime(photos['date'])
        photo_url = max_quality_photo['url']
        photo_height = max_quality_photo['height']
        photo_width = max_quality_photo['width']
        photo_size = str(max_quality_photo['width']) + 'x' + str(max_quality_photo['height'])
        photo_name = str(likes_count) + '_likes_' + photo_date
        photo_dict[photo_url] = [photo_width*photo_height, photo_name, photo_size]

    ydisk = yadisk.YaDisk(token=ya_token)

    if ydisk.is_dir('/backup_vk_yadisk/'):
        ydisk.remove('/backup_vk_yadisk/', permanently=True)
        sleep(1.0)
    ydisk.mkdir('/backup_vk_yadisk/')

    sort_photo_dict = sort_dict(photo_dict)
    photo_out_list = []

    if len(sort_photo_dict) < photos_count:
         out_count = len(sort_photo_dict)
    else: out_count = photos_count

    i = 0
    for photo__url in tqdm(photo_dict, ncols=80, total=out_count, ascii=True, desc='Copying from VK to YaDisk...') :
        i += 1
        photo__name = sort_photo_dict[photo__url][1]
        photo_out_dict = {'file_name': sort_photo_dict[photo__url][1], 'size': sort_photo_dict[photo__url][2]}
        if i <= photos_count:
            sleep(0.01)
            ydisk.upload_url(photo__url, f'/backup_vk_yadisk/{photo__name}')
            photo_out_list.append(photo_out_dict)

    with open('photo_out_list.json', 'w', encoding='utf-8') as out_file_json:
        json.dump(photo_out_list, out_file_json, ensure_ascii=False, indent=4)


backup_vk_yadisk()