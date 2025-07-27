import os
import glob
import argparse
from aiohttp import web
from xoxxox.params import Config, Medium
from xoxxox.shared import Custom

#---------------------------------------------------------------------------
# 定数：設定

parser = argparse.ArgumentParser()
parser.add_argument("--secure", default="0")
parser.add_argument("--svport", type=int, default="80")
parser.add_argument("--adraco", type=str) # default: cnfnet
parser.add_argument("--pthcrt", type=str) # default: cnfnet
parser.add_argument("--pthkey", type=str) # default: cnfnet
objarg = parser.parse_args()

dicnet = Custom.update(Config.cnfnet, {k: v for k, v in vars(objarg).items() if v is not None})

secure = objarg.secure
svport = objarg.svport

#---------------------------------------------------------------------------

@web.middleware
async def mwcors(datreq, handler):
  datres = await handler(datreq)
  datres.headers["Access-Control-Allow-Origin"] = dicnet["adraco"]
  return datres

#---------------------------------------------------------------------------
# 実行

appweb = web.Application()
appweb.middlewares.append(mwcors)
l = glob.glob(Medium.dirweb + "/*")
for d in l:
  appweb.add_routes([web.static("/" + os.path.basename(d), d)])

if secure == "0":
  web.run_app(appweb, port=svport)
if secure == "1":
  import ssl
  sslcon = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  sslcon.load_cert_chain(dicnet["pthcrt"], dicnet["pthkey"])
  web.run_app(appweb, port=svport, ssl_context=sslcon)
