import asyncio
import random

import requests

from aiohttp import ClientSession, client_exceptions
from sys import exit
from rich.progress import Progress
from os import mkdir
from datetime import datetime
from time import time

from modules.other import Help
from modules.args import *
from modules.userAgent import *


class GetImageByAuthor(object):
    def __init__(self, authorid, page, timeout, cookie):
        self.id = authorid
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
        idUrl = "https://www.pixiv.net/ajax/user/{id}/profile/all?lang=zh"
        
        try:
            print(f"{self.h.i} preparing...")

            res = requests.get(url=idUrl.format(id=self.id, page=1), proxies=self.proxy, headers=self.header,
                               timeout=self.timeout)

            allData = json.loads(res.text)["body"]["illusts"]

            for i in allData:
                self.imageId.append(i)
            self.imageSum = len(self.imageId)
            self.totalPage = int(len(self.imageId) / 48)
            if len(self.imageId) / 48 != 1:
                self.totalPage += 1
            if self.page > 0:
                self.totalPage = self.page
            elif self.page < 0:
                print(f"{self.h.e} {self.h.color('red', 'Error, page must be positive integer')}")
                exit()
            elif self.page > self.totalPage:
                print(f"{self.h.e}  {self.h.color('red', 'Error, page must be less than total page')}")
                exit()

            print(f"{self.h.i} images found: {self.h.color('blue', self.imageSum)}")
            print(f"{self.h.i} total pages: {self.h.color('blue', self.totalPage)}")
            if self.page == 0 or self.imageSum <= 48:
                print(f"{self.h.i} Selected: {self.h.color('blue', self.imageSum)}, {self.h.color('blue', self.totalPage)}")
            else:
                print(f"{self.h.i} Selected: {self.h.color('blue', self.totalPage * 48)}, {self.h.color('blue', self.totalPage)}")

            with Progress() as progress:
                task2 = progress.add_task("Getting json ...", total=self.totalPage)
                if self.page == 0 or self.imageSum <= 48:
                    task1 = progress.add_task("Getting image url...", total=self.imageSum)
                else:
                    task1 = progress.add_task("Getting image url...", total=self.totalPage * 48)

                get = False
                for i in range(self.totalPage):
                    progress.update(task2, advance=1)

                    jsonUrl = "https://www.pixiv.net/ajax/user/81533107/profile/illusts?work_category=illustManga&is_first_page=0&lang=zh"
                    if self.imageSum >= 48:
                        for j in range(48 * i, 48 * (i + 1)):
                            jsonUrl = jsonUrl + "&ids[]=%s" % self.imageId[j]
                            if j >= len(self.imageId):
                                get = True
                                break
                    else:
                        for j in range(self.imageSum):
                            jsonUrl = jsonUrl + "&ids[]=%s" % self.imageId[j]
                            if j >= len(self.imageId):
                                get = True
                                break

                    res = requests.get(url=jsonUrl, proxies=self.proxy, headers=self.header, timeout=self.timeout)

                    allData = json.loads(res.text)["body"]["works"]

                    data = []
                    if self.imageSum >= 48:
                        for ii in range(48 * i, 48 * (i + 1)):
                            data.append(allData[self.imageId[ii]])
                            if len(data * (i + 1)) >= 48 * (i + 1):
                                break
                    else:
                        for ii in range(self.imageSum):
                            data.append(allData[self.imageId[ii]])
                            if len(data * (i + 1)) >= 48 * (i + 1):
                                break

                    for d in data:
                        self.authorId.append(d["userId"])
                        self.imageId.append(d["id"])
                        imageBuffer = str(d["url"]).split('/', 6)
                        imageBufferT = imageBuffer[6].rsplit('/', 1)
                        self.imageURL.append(imageBuffer[0] + "//" + imageBuffer[2] + '/img-original/' + imageBufferT[0] + '/' +
                                             imageBufferT[1].rsplit('_', 1)[0] + ".{extra}")
                        progress.update(task1, advance=1)
                    if get:
                        break

        except requests.exceptions.ProxyError:
            print(f"{self.h.e} {self.h.color('red', 'Proxy error, please check your proxy')}")
            exit()
        except requests.exceptions.RequestException:
            print(f"{self.h.e} {self.h.color('red', 'Network error, please check your network')}")
            print(f"{self.h.t} If you are in China, you should {self.h.color('yellow', 'use an proxy')}, try '-h' to get help")
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

    def get_image_by_author(self):
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
                flagMore = False
                flagLess = True

                task = progress.add_task('Process', total=self.num)

            print(f"{self.h.i} Start time: ", self.timeNow)

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
            except client_exceptions.ServerDisconnectedError:
                print(f"{self.h.w} Request too fast, connection failed")
                print(f"{self.h.t} You can use arg '-s' to turn speed down")
                exit()

        print(f"\n{self.h.i} Used time:", time() - timeUse, 'sec')
        print(f"{self.h.i} Saved into ./ResImage/{self.time}/")
