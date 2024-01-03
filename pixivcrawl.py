from modules.args import *
from modules.UI import *
from modules.get_by_tags import GetImageByTag
from modules.get_by_author import GetImageByAuthor
from modules.config import *

if __name__ == "__main__":
    showUI()
    if args.mode != "config":
        if path.exists("./config/config.json"):
            with open("./config/config.json", "r") as f:
                userSetting = json.load(f)["userSetting"]

            if userSetting["Cookie"] != "":
                args.cookie = userSetting["Cookie"]

            if len(userSetting["Id"]) != 0 and args.usesavedid is not None:
                args.id = userSetting["Id"][str(args.usesavedid)]

        checkArgs(get_author_id())
    if args.mode == "tag":
        way = GetImageByTag(args.tag, args.page, args.timeout, args.cookie)
        way.get_image_by_tags()
    elif args.mode == "author":
        way = GetImageByAuthor(args.id, args.page, args.timeout, args.cookie)
        way.get_image_by_author()
    elif args.mode == "config":
        if args.setcookie is not None:
            setCookie(args.setcookie)
        if args.saveid is not None:
            saveId(args.saveid)
    else:
        Usage()
