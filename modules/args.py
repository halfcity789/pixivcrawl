import argparse
import json

from os import path

# args
parser = argparse.ArgumentParser(description='a script to crawl images of pixiv')

parser.add_argument('mode', type=str, help='set modes ([tag], [author],  [config])')
parser.add_argument('--proxy', type=str, help='set proxy', default=None)
parser.add_argument('-t', '--tag', type=str, help='set tag', default="龙娘")
parser.add_argument('-n', '--authorname', type=str, help='set author name', default=None)
parser.add_argument('-i', '--id', type=int, help='set author id(better than "-n")', default=None)
parser.add_argument('-p', '--page', type=int, help='set crawl pageNum default(0), set 0 to choose "ALL"', default=0)
parser.add_argument('--timeout', type=int, help='set your pixiv cookie', default=30)
parser.add_argument('-s', '--sleep', type=int, help='set request interval time', default=0.5)
parser.add_argument('-c', '--cookie', type=str, help='set your pixiv cookie', default="")
parser.add_argument('-ua', '--useragent', type=str, help='set your UA header', default=None)
parser.add_argument('--setcookie', type=str, help='set your default cookie', default=None)
parser.add_argument('--saveid', type=str, help='save author id which you like', default=None)
parser.add_argument('--usesavedid', type=str, help='use the id in json file[path:./config/config.json] to set author id', default=None)

args = parser.parse_args()


