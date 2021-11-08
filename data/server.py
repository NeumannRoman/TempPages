from http.server import HTTPServer, BaseHTTPRequestHandler
from traceback import format_exc
from time import sleep
import cgi

from data.notion_interface import NotionInterface
from data.util import readServer, read
from data.timeline import redrawTimeline


CONS = readServer()

def printProcess(message, i = -1, n = -1):
  progress = f"[{i}/{n}] " if (i > -1 and n > -1) else ""
  print(f"{progress}{message} . . .")

def printInput(message):
  print(f"< {message} >")

def printServerRunning():
  printProcess("Server running. Beep boop")


class TL_Handler(BaseHTTPRequestHandler):
  NOTION = NotionInterface()

  def isRequested(self, ressource):
    return ressource in self.requestline

  def writeGET(self, contentType, path):
    self.send_header("Content-Type", contentType)
    if path is None:
      self.send_header("Content-Length", "0")
    self.end_headers()
    if path is not None:
      with read(path, "rb") as file:
        for line in file.readlines():
          self.wfile.write(line)


  def getCSS(self):
    self.writeGET("text/css", "html/local/style.css")

  def getICON(self):
    self.writeGET("image/x-icon", "html/local/icon.ico")

  def getHTML(self):
    self.writeGET("text/html", "html/local/timeline.html")

  def do_GET(self):
    self.send_response(200) # 'HTTP:200 OK'
    if self.isRequested("style"):
      self.getCSS()
    elif self.isRequested("favicon"):
      self.getICON()
    else:
      self.getHTML()
    print("-" * 75)


  def getFormValue(self, name):
    return cgi.FieldStorage(
      fp = self.rfile,
      headers = self.headers,
      environ = {
        "REQUEST_METHOD" : "POST",
        "CONTENT_TYPE": self.headers["Content-Type"]
      }
    ).getvalue(name)

  def query(self):
    printProcess("Collecting Data", 1, 2)
    return self.NOTION.queryTable()

  def redraw(self):
    printProcess("Drawing Timeline", 2, 2)
    redrawTimeline()

  def redirect(self):
    self.send_response(301) # 'HTTP:301 Moved Permanently'
    self.send_header("Location", f'http://{CONS["address"]}:{CONS["port"]}')
    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
    self.send_header("Pragma", "no-cache")
    self.send_header("Expires", "0")
    self.end_headers()

  def do_POST(self):
    if self.getFormValue("update"):
      if self.query(): self.redraw()
      self.redirect()
    else:
      self.do_GET()
    print("-" * 75)


class TL_Server:
  def __init__(self):
    self.internal = HTTPServer(
      server_address = (CONS["address"], int(CONS["port"])),
      RequestHandlerClass = TL_Handler
    )

  def start(self):
    try:
      printServerRunning()
      self.internal.serve_forever(poll_interval = 2)
    except KeyboardInterrupt:
      pass
    except Exception:
      print(format_exc())
      printInput("Press any key")
      input()
    
    printProcess("Shutting down")
    self.internal.server_close()
    sleep(1)
