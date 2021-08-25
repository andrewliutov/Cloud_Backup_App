import json
import requests
import time
from tqdm import tqdm


class VK:
    def __init__(self, token_vk, version):
        self.api_url = 'https://api.vk.com/method'
        self.token_vk = token_vk
        self.params = {'access_token': token_vk,
                       'v': version}

    def get_pic_hires(self, id_vk):
        """Получить изображения из ВК с самым высоким разрешением.

        Метод создает словарь с именами по кол-ву лайков и ссылками на
        изображения с самым высоким разрешением. Для этого все варианты
        каждого изображения проходят проверку на самое высокое разрешение
        путем сложения высоты и ширины. Информация добавляется в лог.

        """
        pic_search_url = self.api_url + '/photos.get'
        pic_params = {'owner_id': id_vk, 'album_id': 'profile',
                      'extended': 1, 'photo_sizes': 1, 'count': 5}
        req = requests.get(pic_search_url,
                    params=self.params|pic_params).json()['response']['items']
        pic_hires = {}
        log_json = []
        for pic in req:
            pic_allres = {}
            for pic_var in pic['sizes']:
                pic_allres[pic_var['height'] + pic_var['width']] =\
                    [pic_var['url'], pic_var['type']]
            if pic['likes']['count'] in pic_hires.keys():
                pic_hires[f"{pic['likes']['count']} - {time.ctime(pic['date'])}"] =\
                    pic_allres[max(pic_allres)][0]
                pic_log = {'file_name': f"{pic['likes']['count']} - "
                                        f"{time.ctime(pic['date'])}.jpg",
                           'size': pic_allres[max(pic_allres)][1]}
                log_json.append(pic_log)
            else:
                pic_hires[pic['likes']['count']] = pic_allres[max(pic_allres)][0]
                pic_log = {'file_name': f"{pic['likes']['count']}.jpg",
                           'size': pic_allres[max(pic_allres)][1]}
                log_json.append(pic_log)
        with open('log.json', 'w') as file:
            json.dump(log_json, file, indent=2)
        return pic_hires


class Yandex:
    def __init__(self, token_ya):
        self.api_url = 'https://cloud-api.yandex.net'
        self.token_ya = token_ya
        self.pic_hires = backup_dl.get_pic_hires(id_vk)

    def upload_pic(self):
        """Метод загружает полученные фото из ВК на Яндекс Диск."""
        headers = {'accept': 'application/json',
                   'authorization': f'OAuth {backup_ul.token_ya}'}
        requests.put(self.api_url + '/v1/disk/resources',
                     headers=headers,
                     params={'path': 'VK_backup'})
        for pic_name, url in tqdm(self.pic_hires.items()):
            requests.post(self.api_url + '/v1/disk/resources/upload',
                          headers=headers,
                          params={'path': f'VK_backup/{pic_name}.jpg',
                                  'url': url})
            time.sleep(1)
        print('Изображения загружены')


print('Добро пожаловать в программу для резервного копирования изображений \n'
      'из ВК на Яндекс Диск.')
token_vk = input('Введите токен для ВК: ')
id_vk = input('Введите id страницы, изображения с которой нужно загрузить: ')
token_ya = input('Введите токен для Яндекс Диска: ')
print('Загрузка началась')
backup_dl = VK(token_vk, '5.131')
backup_ul = Yandex(token_ya)
backup_ul.upload_pic()
