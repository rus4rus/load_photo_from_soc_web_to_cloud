import requests
import configparser
from log_record import logs


class InstApi:
    URL = "https://graph.instagram.com/v9.0/"

    def __init__(self, token):
        self.token = token

    def get_user_info(self, user_id):
        '''makes dict {"account_type": type, "id":id, "media":[{"id": id},...], "media_count": count,
        "username":username} '''
        try:
            url = self.URL + user_id
            params = {
                "access_token": self.token,
                "fields": "account_type,id,media_count,username, media"
            }
            r = requests.get(url=url, params=params)
            return r.json()
        except KeyError as e:
            logs(f'{e}.')
            return
        except requests.exceptions.ConnectionError as e:
            logs(f'{e}.')


    def get_photo_info_from_photo_id(self, media_id):

        url = f"{self.URL}/{media_id}"
        params = {
            "access_token": self.token,
            "fields": "id, caption, media_url, timestamp, username"
        }
        r = requests.get(url, params=params)
        return r.json()

    def get_list_of_photos(self, dict_of_photos, count=50):
        '''makes list of photos ids, limit - 100'''
        if not dict_of_photos:
            return
        if not dict_of_photos.get('media'):
            logs(f"{dict_of_photos['error']['message']}")
            return
        new_list = []
        dict_of_photos = dict_of_photos['media']
        while True:
            if not dict_of_photos.get('data'):
                logs(f"{dict_of_photos['error']['message']}")
                return
            for data in dict_of_photos['data']:
                new_list.append(data['id'])
            if dict_of_photos['paging'].get('next'):
                dict_of_photos = requests.get(dict_of_photos['paging']['next']).json()
            else:
                break
        return new_list[:count]

    def make_dict_of_photos(self, list_of_photos):
        '''makes list of dicts of photos with name and url. Name is date of creature in Instagram'''

        list_of_photo_info = []
        if not list_of_photos:
            return
        for photo in list_of_photos:
            photo_info = self.get_photo_info_from_photo_id(photo)
            list_of_photo_info.append(
                {'name': photo_info['timestamp'][:-5].replace(":", "_"), 'url': photo_info['media_url']})
        return list_of_photo_info


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('settings.ini')
    insta_api = InstApi(config['Instagram']['token'])
    dict1 = insta_api.get_user_info('17841400296670589')
    new_list = insta_api.get_list_of_photos(dict1, 5)
    new_list_of_dicts = insta_api.make_dict_of_photos(new_list)
