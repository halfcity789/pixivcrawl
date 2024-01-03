import json
import asyncio
import argparse
import requests
from aiohttp import ClientSession
from sys import exit
from rich.progress import Progress, track
from os import mkdir, path
from datetime import datetime
from time import time as tm

# args
parser = argparse.ArgumentParser(description='a script to crawl images of pixiv')

parser.add_argument('--proxy', type=str, help='set proxy', default="")
parser.add_argument('-t', '--tag', type=str, help='set tag', default="龙娘")
parser.add_argument('-p', '--page', type=int, help='set crawl pageNum default(1)', default=1)
parser.add_argument('-c', '--cookie', type=str, help='set your pixiv cookie', default="")
parser.add_argument('--timeout', type=int, help='set your pixiv cookie', default=15)

args = parser.parse_args()

# v
PROXY = args.proxy

proxy = {
    "http": args.proxy,
    "https": args.proxy
}

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 "
                  "Safari/537.36 SLBrowser/7.0.0.5211 SLBChan/25",
    "Referer": "https://www.pixiv.net/",
    "Cookie": args.cookie
}

searchImageURL = "https://www.pixiv.net/ajax/search/artworks/{tag}?word={tag}&order=date_d&mode=all&p={page}&s_mode=s_tag&type=all&lang=zh"

authorId = []

imageURL = []
imageId = []
imageSum = 0

totalPage = 0
num = 0
other = 0

time = 0
timeNow = 0


# Use json to get url, etc
def getSource(url):
    global totalPage
    global authorId
    global imageURL
    global imageId
    global imageSum

    try:
        res = requests.get(url=url.format(tag=args.tag, page=1), proxies=proxy, headers=header)

        allData = json.loads(res.text)["body"]["illustManga"]

        imageSum = allData["total"]
        totalPage = allData["lastPage"]
        data = allData["data"]

        for d in track(data):
            authorId.append(d["userId"])
            imageId.append(d["id"])
            imageBuffer = str(d["url"]).split('/', 6)
            imageBufferT = imageBuffer[6].rsplit('/', 1)
            imageURL.append(imageBuffer[0] + "//" + imageBuffer[2] + '/img-original/' + imageBufferT[0] + '/' +
                            imageBufferT[1].rsplit('_', 1)[0] + ".{extra}")

        if args.page == 0:
            for i in track(range(2, totalPage + 1)):
                res = requests.get(url=url.format(tag=args.tag, page=i), proxies=proxy, headers=header, timeout=args.timeout)

                data = json.loads(res.text)["body"]["illustManga"]["data"]

                for ii in data:
                    authorId.append(ii["userId"])
                    imageId.append(ii["id"])
                    imageBuffer = str(ii["url"]).split('/', 6)
                    imageBufferT = imageBuffer[6].rsplit('/', 1)
                    imageURL.append(imageBuffer[0] + "//" + imageBuffer[2] + '/img-original/' + imageBufferT[0] + '/' +
                                    imageBufferT[1].rsplit('_', 1)[0] + ".{extra}")
        elif args.page > 1:
            for i in track(range(2, args.page + 1)):
                res = requests.get(url=url.format(tag=args.tag, page=i), proxies=proxy, headers=header, timeout=args.timeout)

                data = json.loads(res.text)["body"]["illustManga"]["data"]

                for ii in data:
                    authorId.append(ii["userId"])
                    imageId.append(ii["id"])
                    imageBuffer = str(ii["url"]).split('/', 6)
                    imageBufferT = imageBuffer[6].rsplit('/', 1)
                    imageURL.append(imageBuffer[0] + "//" + imageBuffer[2] + '/img-original/' + imageBufferT[0] + '/' +
                                    imageBufferT[1].rsplit('_', 1)[0] + ".{extra}")
        elif args.page < 0:
            print("\033[91m[-] Error, page must be positive integer")
            exit()
    except requests.exceptions.ProxyError:
        print("\033[91m[-] Proxy error, please check your proxy\033[0m")
        exit()
    except requests.exceptions.RequestException:
        print("\033[91m[-] Network error, please check your network")
        print("\033[93m[*] If you are in China, you should use an proxy, try '-h' to get help\033[0m")
        exit()


# Check env
def check():
    global imageURL
    global time
    global timeNow
    global num
    global other

    timeNow = datetime.now()
    time = str(timeNow).split(' ')[0] + '-' + str(timeNow).split(' ')[1].rsplit('.')[0].replace(':', '-')

    if not path.exists("./ResImage"):
        mkdir("./ResImage")
    if not path.exists("./ResImage/{time}".format(time=time)):
        mkdir("./ResImage/{time}".format(time=time))

    if (len(imageURL) / 5) >= 1:
        num = int(len(imageURL) / 5)
        other = len(imageURL) % 5
    else:
        num = len(imageURL)


# UI
def UI():
    print("=====================================================================")
    print("           .__       .__                                 .__   ")
    print(r"    ______ |__|__  __|__|__  __ ________________ __  _  _|  |  ")
    print(r"    \____ \|  \  \/  /  \  \/ // ___\_  __ \__  \\ \/ \/ /  |  ")
    print(r"    |  |_> >  |>    <|  |\   /\  \___|  | \// __ \\     /|  |__")
    print(r"    |   __/|__/__/\_ \__| \_/  \___  >__|  (____  /\/\_/ |____/")
    print(r"    |__|            \/             \/           \/             ")
    print("                             Ver: 1.0")
    print("Author: 114514")
    print("Mail: admin@test.com")
    print("======================================================================")
    print("\033[93m[*] preparing...")


# Main
def main():
    global authorId
    global imageId
    global imageURL

    UI()
    getSource(searchImageURL)
    check()

    with Progress() as progress:
        if num >= 5:
            flagMore = False
            flagLess = False

            if other > 0:
                flagMore = True

                task1 = progress.add_task('ProcessOne', total=num)
                task2 = progress.add_task('ProcessTwo', total=num)
                task3 = progress.add_task('ProcessThree', total=num)
                task4 = progress.add_task('ProcessFour', total=num)
                task5 = progress.add_task('ProcessFive', total=num + other)

            task1 = progress.add_task('ProcessOne', total=num)
            task2 = progress.add_task('ProcessTwo', total=num)
            task3 = progress.add_task('ProcessThree', total=num)
            task4 = progress.add_task('ProcessFour', total=num)
            task5 = progress.add_task('ProcessFive', total=num)
        else:
            flagLess = True

            task = progress.add_task('Process', total=num)

        print("\033[96m[+] Start time: \n", timeNow)

        timeUse = tm()
        try:
            async def processOne():
                async with ClientSession() as session:
                    ii = 0
                    for i in imageURL[0: num]:
                        async with await session.get(url=i.format(extra="png"), headers=header, proxy=PROXY, timeout=args.timeout) as res:
                            if res.status == 404:
                                async with await session.get(url=i.format(extra="jpg"), headers=header, timeout=args.timeout,
                                                             proxy=PROXY) as resT:
                                    imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                        extra="jpg"), 'wb') as f:
                                        f.write(await resT.content.read())
                                    progress.update(task1, advance=1)
                                    ii += 1
                            else:
                                imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                    extra="png"), 'wb') as f:
                                    f.write(await res.content.read())
                                progress.update(task1, advance=1)
                                ii += 1

            async def processTwo():
                async with ClientSession() as session:
                    ii = num
                    for i in imageURL[num: num * 2]:
                        async with await session.get(url=i.format(extra="png"), headers=header, proxy=PROXY, timeout=args.timeout) as res:
                            if res.status == 404:
                                async with await session.get(url=i.format(extra="jpg"), headers=header,
                                                             proxy=PROXY, timeout=args.timeout) as resT:
                                    imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                        extra="jpg"), 'wb') as f:
                                        f.write(await resT.content.read())
                                    progress.update(task2, advance=1)
                                    ii += 1
                            else:
                                imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                    extra="png"), 'wb') as f:
                                    f.write(await res.content.read())
                                progress.update(task2, advance=1)
                                ii += 1

            async def processThree():
                async with ClientSession() as session:
                    ii = num * 2
                    for i in imageURL[num * 2: num * 3]:
                        async with await session.get(url=i.format(extra="png"), headers=header, proxy=PROXY, timeout=args.timeout) as res:
                            if res.status == 404:
                                async with await session.get(url=i.format(extra="jpg"), headers=header,
                                                             proxy=PROXY, timeout=args.timeout) as resT:
                                    imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                        extra="jpg"), 'wb') as f:
                                        f.write(await resT.content.read())
                                    progress.update(task3, advance=1)
                                    ii += 1
                            else:
                                imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                    extra="png"),
                                          'wb') as f:
                                    f.write(await res.content.read())
                                progress.update(task3, advance=1)
                                ii += 1

            async def processFour():
                async with ClientSession() as session:
                    ii = num * 3
                    for i in imageURL[num * 3: num * 4]:
                        async with await session.get(url=i.format(extra="png"), headers=header, proxy=PROXY, timeout=args.timeout) as res:
                            if res.status == 404:
                                async with await session.get(url=i.format(extra="jpg"), headers=header,
                                                             proxy=PROXY, timeout=args.timeout) as resT:
                                    imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                        extra="jpg"), 'wb') as f:
                                        f.write(await resT.content.read())
                                    progress.update(task4, advance=1)
                                    ii += 1
                            else:
                                imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                    extra="png"),
                                          'wb') as f:
                                    f.write(await res.content.read())
                                progress.update(task4, advance=1)
                                ii += 1

            if flagMore:
                async def processFive():
                    async with ClientSession() as session:
                        ii = num * 4
                        for i in imageURL[num * 4: num * 5 + other]:
                            async with await session.get(url=i.format(extra="png"), headers=header, proxy=PROXY, timeout=args.timeout) as res:
                                if res.status == 404:
                                    async with await session.get(url=i.format(extra="jpg"), headers=header,
                                                                 proxy=PROXY, timeout=args.timeout) as resT:
                                        imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                            extra="jpg"), 'wb') as f:
                                            f.write(await resT.content.read())
                                        progress.update(task5, advance=1)
                                        ii += 1
                                else:
                                    imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                        extra="png"), 'wb') as f:
                                        f.write(await res.content.read())
                                    progress.update(task5, advance=1)
                                    ii += 1
            elif flagLess:
                async def processFive():
                    async with ClientSession() as session:
                        ii = num
                        for i in imageURL:
                            async with await session.get(url=i.format(extra="png"), headers=header, proxy=PROXY, timeout=args.timeout) as res:
                                if res.status == 404:
                                    async with await session.get(url=i.format(extra="jpg"), headers=header,
                                                                 proxy=PROXY, timeout=args.timeout) as resT:
                                        imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                            extra="jpg"), 'wb') as f:
                                            f.write(await resT.content.read())
                                        progress.update(task, advance=1)
                                        ii += 1
                                else:
                                    imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                        extra="png"), 'wb') as f:
                                        f.write(await res.content.read())
                                    progress.update(task, advance=1)
                                    ii += 1
            else:
                async def processFive():
                    async with ClientSession() as session:
                        ii = num * 4
                        for i in imageURL[num * 4: num * 5]:
                            async with await session.get(url=i.format(extra="png"), headers=header, proxy=PROXY, timeout=args.timeout) as res:
                                if res.status == 404:
                                    async with await session.get(url=i.format(extra="jpg"), headers=header,
                                                                 proxy=PROXY, timeout=args.timeout) as resT:
                                        imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                        with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                            extra="jpg"), 'wb') as f:
                                            f.write(await resT.content.read())
                                        progress.update(task5, advance=1)
                                        ii += 1
                                else:
                                    imageName = str(authorId[ii]) + '-' + str(imageId[ii])
                                    with open("./ResImage/{time}/{name}.{extra}".format(time=time, name=imageName,
                                                                                        extra="png"), 'wb') as f:
                                        f.write(await res.content.read())
                                    progress.update(task5, advance=1)
                                    ii += 1

            loop = asyncio.get_event_loop()

            task11 = asyncio.ensure_future(processOne())
            task22 = asyncio.ensure_future(processTwo())
            task33 = asyncio.ensure_future(processThree())
            task44 = asyncio.ensure_future(processFour())
            task55 = asyncio.ensure_future(processFive())

            tasks = [task11, task22, task33, task44, task55]

            loop.run_until_complete(asyncio.wait(tasks))

        except requests.exceptions.ProxyError:
            print("\033[91m[-] Proxy error, please check your proxy\033[0m")
            exit()
        except requests.exceptions.RequestException:
            print("\033[91m[-] Network error, please check your network")
            print("\033[93m[*] If you are in China, you should use an proxy, try '-h' to get help\033[0m")
            exit()

    print("\n\033[96m[+] Used time:", tm() - timeUse, 'sec\033[0m')


if __name__ == "__main__":
    main()
