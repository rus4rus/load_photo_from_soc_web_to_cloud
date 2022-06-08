import sys
from tokens import token_yandex
import requests
import datetime

TOKEN = token_yandex


class YaUploader:
    def __init__(self, token=TOKEN):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application.json',
            'Authorization': f'OAuth {self.token}'
        }

    def get_link_to_upload(self, path: str):
        link = f'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        headers = self.get_headers()
        params = {'path': path, 'overwrite': 'true'}

        try:
            r = requests.get(link, headers=headers, params=params, timeout=5)
        except requests.ConnectionError:
            print(f'Нет соединения с сервером. Возможно, отсутствует подключение к интернету')
            with open("logs.txt", "a") as f:
                f.write(f'{datetime.datetime.now().strftime("%H:%M:%S:%f %d/%m/%Y")} | Нет соединения с сервером. '
                        f'Возможно, отсутствует подключение к интернету\n')
            sys.exit()
        if r.status_code == 200:
            with open('log.txt', 'a') as log:
                log.write(
                    f'{datetime.datetime.now().strftime("%H:%M:%S:%f %d/%m/%Y")} | Связь с сервером установлена\n')
        else:
            print(f'Внимание! ошибка {r.status_code}')
            print(r.json()['message'])
            sys.exit()

        return r.json()['href']

    def _get_file_name_from_path(self, path: str) -> str:  # возвращает имя файла из пути (для Windows \ для linux /! )
        return path[path.rfind('\\') + 1:]  # сделать автоматически!!!

    def upload(self, upload_file: str):
        file_name = f"/files_for_netology/" + self._get_file_name_from_path(upload_file)
        with open(upload_file, 'rb') as f:
            r = requests.put(self.get_link_to_upload(path=file_name), data=f.read())
            self.logs(r.status_code, request=r.json().get("message", ""),
                      file_name=self._get_file_name_from_path(upload_file))
            if r.status_code == 201:
                print(f'\t{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Файл '
                      f'{file_name[file_name.rfind("/") + 1:]} успешно загружен на Я.Диск', end="")
            else:
                print(f'При загрузке файла произошла ошибка {r.status_code}')

    def upload_from_href(self, url: str, name_file: str, name_of_dir: str = "files_for_netology"):
        link = f'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        headers = self.get_headers()
        params = {"path": f"/{name_of_dir}/" + name_file + ".jpg", "url": url}
        if requests.get("https://cloud-api.yandex.net/v1/disk/resources/",  # проверка на существование папки
                        headers=headers,
                        params={"path": name_of_dir}) != 404:
            self.add_directory(name_of_dir)
        r = requests.post(link, params=params, headers=headers)
        if r.status_code not in [200, 201, 202]:
            with open('log.txt', 'a') as log:
                log.write(
                    f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Произошла ошибка: '
                    f'{r.json()["message"]}\n')
            sys.exit()

        self.logs(r.status_code, request=r.json().get("message", ""), file_name=name_file)
        if r.status_code == 202:
            print(f'Файл {name_file} загружен успешно', end="")

    def add_directory(self, name_of_dir: str):
        url = f"https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        params = {"path": name_of_dir}
        r = requests.put(url, headers=headers, params=params)
        self.logs(r.status_code, request=r.json().get("message", ""), dir_name=name_of_dir)

    def logs(self, status_code, request, file_name="", dir_name=""):
        # функция для создания лог=файла
        with open('log.txt', 'a') as log:
            if file_name:
                if status_code == 202:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Файл '
                        f'{file_name} успешно загружен на Я.Диск\n')
                elif status_code == 201:
                    pass
                else:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | При загрузке файла на Я.диск '
                        f'"{file_name}" произошла ошибка: {status_code}: {request}\n'
                    )
            if dir_name:
                if status_code == 201:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Папка '
                        f'{dir_name} успешно создана на Я.Диск\n')
                elif status_code == 409:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Невозможно создать папку.  '
                        f'Папка {dir_name} уже существует на Я.Диск\n')
                elif status_code == 202:
                    pass
                else:
                    log.write(f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | При создании папки '
                              f'{file_name} на Я.диск произошла ошибка {status_code}: {request}\n')

    def check_disk(self):
        """Проверка на доступность диска"""
        link = f'https://cloud-api.yandex.net/v1/disk/'
        headers = self.get_headers()
        r = requests.get(link, headers=headers)
        if r.status_code == 401:
            print(f'Ошибка Я.диска: {r.json()["message"]} Проверьте токен!')
            with open("log.txt", "a") as log:
                log.write(
                    f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | '
                    f'Ошибка Я.диска: {r.json()["message"]} Проверьте токен!\n')
            sys.exit()
