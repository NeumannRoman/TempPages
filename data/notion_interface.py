from requests.structures import CaseInsensitiveDict
from json import dumps as json_dumps
from traceback import format_exc
from math import inf
import requests

from data.util import readNotion, write


class NotionInterface:
  CONS = readNotion()

  def strEq(self, val : str, test : str):
    return val.lower() == test.lower()
  def isTable(self, element):
    return self.strEq(element, "table")
  def isGetRequest(self, type):
    return self.strEq(type, "GET")
  def isPostRequest(self, type):
    return self.strEq(type, "POST")
  def isPatchRequest(self, type):
    return self.strEq(type, "PATCH")
  
  def getID(self, element):
    if self.isTable(element):
      return self.CONS["table-id"]
    else:
      return None

  def getTarget(self, element):
    if self.isTable(element):
      return "databases"
    else:
      return None

  def getURL(self, type, element):
    appendable = "/query" if not self.isGetRequest(type) else ""
    target = self.getTarget(element)
    id = self.getID(element)
    return f"https://api.notion.com/v1/{target}/{id}{appendable}"

  def getHeaders(self, type):
    headers = CaseInsensitiveDict({
      "Authorization" : f"Bearer {self.CONS['api-key']}",
      "Notion-Version" : self.CONS["notion-version"]
    })
    if not self.isGetRequest(type):
      headers["Content-Type"] = "application/json"
    return headers

  def getData(self, type, element):
    if self.isTable(element) and self.isPostRequest(type):
      return json_dumps(self.CONS["data"])
    else:
      return None

  def getKwargs(self, type, element):
    kwargs = {
      "url" : self.getURL(type, element),
      "headers" : self.getHeaders(type)
    }
    if not self.isGetRequest(type): 
      kwargs["data"] = self.getData(type, element)
    return kwargs

  def doRequest(self, type, element) -> requests.Response:
    kwargs = self.getKwargs(type, element)
    response = None
    if self.isGetRequest(type):
      response = requests.get(**kwargs)
    elif self.isPostRequest(type):
      response = requests.post(**kwargs)
    elif self.isPatchRequest(type):
      response = requests.patch(**kwargs)
    return response.json() if response else None

  def writeJSON(self, objects):
    with write("content.json") as out:
      out.write(json_dumps(objects))

  def getPropListText(self, props, key0, key1):
    lst = props[key0][key1]
    return lst[0]["plain_text"] if lst else ""
  def getPropTitle(self, props):
    return self.getPropListText(props, "Event", "title")
  def getPropRichText(self, props, name):
    return self.getPropListText(props, name, "rich_text")
  def getPropSpecial(self, props):
    return [ entry["name"] for entry in props["Special"]["multi_select"] ]

  def extractProps(self, props):
    return {
      "event" : self.getPropTitle(props),
      "start" : self.getPropRichText(props, "Start"),
      "end" : self.getPropRichText(props, "End"),
      "color" : self.getPropRichText(props, "Color"),
      "special" : self.getPropSpecial(props)
    }

  def queryTable(self):
    success = False
    response = self.doRequest("post", "table")
    try:
      objects = []
      for i in range(len(response["results"])):
        props = response["results"][i]["properties"]
        obj = self.extractProps(props)
        num = props["Order"]["number"]
        if num is None: num = -inf
        objects.append((obj, num))
      objects.sort(key = lambda x : x[1])
      objects = [ pair[0] for pair in objects ]
      objects.reverse() # NOTE : strips are added to the plot from the bottom: reversing orders the final plot from top to bottom
      self.writeJSON(objects)
      success = True
    except:
      print(format_exc())
    return success

