""" Created by MrBBS - 1/10/2023 """
# -*-encoding:utf-8-*-

import multiprocessing
import random
import string
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

ori_url = 'https://nemshop.vn/collections/tat-ca-san-pham{}'
url_product = 'https://nemshop.vn/collections/tat-ca-san-pham{}'
output = Path(r'E:\data\remove_bg\crawl\nemshop')
output.mkdir(parents=True, exist_ok=True)


def crawl(href):
    u = url_product.format(href)
    res = requests.get(u).text
    soup = BeautifulSoup(res, 'html.parser')
    for item in soup.find_all('li', attrs={'class': 'thumbnail-item'}):
        img = 'http:' + item.findNext('a')['href']
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

    for i in tqdm(range(1, 110), position=0):
        page = ''
        if i > 1:
            page = f'?page={i}'
        url = ori_url.format(page)
        res = requests.get(url).text
        soup = BeautifulSoup(res, 'html.parser')
        collection = soup.find('div', attrs={'class': 'collection-body'})
        products = []
        for item in collection.find_all('div', attrs={'class': 'product-title'}):
            href = item.findNext('a')['href']
            jobs.append(pool.apply_async(crawl, args=(href,), callback=None))
    pool.close()
    for job in tqdm(jobs, position=1, leave=False):
        job.get()
    pool.join()
