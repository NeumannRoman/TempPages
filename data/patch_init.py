from subprocess import run

from util import replace, readConstants


def gitPush():
  run(["git", "add", "."])
  run(["git", "commit", "-m", "Patched init."])
  run(["git", "push", "origin", "main"])

def patchInitIndex():
  base = "data/html/init_base.html"
  target = "index.html"
  cons = readConstants()
  data = None
  with open(base, "r") as file:
    data = file.readlines()
    for i in range(len(data)):
      if "%1" in data[i]: replace(data, i, "%1", cons["server"]["address"])
      if "%2" in data[i]: replace(data, i, "%2", cons["server"]["port"])
      if "%3" in data[i]: replace(data, i, "%3", cons["plotly"]["font-family"])
  with open(target, "w") as file:
    file.writelines(data)
  gitPush()


if __name__ == "__main__":
  patchInitIndex()