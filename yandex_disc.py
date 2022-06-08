import requests
import datetime


class YaUploader:
    def __init__(self, token):
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
            return False

        if r.status_code == 200:
            with open('logs.txt', 'a') as log:
                log.write(
                    f'{datetime.datetime.now().strftime("%H:%M:%S:%f %d/%m/%Y")} | Связь с сервером установлена\n')
        else:
            print(f'Внимание! ошибка Я.Диска: {r.status_code}')
            print(r.json()['message'])
            return False

        return r.json()['href']

    def _get_file_name_from_path(self, path: str) -> str:  # возвращает имя файла из пути (для Windows \ для linux /! )
        """Из полного пути файла возвращает его имя"""
        return path[path.rfind('\\') + 1:]  # сделать автоматически!!!

    def upload(self, upload_file: str):
        file_name = f"/files_for_netology/" + self._get_file_name_from_path(upload_file)
        with open(upload_file, 'rb') as f:
            r = requests.put(self.get_link_to_upload(path=file_name), data=f.read())
            self.logs(r.status_code, request=r.json().get("message", ""),
                      file_name=self._get_file_name_from_path(upload_file))
            if r.status_code == 201:
                print(f'\t{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Файл'
                      f'{file_name[file_name.rfind("/") + 1:]} успешно загружен на Я.Диск', end="")
            else:
                print(f'При загрузке файла на Я.Диск произошла ошибка {r.status_code}')

    def upload_from_href(self, url: str, name_file: str, name_of_dir: str = "files_for_netology"):
        link = f'https://cloud-api.yandex.net/v1/disk/resources/upload/'
        headers = self.get_headers()
        params = {"path": f"/{name_of_dir}/" + name_file + ".jpg", "url": url}
        if requests.get("https://cloud-api.yandex.net/v1/disk/resources/",  # проверка на существование папки
                        headers=headers,
                        params={"path": name_of_dir}) != 404:
            if not self.add_directory(name_of_dir):
                return False
        r = requests.post(link, params=params, headers=headers)
        if r.status_code not in [200, 201, 202]:
            with open('logs.txt', 'a') as log:
                log.write(
                    f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Произошла ошибка: '
                    f'{r.json()["message"]}\n')
                print(
                    f'Произошла ошибка Я.Диска: {r.json()["message"]}\n')
            return False
        self.logs(r.status_code, request=r.json().get("message", ""), file_name=name_file)
        return True

    def add_directory(self, name_of_dir: str):
        url = f"https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        params = {"path": name_of_dir}
        r = requests.put(url, headers=headers, params=params)
        return self.logs(r.status_code, request=r.json().get("message", ""), dir_name=name_of_dir)

    def logs(self, status_code, request, file_name="", dir_name=""):
        # функция для создания лог=файла
        with open('logs.txt', 'a') as log:
            if file_name:
                if status_code == 202:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Файл '
                        f'{file_name} успешно загружен на Я.Диск\n')
                else:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | При загрузке файла на Я.диск '
                        f'"{file_name}" произошла ошибка Я.диска: {status_code}: {request}\n'
                    )
                    return False
            if dir_name:
                if status_code == 201:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | Папка '
                        f'{dir_name} успешно создана на Я.Диск\n')
                elif status_code == 409:
                    log.write(
                        f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | '
                        f'Невозможно создать папку {dir_name}:  {request}\n')
                else:
                    log.write(f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | При создании папки '
                              f'{file_name} на Я.диск произошла ошибка {status_code}: {request}\n')
                    print(
                        f'При создании папки '
                        f'{file_name} на Я.диск произошла ошибка {status_code}: {request}\n')
                    return False
        return True

    def check_disk(self):
        """Проверка на доступность диска"""
        link = f'https://cloud-api.yandex.net/v1/disk/'
        headers = self.get_headers()
        try:
            r = requests.get(link, headers=headers)
        except requests.ConnectionError:
            print(f'Нет соединения с сервером. Возможно, отсутствует подключение к интернету')
            with open("logs.txt", "a") as f:
                f.write(f'{datetime.datetime.now().strftime("%H:%M:%S:%f %d/%m/%Y")} | Нет соединения с сервером. '
                        f'Возможно, отсутствует подключение к интернету\n')
            return False
        if r.status_code == 401:
            print(f'Ошибка Я.диска: {r.json()["message"]} Проверьте токен!')
            with open("logs.txt", "a") as log:
                log.write(
                    f'{datetime.datetime.now().strftime(f"%H:%M:%S:%f %d/%m/%Y")} | '
                    f'Ошибка Я.диска: {r.json()["message"]} Проверьте токен!\n')
            return False
        return True
