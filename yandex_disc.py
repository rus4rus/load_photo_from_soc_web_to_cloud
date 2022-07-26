import requests
import datetime
from log_record import logs


class YaUploader:
    def __init__(self, token):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application.json',
            'Authorization': f'OAuth {self.token}'
        }

    def get_link_to_upload(self, path: str):
        '''get temporary link to upload on YndexDisc'''
        link = f'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        headers = self.get_headers()
        params = {'path': path, 'overwrite': 'true'}
        try:
            r = requests.get(link, headers=headers, params=params, timeout=5)
        except requests.ConnectionError as e:
            logs(f'{e}. Нет соединения с сервером. Возможно, отсутствует подключение к интернету')
            return False
        if r.status_code == 200:
            logs('Связь с сервером установлена\n')
        else:
            logs(f"Внимание! ошибка Я.Диска: {r.status_code}. r.json()['message']")
            return False
        return r.json()['href']

    def _get_file_name_from_path(self, path: str) -> str:
        return path[path.rfind('\\') + 1:]  # to do automatically for both Win and Linux

    def upload(self, upload_file: str):
        file_name = f"/files_for_netology/" + self._get_file_name_from_path(upload_file)
        with open(upload_file, 'rb') as f:
            r = requests.put(self.get_link_to_upload(path=file_name), data=f.read())
            logs(f'{r.status_code}, {r.json().get("message", "")}')
            if r.status_code == 201:
                logs('Файл {file_name[file_name.rfind("/") + 1:]} успешно загружен на Я.Диск')
            else:
                logs(f'При загрузке файла на Я.Диск произошла ошибка {r.status_code}')

    def upload_from_href(self, url: str, name_file: str, name_of_dir: str = "files_for_netology"):
        link = f'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        headers = self.get_headers()
        params = {"path": f"/{name_of_dir}/" + name_file + ".jpg", "url": url}
        # check dir existence
        if requests.get("https://cloud-api.yandex.net/v1/disk/resources/",
                        headers=headers,
                        params={"path": name_of_dir}) != 404:
            if not self.add_directory(name_of_dir):
                return False
        r = requests.post(link, params=params, headers=headers)
        if r.status_code not in [200, 201, 202]:
            logs(f'Произошла ошибка:{r.json()["message"]}')
            return False
        if r.status_code == 202:
            logs(f'Файл {name_file} успешно загружен на Я.Диск.', pr=False)
        else:
            logs(
                f'При загрузке файла на Я.диск "{name_file}" произошла ошибка Я.диска: {r.status_code}: {r.json()["message"]}')
            return False
        return True

    def add_directory(self, name_of_dir: str):
        url = f"https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        params = {"path": name_of_dir}
        r = requests.put(url, headers=headers, params=params)
        if r.status_code == 201:
            logs(f'Папка {name_of_dir} успешно создана на Я.Диск', pr=False)
        elif r.status_code == 409:
            logs(f'Невозможно создать папку {name_of_dir}:  {r.json().get("message", "")}', pr=False)
        else:
            logs(
                f'При создании папки {name_of_dir} на Я.диск произошла ошибка {r.status_code}: {r.json().get("message", "")}',
                pr=False)
            return False
        return True

    def check_disk(self):
        link = f'https://cloud-api.yandex.net/v1/disk/'
        headers = self.get_headers()
        try:
            r = requests.get(link, headers=headers)
        except requests.ConnectionError as e:
            logs(f'{e}. Нет соединения с сервером. Возможно, отсутствует подключение к интернету')
            return False
        if r.status_code == 401:
            logs(f'Ошибка Я.диска: {r.json()["message"]} Проверьте токен!')
            return False
        return True
