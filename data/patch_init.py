from subprocess import run

from util import replace, readServer


def gitPush(targets):
  run(["git", "add", *targets])
  run(["git", "commit", "-m", "Patched init."])
  run(["git", "push", "origin", "main"])

def patchInitIndex():
  base = "html/init_base.html"
  target = "index.html"
  cons = readServer()
  data = None
  with open(base, "r") as file:
    data = file.readlines()
    for i in range(len(data)):
      replace(data, i, "%1", cons["address"])
      replace(data, i, "%2", cons["port"])
      break
  with open(target, "w") as file:
    file.writelines(data)

  gitPush(target)


if __name__ == "__main__":
  patchInitIndex()