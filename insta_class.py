from pprint import pprint
import requests
from tokens import insta_token


class InstApi:
    URL = "https://graph.instagram.com/v9.0/"

    def __init__(self, token):
        self.token = token

    def get_user_id(self, username): #не работает
        url = f"https://www.instagram.com/web/search/topsearch/?context=user&count=0&query=bassjester"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36"}
        r = requests.get(url)*
        print(r)
        return r.json()


    def get_user_info(self, user_id):
        url = self.URL + user_id
        params = {
            "access_token": self.token,
            "fields": "account_type,id,media_count,username"
        }
        r = requests.get(url=url, params=params)
        return r.json()

    def get_photo_url_from_photo_id(self, user_id): #тоже не робит
        url = f"{self.URL}/{user_id}/media"
        params = {
            "access_token": self.token,
            "fields": "media_url, caption"
        }
        r = requests.get(url, params=params)
        return r.json()

    def get_likes_from_media(self, media_id):
        url = f"https://api.instagram.com/v1/media/{media_id}/likes?access_token={self.token}"
        r = requests.get(url)
        return r.json()



if __name__ == "__main__":
    insta_api = InstApi(insta_token)
    # pprint(insta_api.get_user_info('17841400296670589'))
    pprint(insta_api.get_photo_url_from_photo_id('17841400296670589'))
    # print(insta_api.get_user_id('bassjester'))
    pprint(insta_api.get_likes_from_media('17906642740197100'))
