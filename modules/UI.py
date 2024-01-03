from modules.other import Help
from modules.search import Search
from modules.args import *

from sys import exit

h = Help()


# UI
def showUI():
    print("=====================================================================")
    print(r"           .__       .__                                 .__   ")
    print(r"    ______ |__|__  __|__|__  __ ________________ __  _  _|  |  ")
    print(r"    \____ \|  \  \/  /  \  \/ // ___\_  __ \__  \\ \/ \/ /  |  ")
    print(r"    |  |_> >  |>    <|  |\   /\  \___|  | \// __ \\     /|  |__")
    print(r"    |   __/|__/__/\_ \__| \_/  \___  >__|  (____  /\/\_/ |____/")
    print(r"    |__|            \/             \/           \/             ")
    print("                             Ver: 1.0")
    print("Author: chumo")
    print("Mail: admin@test.com")
    print("======================================================================")


def get_author_id():
    if args.authorname is not None:
        print(f"{h.i} Start search author")
        search = Search(args.authorname, args.proxy, args.timeout, args.cookie)

        args.id = search.search()

        print(f"{h.i} Succeed\n======================================================================")
        return True
    else:
        return False


def checkArgs(status):
    if args.proxy is not None:
        print(f"{h.i} Proxy: {h.color('blue', args.proxy)}")

    print(f"{h.t} Cookie is not necessary, but if you don't give a valid Cookie, may you {h.color('red', 'cannot get')} all the correct data")

    if args.cookie == "":
        print(f"{h.w} {h.color('red', 'Cookie not set')}")
    else:
        print(f"{h.i} Cookie: {h.color('blue', args.cookie)}")

    if args.mode == "tag":
        print(f"{h.i} Tag: {h.color('blue', args.tag)}")
    else:
        if args.id is not None:
            if status:
                print(f"{h.i} AuthorName: {args.authorname} => {h.color('blue', args.id)}")
            else:
                print(f"{h.i} AuthorId: {h.color('blue', args.id)}")
        else:
            print(f"{h.w}  {h.color('red', 'AuthorId not set')}")
            exit()

    print(f"{h.i} Request interval time: {args.sleep} sec")

    if args.page == 0:
        print(f"{h.i} Page to crawl: {h.color('green', 'ALL')}")
    else:
        print(f"{h.i} Page to crawl: {args.page}")

    print(f"{h.i} Timeout: {args.timeout}")
    print("======================================================================")


def Usage():
    print("Usage: ")
    print("    python pixivcrawl.py [-h] [--help]")
