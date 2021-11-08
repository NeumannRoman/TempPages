from json import load as jsonLoad
from os import path


def colorIsLighter(hex : str):
  value = int(hex.replace("#", "0x"), 16)
  r = value >> 16 & 0xFF
  g = value >> 8 & 0xFF
  b = value >> 0 & 0xFF
  return (r + g + b) > (127 * 3)


def _open(file, mode):
  dir = path.dirname(path.abspath(__file__))
  return open(path.join(dir, file), mode)

def read(file, type = None):
  return _open(file, "r" if type is None else type)

def write(file, type = None):
  return _open(file, "w" if type is None else type)

def readConstants():
  content = None
  with read("../properties.json") as file:
    content = jsonLoad(file)
  return content

def readServer():
  return readConstants()["server"]
def readNotion():
  return readConstants()["notion"]
def readPlotly():
  return readConstants()["plotly"]


def replace(data, i, toReplace, content):
  data[i] = data[i].replace(toReplace, content)

def replaceHead(data, i, content):
  replace(data, i, "<head>", f"<head>{content}\n")

def formatStylesheet(cons):
  fontColor = cons["dark-font-color"] if colorIsLighter(cons["default-timestrip-color"]) else cons["light-font-color"]
  data = None
  with read("html/style_base.css") as file:
    data = file.readlines()
  with read("html/drag_bars.css") as file:
    data.extend(file.readlines())
  for i in range(len(data)):
    if "%1" in data[i]: replace(data, i, "%1", cons["background-color"])
    elif "%2" in data[i]: replace(data, i, "%2", cons["default-timestrip-color"])
    elif "%3" in data[i]: replace(data, i, "%3", fontColor)
    elif "%4" in data[i]: replace(data, i, "%4", cons["font-family"])
  with write("html/local/style.css") as file:
    file.writelines(data)

def insertHead(data, i):
  temp = '<link rel="stylesheet" href="%1">'
  replaceHead(data, i, temp.replace("%1", "data/html/local/style.css"))
  replaceHead(data, i, temp.replace("%1", "https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css"))
  replaceHead(data, i, '<link rel="icon" href="data/html/local/icon.ico">')
  replaceHead(data, i, "<title>Notion Timeline</title>")

def insertButtons(data, i, cons):
  content = None
  with read("html/insert.html") as file:
    content = file.readlines()
    for j in range(len(content)):
      if "%" in content[j]: 
        replace(content, j, "%1", cons["address"])
        replace(content, j, "%2", cons["port"])
        break

  content.insert(0, data[i].replace("<div>", "<div style='position: relative;'>"))
  data[i] = f"{''.join(content)}\n"

def movePlotlyModebar(data, search, i):
  replace(data, i, search, "position:absolute;top:10px;left:20%;") # NOTE : hacky : modebar is only line of code with this value

def removeDragbarFill(data, search, i):
  replace(data, i, search, search[:-len('fill:"transparent",',)])

def adjustHTML():
  dragbarClassed = 'classed("drag",!0).style({fill:"transparent",'
  oldPos = "position:absolute;top:2px;right:2px;"
  cons : dict = readServer()
  cons.update(readPlotly())
  data = None

  with read("html/local/timeline.html") as file:
    data = file.readlines()

  for i in range(len(data)):
    if "<head>" in data[i]: insertHead(data, i)
    if "<div>" in data[i]: insertButtons(data, i, cons)
    if oldPos in data[i]: movePlotlyModebar(data, oldPos, i)
    if dragbarClassed in data[i]: removeDragbarFill(data, dragbarClassed, i)

  with write("html/local/timeline.html") as file:
    file.writelines(data)
  formatStylesheet(cons)
