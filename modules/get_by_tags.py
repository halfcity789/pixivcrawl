import json
import asyncio
import random
import requests
from aiohttp import ClientSession
from sys import exit
from rich.progress import Progress, track
from os import mkdir, path
from datetime import datetime
from time import time

from modules.args import *
from modules.userAgent import *
from modules.other import Help


class GetImageByTag(object):
    def __init__(self, tag, page, timeout, cookie):
        self.tag = tag
        self.page = page
        self.timeout = timeout
        self.cookie = cookie
        self.authorId = []
        self.imageURL = []
        self.imageId = []
        self.imageSum = 0
        self.totalPage = 0
        self.num = 0
        self.other = 0
        self.sleep = args.sleep
        self.time = 0
        self.timeNow = 0
        self.h = Help()
        self.PROXY = args.proxy
        self.proxy = {
            "http": args.proxy,
            "https": args.proxy
        }
        self.header = {
            "User-Agent": random.choice(user_agent),
            "Referer": "https://www.pixiv.net/",
            "Cookie": self.cookie
        }

    def get_image_url(self):
        url = "https://www.pixiv.net/ajax/search/artworks/{tag}?word={tag}&order=date_d&mode=all&p={page}&s_mode=s_tag&type=all&lang=zh"

        try:
            print(f"{self.h.i} preparing...")

            res = requests.get(url=url.format(tag=self.tag, page=1), proxies=self.proxy, headers=self.header,
                               timeout=self.timeout)

            allData = json.loads(res.text)["body"]["illustManga"]

            self.imageSum = allData["total"]
            self.totalPage = allData["lastPage"]
            data = allData["data"]

            if self.imageSum == 0:
                print(f"{self.h.w} {self.h.color('red', 'No image found!')}")
                exit()

            for d in track(data):
                self.authorId.append(d["userId"])
                self.imageId.append(d["id"])
                imageBuffer = str(d["url"]).split('/', 6)
                imageBufferT = imageBuffer[6].rsplit('/', 1)
                self.imageURL.append(imageBuffer[0] + "//" + imageBuffer[2] + '/img-original/' + imageBufferT[0] + '/' +
                                     imageBufferT[1].rsplit('_', 1)[0] + ".{extra}")

            if self.page == 0:
                self.header["User-Agent"] = random.choice(user_agent)

                for i in track(range(2, self.totalPage + 1)):
                    res = requests.get(url=url.format(tag=self.tag, page=i), proxies=self.proxy, headers=self.header,
                                       timeout=args.timeout)

                    data = json.loads(res.text)["body"]["illustManga"]["data"]

                    for ii in data:
                        self.authorId.append(ii["userId"])
                        self.imageId.append(ii["id"])
                        imageBuffer = str(ii["url"]).split('/', 6)
                        imageBufferT = imageBuffer[6].rsplit('/', 1)
                        self.imageURL.append(
                            imageBuffer[0] + "//" + imageBuffer[2] + '/img-original/' + imageBufferT[0] + '/' +
                            imageBufferT[1].rsplit('_', 1)[0] + ".{extra}")
            elif self.page > 1:
                for i in track(range(2, self.page + 1)):
                    self.header["User-Agent"] = random.choice(user_agent)

                    res = requests.get(url=url.format(tag=self.tag, page=i), proxies=self.proxy, headers=self.header,
                                       timeout=self.timeout)

                    data = json.loads(res.text)["body"]["illustManga"]["data"]

                    for ii in data:
                        self.authorId.append(ii["userId"])
                        self.imageId.append(ii["id"])
                        imageBuffer = str(ii["url"]).split('/', 6)
                        imageBufferT = imageBuffer[6].rsplit('/', 1)
                        self.imageURL.append(
                            imageBuffer[0] + "//" + imageBuffer[2] + '/img-original/' + imageBufferT[0] + '/' +
                            imageBufferT[1].rsplit('_', 1)[0] + ".{extra}")
            elif self.page < 0:
                print(f"{self.h.e} {self.h.color('red', 'Error, page must be positive integer')}")
                exit()
            elif self.page > self.totalPage:
                print(f"{self.h.e}  {self.h.color('red', 'Error, page must be less than total page')}")
                exit()
            print(f"{self.h.i} images found: {self.h.color('blue', self.imageSum)}")
            print(f"{self.h.i} total pages: {self.h.color('blue', self.totalPage)}")
            print(f"{self.h.i} Selected: {self.h.color('blue', len(self.imageURL))}, {self.h.color('blue', self.page)}")
        except requests.exceptions.ProxyError:
            print(f"{self.h.e} {self.h.color('red', 'Proxy error, please check your proxy')}")
            exit()
        except requests.exceptions.RequestException:
            print(f"{self.h.e} {self.h.color('red', 'Network error, please check your network')}")
            print(
                f"{self.h.t} If you are in China, you should {self.h.color('yellow', 'use an proxy')}, try '-h' to get help")
            exit()

    def check(self):
        self.timeNow = datetime.now()
        self.time = str(self.timeNow).split(' ')[0] + '-' + str(self.timeNow).split(' ')[1].rsplit('.')[0].replace(':',
                                                                                                                   '-')

        if not path.exists("./ResImage"):
            mkdir("./ResImage")
        if not path.exists("./ResImage/{time}".format(time=self.time)):
            mkdir("./ResImage/{time}".format(time=self.time))

        if (len(self.imageURL) / 5) >= 1:
            self.num = int(len(self.imageURL) / 5)
            self.other = len(self.imageURL) % 5
        else:
            self.num = len(self.imageURL)

    def get_image_by_tags(self):
        self.get_image_url()
        self.check()

        with Progress() as progress:
            if self.num >= 5:
                flagMore = False
                flagLess = False

                if self.other > 0:
                    flagMore = True

                    task1 = progress.add_task('ProcessOne', total=self.num)
                    task2 = progress.add_task('ProcessTwo', total=self.num)
                    task3 = progress.add_task('ProcessThree', total=self.num)
                    task4 = progress.add_task('ProcessFour', total=self.num)
                    task5 = progress.add_task('ProcessFive', total=self.num + self.other)
                else:
                    task1 = progress.add_task('ProcessOne', total=self.num)
                    task2 = progress.add_task('ProcessTwo', total=self.num)
                    task3 = progress.add_task('ProcessThree', total=self.num)
                    task4 = progress.add_task('ProcessFour', total=self.num)
                    task5 = progress.add_task('ProcessFive', total=self.num)
            else:
                flagLess = True

                task = progress.add_task('Process', total=self.num)

            print("[\033[96mInfo\033[0m] Start time: ", self.timeNow)

            timeUse = time()
            try:
                async def processOne():
                    async with ClientSession() as session:
                        ii = 0
                        for i in self.imageURL[0: self.num]:
                            self.header["User-Agent"] = random.choice(user_agent)
                            async with await session.get(url=i.format(extra="png"), headers=self.header,
                                                         proxy=self.PROXY,
                                                         timeout=self.timeout) as res:
                                if res.status == 404:
                                    self.header["User-Agent"] = random.choice(user_agent)
                                    async with await session.get(url=i.format(extra="jpg"), headers=self.header,
                                                                 proxy=self.PROXY, timeout=self.timeout) as resT:
                                        imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                            name=imageName,
                                                                                            extra="jpg"), 'wb') as f:
                                            f.write(await resT.content.read())
                                        progress.update(task1, advance=1)
                                        ii += 1
                                        await asyncio.sleep(self.sleep)
                                else:
                                    imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=self.time, name=imageName,
                                                                                        extra="png"), 'wb') as f:
                                        f.write(await res.content.read())
                                    progress.update(task1, advance=1)
                                    ii += 1
                                    await asyncio.sleep(self.sleep)

                async def processTwo():
                    async with ClientSession() as session:
                        ii = self.num
                        for i in self.imageURL[self.num: self.num * 2]:
                            self.header["User-Agent"] = random.choice(user_agent)
                            async with await session.get(url=i.format(extra="png"), headers=self.header,
                                                         proxy=self.PROXY,
                                                         timeout=self.timeout) as res:
                                if res.status == 404:
                                    async with await session.get(url=i.format(extra="jpg"), headers=self.header,
                                                                 proxy=self.PROXY, timeout=self.timeout) as resT:
                                        imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                            name=imageName,
                                                                                            extra="jpg"), 'wb') as f:
                                            f.write(await resT.content.read())
                                        progress.update(task2, advance=1)
                                        ii += 1
                                        await asyncio.sleep(self.sleep)
                                else:
                                    imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=self.time, name=imageName,
                                                                                        extra="png"), 'wb') as f:
                                        f.write(await res.content.read())
                                    progress.update(task2, advance=1)
                                    ii += 1
                                    await asyncio.sleep(self.sleep)

                async def processThree():
                    async with ClientSession() as session:
                        ii = self.num * 2
                        for i in self.imageURL[self.num * 2: self.num * 3]:
                            self.header["User-Agent"] = random.choice(user_agent)
                            async with await session.get(url=i.format(extra="png"), headers=self.header,
                                                         proxy=self.PROXY,
                                                         timeout=self.timeout) as res:
                                if res.status == 404:
                                    async with await session.get(url=i.format(extra="jpg"), headers=self.header,
                                                                 proxy=self.PROXY, timeout=self.timeout) as resT:
                                        imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                            name=imageName,
                                                                                            extra="jpg"), 'wb') as f:
                                            f.write(await resT.content.read())
                                        progress.update(task3, advance=1)
                                        ii += 1
                                        await asyncio.sleep(self.sleep)
                                else:
                                    imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=self.time, name=imageName,
                                                                                        extra="png"),
                                              'wb') as f:
                                        f.write(await res.content.read())
                                    progress.update(task3, advance=1)
                                    ii += 1
                                    await asyncio.sleep(self.sleep)

                async def processFour():
                    async with ClientSession() as session:
                        ii = self.num * 3
                        for i in self.imageURL[self.num * 3: self.num * 4]:
                            self.header["User-Agent"] = random.choice(user_agent)
                            async with await session.get(url=i.format(extra="png"), headers=self.header,
                                                         proxy=self.PROXY,
                                                         timeout=self.timeout) as res:
                                if res.status == 404:
                                    async with await session.get(url=i.format(extra="jpg"), headers=self.header,
                                                                 proxy=self.PROXY, timeout=self.timeout) as resT:
                                        imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                            name=imageName,
                                                                                            extra="jpg"), 'wb') as f:
                                            f.write(await resT.content.read())
                                        progress.update(task4, advance=1)
                                        ii += 1
                                        await asyncio.sleep(self.sleep)
                                else:
                                    imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=self.time, name=imageName,
                                                                                        extra="png"),
                                              'wb') as f:
                                        f.write(await res.content.read())
                                    progress.update(task4, advance=1)
                                    ii += 1
                                    await asyncio.sleep(self.sleep)

                if flagMore:
                    async def processFive():
                        async with ClientSession() as session:
                            ii = self.num * 4
                            for i in self.imageURL[self.num * 4: self.num * 5 + self.other]:
                                self.header["User-Agent"] = random.choice(user_agent)
                                async with await session.get(url=i.format(extra="png"), headers=self.header,
                                                             proxy=self.PROXY,
                                                             timeout=self.timeout) as res:
                                    if res.status == 404:
                                        async with await session.get(url=i.format(extra="jpg"), headers=self.header,
                                                                     proxy=self.PROXY, timeout=self.timeout) as resT:
                                            imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                            with open(
                                                    "./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                              name=imageName,
                                                                                              extra="jpg"), 'wb') as f:
                                                f.write(await resT.content.read())
                                            progress.update(task5, advance=1)
                                            ii += 1
                                            await asyncio.sleep(self.sleep)
                                    else:
                                        imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                            name=imageName,
                                                                                            extra="png"), 'wb') as f:
                                            f.write(await res.content.read())
                                        progress.update(task5, advance=1)
                                        ii += 1
                                        await asyncio.sleep(self.sleep)
                elif flagLess:
                    async def processFive():
                        async with ClientSession() as session:
                            ii = self.num
                            for i in self.imageURL:
                                self.header["User-Agent"] = random.choice(user_agent)
                                async with await session.get(url=i.format(extra="png"), headers=self.header,
                                                             proxy=self.PROXY,
                                                             timeout=self.timeout) as res:
                                    if res.status == 404:
                                        async with await session.get(url=i.format(extra="jpg"), headers=self.header,
                                                                     proxy=self.PROXY, timeout=self.timeout) as resT:
                                            imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                            with open(
                                                    "./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                              name=imageName,
                                                                                              extra="jpg"), 'wb') as f:
                                                f.write(await resT.content.read())
                                            progress.update(task, advance=1)
                                            ii += 1
                                            await asyncio.sleep(self.sleep)
                                    else:
                                        imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                            name=imageName,
                                                                                            extra="png"), 'wb') as f:
                                            f.write(await res.content.read())
                                        progress.update(task, advance=1)
                                        ii += 1
                                        await asyncio.sleep(self.sleep)
                else:
                    async def processFive():
                        async with ClientSession() as session:
                            ii = self.num * 4
                            for i in self.imageURL[self.num * 4: self.num * 5]:
                                self.header["User-Agent"] = random.choice(user_agent)
                                async with await session.get(url=i.format(extra="png"), headers=self.header,
                                                             proxy=self.PROXY,
                                                             timeout=self.timeout) as res:
                                    if res.status == 404:
                                        async with await session.get(url=i.format(extra="jpg"), headers=self.header,
                                                                     proxy=self.PROXY, timeout=self.timeout) as resT:
                                            imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                            with open(
                                                    "./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                              name=imageName,
                                                                                              extra="jpg"), 'wb') as f:
                                                f.write(await resT.content.read())
                                            progress.update(task5, advance=1)
                                            ii += 1
                                            await asyncio.sleep(self.sleep)
                                    else:
                                        imageName = str(self.authorId[ii]) + '-' + str(self.imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=self.time,
                                                                                            name=imageName,
                                                                                            extra="png"), 'wb') as f:
                                            f.write(await res.content.read())
                                        progress.update(task5, advance=1)
                                        ii += 1
                                        await asyncio.sleep(self.sleep)

                loop = asyncio.get_event_loop()

                task11 = asyncio.ensure_future(processOne())
                task22 = asyncio.ensure_future(processTwo())
                task33 = asyncio.ensure_future(processThree())
                task44 = asyncio.ensure_future(processFour())
                task55 = asyncio.ensure_future(processFive())

                tasks = [task11, task22, task33, task44, task55]

                loop.run_until_complete(asyncio.wait(tasks))

            except requests.exceptions.ProxyError:
                print(f"{self.h.e} {self.h.color('red', 'Proxy error, please check your proxy')}")
                exit()
            except requests.exceptions.RequestException:
                print(f"{self.h.e} {self.h.color('red', 'Network error, please check your network')}")
                print(
                    f"{self.h.t} If you are in China, you should {self.h.color('yellow', 'use an proxy')}, try '-h' to get help")
                exit()
            except aiohttp.client_exceptions.ServerDisconnectedError:
                print(f"{self.h.w} Request for too fast connection failed")
                print(f"{self.h.t} You can use arg '-s'")

        print(f"\n{self.h.i} Used time:", time() - timeUse, 'sec')
        print(f"{self.h.i} Saved into ./ResImage/{self.time}/")
