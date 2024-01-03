import requests
import random

from sys import exit
from lxml import etree

from modules.other import Help
from modules.userAgent import *


class Search(object):
    def __init__(self, name, proxy, timeout, cookie):
        self.h = Help()
        self.name = name
        self.proxy = proxy
        self.timeout = timeout
        self.proxy = {
            "http": proxy,
            "https": proxy
        }
        self.header = {
            "User-Agent": random.choice(user_agent),
            "Referer": "https://www.pixiv.net/",
            "Cookie": cookie
        }

    def search(self):
        url = "https://www.pixiv.net/search/users?nick={author}&s_mode=s_usr"

        try:
            print(f"{self.h.i} searching...")

            res = requests.get(url=url.format(author=self.name), proxies=self.proxy, headers=self.header,
                               timeout=self.timeout)
            tree = etree.HTML(res.text)
            authorid = tree.xpath("/html/body/div[1]/div/div[2]/div[5]/div/div[1]/div[3]/li[1]/div/div[1]/div/div/div[1]/a/@data-gtm-value")

            return int(authorid[0])
        except IndexError:
            print(f"{self.h.w} {self.h.color('red', 'Author not found')}")
            exit()
        except requests.exceptions.ProxyError:
            print(f"{self.h.e} {self.h.color('red', 'Proxy error, please check your proxy')}")
            exit()
        except requests.exceptions.RequestException:
            print(f"{self.h.e} {self.h.color('red', 'Network error, please check your network')}")
            print(
                f"{self.h.t} If you are in China, you should {self.h.color('yellow', 'use an proxy')}, try '-h' to get help")
            exit()
