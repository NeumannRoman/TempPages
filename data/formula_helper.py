from util import write


def func(name, params):
  string = f"{name}("
  for i in range(len(params)):
    if i != 0: string += ", "
    string += f"{params[i]}"
  return string + ")"
def op(op, first, second):
  return f"({first}) {op} ({second})"

def _if(test, true, false):
  return func("if", [test, true, false])
def _and(first, second):
  return op("and", first, second)
def _or(first, second):
  return op("or", first, second)
def _less(first, second):
  return op("<", first, second)
def _equal(first, second):
  return op("==", first, second)
def _str(val):
  return f'"{val}"'
def _test(first, second):
  return func("test", [first, second])
def _num(name, indices):
  return f"toNumber(slice(prop({_str(name)}), {indices[0]}, {indices[1]}))"



def regex(format, name):
  ex = None
  if format == "oneOne":
    ex = r'"^\d\.\d\.-?\d+$"'
  elif format == "oneTwo":
    ex = r'"^\d\.\d\d\.-?\d+$"'
  elif format == "twoOne":
    ex = r'"^\d\d\.\d\.-?\d+$"'
  elif format == "twoTwo":
    ex = r'"^\d\d\.\d\d\.-?\d+$"'
  elif format == "one":
    ex = r'"^\d\.-?\d+$"'
  elif format == "two":
    ex = r'"^\d\d\.-?\d+$"'
  elif format == "year":
    ex = r'"^-?\d+$"'
  return _test(f"prop({_str(name)})", ex)
def day(format, name):
  indices = None
  if format == "oneOne":
    indices = [0, 1]
  elif format == "oneTwo":
    indices = [0, 1]
  elif format == "twoOne":
    indices = [0, 2]
  elif format == "twoTwo":
    indices = [0, 2]
  return _num(name, indices) if format not in ["one", "two", "year"] else "1"
def month(format, name):
  indices = None
  if format == "oneOne":
    indices = [2, 3]
  elif format == "oneTwo":
    indices = [2, 4]
  elif format == "twoOne":
    indices = [3, 4]
  elif format == "twoTwo":
    indices = [3, 5]
  elif format == "one":
    indices = [0, 1]
  elif format == "two":
    indices = [0, 2]
  return _num(name, indices) if format != "year" else "1"
def year(format, name):
  indices = [None, f'length(prop({_str(name)}))']
  if format == "oneOne": indices[0] = 4
  elif format == "oneTwo": indices[0] = 5
  elif format == "twoOne": indices[0] = 5
  elif format == "twoTwo": indices[0] = 6
  elif format == "one": indices[0] = 2
  elif format == "two": indices[0] = 3
  elif format == "year": indices[0] = 0
  return _num(name, indices)
def _date(format, name):
  return {
    "year" : year(format, name),
    "month" : month(format, name),
    "day" : day(format, name)
  }



def checkOrder(s, e):
  return _or(
    _or(
      _less(s["year"], e["year"]),
      _and(
          _equal(s["year"], e["year"]),
          _less(s["month"], e["month"])
      )
    ), 
    _and(
      _equal(s["year"], e["year"]),
      _and(
        _equal(s["month"], e["month"]),
        _less(s["day"], e["day"])
      )
    )
  )
def logicBlock(sFormat, eFormat, i):
  return _if(
    _and(
      regex(sFormat, "Start"), 
      regex(eFormat, "End")
    ),
    checkOrder(_date(sFormat, "Start"), _date(eFormat, "End")), 
    f"%{i}"
  )
def writeValidOrder():
  formats = ["oneOne", "oneTwo", "twoOne", "twoTwo", "one", "two", "year"]
  lst = []
  i = 1
  for sFormat in formats:
    for eFormat in formats:
      lst.append(logicBlock(sFormat, eFormat, i))
      i += 1
  lst.append("false") # if whole cascade fails return false

  result = "%0"
  length = len(lst)
  for i in range(length):
    result = result.replace(f"%{i}", lst.pop(0))

  with write("notion/formula_valid_order.txt") as validOrder :
    validOrder.write(result)



if __name__ == "__main__":
  writeValidOrder()
