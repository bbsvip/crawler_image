""" Created by MrBBS - 4/4/2023 """
# -*-encoding:utf-8-*-

import json
import re
import time
from base64 import b64decode as decode
from pathlib import Path
from random import randint
from re import findall

import requests
from requests import get, Session
from tqdm import tqdm


class Bot:
    def __init__(self, delay=1):
        self.sockets = []
        self._update_proxy()
        self.delay = delay

    def _update_proxy(self):
        r = requests.get('https://www.sslproxies.org/')
        matches = findall(r"<td>\d+\.\d+\.\d+\.\d+</td><td>\d+</td>", r.text)
        revised = [m.replace('<td>', '') for m in matches]
        self.sockets = [s[:-5].replace('</td>', ':') for s in revised]

    def _rand_proxy(self):
        return randint(0, len(self.sockets) - 1)

    def _remove(self, path):
        if len(self.sockets) == 0:
            self._update_proxy()
        current_socket = self.sockets.pop(self._rand_proxy())
        proxies = {
            'http': 'http://' + current_socket,
            'https': 'https://' + current_socket
        }
        s = Session()
        s.headers[
            "User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 Edg/98.0.1108.62"
        s.headers["x-requested-with"] = "XMLHttpRequest"
        s.headers["origin"] = "https://www.remove.bg"
        get_csrf = s.get("https://www.remove.bg/upload")
        time.sleep(self.delay)
        csrf = re.search(r"name\=\"csrf\-token\"\ content\=\"(.*?)\"", get_csrf.text).group(1)
        s.headers["x-csrf-token"] = csrf
        s.headers["referer"] = "https://www.remove.bg/upload"

        r = s.post("https://www.remove.bg/trust_tokens")
        use_token = re.search(r"ken\(\'(.*?)\'\)", r.text)
        if use_token:
            if not isinstance(path, Path) and "http" in path:
                file = get(path).content
            else:
                file = open(path.as_posix(), "rb")

            filename = path.name
            form_data = {"trust_token": use_token.group(1)}
            form_files = {"image[original]": (filename, file, "multipart/form-data")}
            time.sleep(self.delay)
            r = s.post("https://www.remove.bg/images", data=form_data, files=form_files)
            res_url = r.json()["url"]

            time.sleep(3)
            res = get(f"https://www.remove.bg{res_url}")

            result_json = json.loads(decode(res.json()["pl"]).decode("utf-8"))

            return result_json
        else:
            return None

    def _download(self, out: Path, result_json):
        url = result_json.get("result")["url"]
        name = url.split("/")[-1]
        r = get(url, allow_redirects=True)
        with open(out.joinpath(name).as_posix(), 'wb') as image_file:
            image_file.write(r.content)

    def _run(self, inp, out):
        respone = self._remove(inp)
        if respone is not None:
            self._download(out, respone)
            return True
        return False

    def start(self, input_folder: Path, output_folder: Path):
        for p in tqdm(input_folder.rglob('*.[jp][pn]*')):
            self._run(p, output_folder)
            # if not self._run(p, output_folder):
            #     break


if __name__ == '__main__':
    bot = Bot()
    input_folder = Path(
        r'E:\segment_image\crawler\hand_holding\Hand Holding Photos, Download The BEST Free Hand Holding Stock Photos & HD Images')
    output_folder = Path(r'E:\segment_image\crawler\hand_holding\abc')
    output_folder.mkdir(parents=True, exist_ok=True)
    bot.start(input_folder, output_folder)
