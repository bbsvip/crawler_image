""" Created by MrBBS - 3/28/2023 """
# -*-encoding:utf-8-*-

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
import random
import string
import multiprocessing


def download(url, out: Path):
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.png'
    r = requests.get(url)
    if r.status_code == 200:
        with open(out.joinpath(name).as_posix(), 'wb') as f:
            f.write(r.content)


def download_image(url, out):
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    container = soup.find_all('div', attrs={
        'class': 'gallery-item-container item-container-regular has-custom-focus visible clickable'})
    pool = multiprocessing.Pool(processes=12)
    jobs = []
    for div in container:
        try:
            link = div.find('source')
            img = link['srcset'].split('png')[0]
            jobs.append(pool.apply_async(download, args=(img + 'png', out), callback=None))
        except:
            pass
    pool.close()
    for job in tqdm(jobs, position=1, leave=False):
        job.get()


def get_image(url, out):
    out.mkdir(parents=True, exist_ok=True)
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    container = soup.find('div', attrs={'aria-label': 'Matrix gallery'})
    if container is not None:
        for collection in container.find_all('a'):
            try:
                link = collection['href']
                c = link.split('/')[-1].split('-')[0]
                o = out.joinpath(c)
                o.mkdir(parents=True, exist_ok=True)
                download_image(collection['href'], o)
            except:
                pass
            # break


if __name__ == '__main__':
    url = 'https://www.freepngs.com/'
    output = Path(r'E:\segment_image\crawler')

    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    container = soup.find('div', attrs={'aria-label': 'Matrix gallery'})

    for collection in tqdm(container.find_all('a')[23:], position=0):
        get_image(collection['href'], output)

