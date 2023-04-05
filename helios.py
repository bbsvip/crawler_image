""" Created by MrBBS - 1/13/2023 """
# -*-encoding:utf-8-*-

import multiprocessing
import random
import string
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

ori_url = 'https://heliosjewels.vn/collections/nhan'
product_url = 'https://heliosjewels.vn{}'


def download(href):
    url = product_url.format(href)
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    container = soup.find('div', attrs={'class': 'theme-images swiper-wrapper'})
    for item in container.find_all_next('img', attrs={'class':'rimage__image lazyload--manual'}):
        print(item['data-src'])


url = ori_url.format(ori_url)
res = requests.get(url).text
soup = BeautifulSoup(res, 'html.parser')
collection = soup.find_all('a', attrs={'class': 'image-inner'})
for item in collection:
    download(item['href'])
    break
