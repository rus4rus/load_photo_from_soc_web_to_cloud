import requests
from datetime import datetime
from yandex_disc import YaUploader

class VkApi:
    URL = "https://api.vk.com/method/"
    def __init__(self, token):
        self.token = token

    def get_params(self):
        return {
            "v": "5.131",
            "access_token": self.token
        }

    def get_user_info(self, *user_id):
        '''Получение информации о человеке/людях по его id/нику'''
        url = self.URL +'users.get'
        users = ",".join(user_id)
        params = {
            **self.get_params(),
            **{"user_ids": users},
            "fields": "about",
        }
        #Проверка соединения интернета
        try:
            r = requests.get(url, params=params)
        except requests.ConnectionError:
            print(f'Нет соединения с сервером. Возможно, отсутствует подключение к интернету')
            with open("logs.txt", "a") as f:
                f.write(f'{datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Нет соединения с сервером. Возможно, отсутствует подключение к интернету\n')
            return False


        if r.json().get("error"): # Проверка на ошибки
            print(f"Ошибка при подключении в ВК! {r.json()['error']['error_msg']}")
            with open("logs.txt", "a") as f:
                f.write(f'{datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Ошибка при подключении к ВК! {r.json()["error"]["error_msg"]}\n')
            return False

        if not r.json()["response"]: # Проверка на существование пользователя
            s_names = str([*user_id]).rstrip("]").lstrip("[").replace("'","") #из списка имена пользователей в строку
            print(f"Пользователей с именем(-ами) {s_names} не существует")
            with open("logs.txt", "a") as f:
                f.write(f'{datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Пользователей с именем(-ами) {s_names} не существует\n')
            return False
        return r.json()

    def _get_user_id(self, user):
        '''Получение id из уникального имени'''
        r = self.get_user_info(user)
        if not r:
            return False
        user_id = r["response"][0]["id"]
        return user_id

    def get_photos_list(self, user_id):
        if not user_id:
            return False
        owner_id = self._get_user_id(user_id)
        if not owner_id:
            return False
        '''Получение список фото'''
        url = self.URL + 'photos.get'
        params = {**self.get_params(), **{"owner_id": owner_id,
                                          "album_id": "profile",
                                          "extended": 1}}
        r = requests.get(url, params=params)
        if r.json().get("error"): # Проверка на ошибки
            print(f"Ошибка ВК! {r.json()['error']['error_msg']}")
            with open("logs.txt", "a") as f:
                f.write(f'{datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Ошибка ВК! {r.json()["error"]["error_msg"]}\n')
            return False
        elif not r.json()["response"]["count"]:
            print(f"У пользователя {user_id}  нет фотографий")
            with open("logs.txt", "a") as f:
                f.write(f'{datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | У пользователя {user_id}  нет фотографий\n')
            return False
        print('Фотографии подготовлены для загрузки')
        with open("logs.txt", "a") as f:
            f.write(f'{datetime.now().strftime(f"%H:%M:%S:%f%d/%m/%Y")} | Фотографии подготовлены для загрузки\n')
        return r.json()

    def get_max_size_photos(self, user_id, count):
        ''''Получаем список максимальных по размеру фото, число фото count по умолчанию - 5'''
        r = self.get_photos_list(user_id)
        if not r:
            return False
        list_of_all_photos = r["response"]["items"]
        list_of_max_photos = [] #список с фотографиями в максимальном разрешении
        # Получаем список фото в максимальноми размере
        for photo in list_of_all_photos:
            list_of_max_photos.append(
                                       {"likes":photo["likes"],
                                       "date": photo["date"],
                                       "sizes":photo["sizes"][-1]
                                       }
                                      ) #API выводит фото в максимальном разрешении последним среди однотипных
        sorted_list = sorted(list_of_max_photos, key=lambda x: x["sizes"]["height"] * x["sizes"]["width"], reverse=True)
        return sorted_list[:count] #возвращаем первые count фото с максимальным разрешением


