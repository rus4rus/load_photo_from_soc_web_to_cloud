import configparser
from functions import download_photo

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    insta_token, vk_token, ya_token = config['Instagram']['token'], config['VK']['token'], config['Yandex']['token']
    download_photo(ya_token, vk_token, insta_token)
