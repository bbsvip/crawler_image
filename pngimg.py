""" Created by MrBBS - 4/5/2023 """
# -*-encoding:utf-8-*-

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from pathlib import Path
import random
import string
import multiprocessing


def download_image(url, out: Path):
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    container = soup.find('div', attrs={'class': "png_big"})
    u = container.find('img')['src']
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + '.png'
    r = requests.get(u)
    if r.status_code == 200:
        with open(out.joinpath(name).as_posix(), 'wb') as f:
            f.write(r.content)


def get_category(url):
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    catalog = soup.find_all('div', attrs={'class': 'sub_category'})
    all_category = {}
    for category in catalog:
        a = category.find_all('a')
        for i in a:
            name = i.text
            u = i['href']
            all_category[name] = url + u
    return all_category


def get_image(category, url, output_path: Path):
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    out = output_path.joinpath(category)
    out.mkdir(parents=True, exist_ok=True)
    li = soup.find_all('li', attrs={'itemprop': "associatedMedia"})
    pool = multiprocessing.Pool(processes=8)
    jobs = []
    for l in li:
        try:
            url_download = l.find('a')['href']
            jobs.append(pool.apply_async(download_image, args=(url_download, out), callback=None))
        except:
            pass
    pool.close()
    for job in tqdm(jobs, desc='Download image', position=1, leave=False):
        job.get()


if __name__ == '__main__':
    url = 'https://pngimg.com'
    output = Path(r'E:\segment_image\crawler\pngimg')
    catalog = get_category(url)
    for name, u in tqdm(catalog.items(), desc='Fetch category', position=0):
        get_image(name, u, output)
