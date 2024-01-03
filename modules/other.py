import json

from os import path, mkdir


class Help(object):
    def __init__(self):
        self.i = "[\033[96mInfo\033[0m]"
        self.w = "[\033[93mWarning\033[0m]"
        self.e = "[\033[91mError\033[0m]"
        self.t = "[\033[92mTips\033[0m]"

    @staticmethod
    def color(colors, string):
        if colors == "blue":
            return "\033[96m{string}\033[0m".format(string=string)
        elif colors == "green":
            return "\033[92m{string}\033[0m".format(string=string)
        elif colors == "red":
            return "\033[91m{string}\033[0m".format(string=string)
        elif colors == "yellow":
            return "\033[93m{string}\033[0m".format(string=string)
        else:
            return "\033[0m{string}".format(string=string)


class Config(object):
    def __init__(self):
        self.path = "./config"
        self.jsonpath = "./config/config.json"

        if not path.exists(self.path):
            mkdir(self.path)
            with open(self.jsonpath, "w") as f:
                f.write("{\"userSetting\": {\"Cookie\": \"\"}}")
        elif not path.exists(self.jsonpath):
            with open(self.jsonpath, "w") as f:
                f.write("{\"userSetting\": {\"Cookie\": \"\"}}")

    def setCookie(self, cookie):
        with open(self.jsonpath, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            old_data["userSetting"]["Cookie"] = cookie
        with open(self.jsonpath, "w", encoding="utf-8") as f:
            json.dump(old_data, f, ensure_ascii=False)
        print(f"[\033[96mInfo\033[0m] Cookie updated!")

    def saveId(self, authorid):
        allId = authorid.split(",")

        with open(self.jsonpath, "r", encoding="utf-8") as f:
            old_data = json.load(f)
            savedNum = len(old_data["userSetting"]["Id"])

            for i in range(len(allId)):
                old_data["userSetting"]["Id"][str(i + savedNum)] = allId[i]

        with open(self.jsonpath, "w", encoding="utf-8") as f:
            json.dump(old_data, f, ensure_ascii=False)
        print(f"[\033[96mInfo\033[0m] Id saved!")
