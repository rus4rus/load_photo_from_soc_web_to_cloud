import configparser
from downloader import input_dir_name_and_count, input_social_network_and_username

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('settings.ini')
    insta_token, vk_token, ya_token = config['Instagram']['token'], config['VK']['token'], config['Yandex']['token']

    input_dir_name_and_count(ya_token, vk_token, insta_token)