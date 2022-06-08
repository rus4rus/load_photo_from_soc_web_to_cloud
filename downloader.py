from vk_class import VkApi
from yandex_disc import YaUploader
from tqdm import tqdm
from datetime import datetime
import json


class Download:
    """Создаем схемы загрузки из источника в получатель"""

    def __init__(self, ya_token, vk_token):
        self.ya_token = ya_token
        self.vk_token = vk_token


    def upload_photo_from_vk_to_ya_disc(self, user_id, count=5, name_of_dir="files_for_netology"):

        vk = VkApi(self.vk_token)
        ya = YaUploader(self.ya_token)

        if not ya.check_disk(): #проверка на доступность диска
            return
        # создаем имена по сценарию из файла с данными о фото:
        list_of_photos = vk.make_photo_names(vk.get_max_size_photos(user_id, count))
        if not list_of_photos:
            return
        t = tqdm(total=len(list_of_photos))
        for photo in list_of_photos:
            if not ya.upload_from_href(photo["sizes"]["url"], photo["name"], name_of_dir):
                return
            t.update()
        t.close()
        print(f'\nВсе файлы загружены (в количестве {len(list_of_photos)} при запросе {count} фотографий)')
        with open('logs.txt', 'a') as f:
            f.write(f'{datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | '
                    f'Все файлы загружены (в количестве {len(list_of_photos)} при запросе {count} фотографий)\n')
        json_list = []
        for photo in list_of_photos:
            json_list.append({"file_name": photo["name"], "size": photo["sizes"]["type"]})

        with open('photos.json', 'w') as f:
            json.dump(json_list, f)
