""" Created by MrBBS - 1/10/2023 """
# -*-encoding:utf-8-*-

import multiprocessing
import random
import string
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

ori_url = 'https://jm.com.vn/lookbook-ac2153.html{}'
url_product = 'https://jm.com.vn{}'
output = Path(r'E:\data\remove_bg\crawl\jm')
output.mkdir(parents=True, exist_ok=True)


def download(href):
    u = url_product.format(href)
    res = requests.get(u).text
    soup = BeautifulSoup(res, 'html.parser')
    for a in soup.find_all('a', attrs={'class': 'fancybox-album'}):
        img = a['href']
        name = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        ext = img.split('.')[-1]
        out = output.joinpath(f'{name}.{ext}')
        r = requests.get(img)
        if r.status_code == 200:
            with open(out.as_posix(), 'wb') as f:
                f.write(r.content)


if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=12)
    jobs = []
    for i in tqdm(range(1, 4), position=0):
        page = ''
        if i > 1:
            page = f'?page={i}'
        url = ori_url.format(page)
        res = requests.get(url).text
        soup = BeautifulSoup(res, 'html.parser')
        collection = soup.find('div', attrs={'class': 'listAlbum clearfix'})
        for item in collection:
            href = item.findNext('a')['href']
            jobs.append(pool.apply_async(download, args=(href,), callback=None))
    pool.close()
    for job in tqdm(jobs, position=1, leave=False):
        job.get()
    pool.join()
