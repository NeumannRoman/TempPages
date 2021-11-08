class Date:
  def __init__(self, year, month, day):
    self.year = year
    self.month = month
    self.day = day

  @classmethod
  def fromString(cls, string : str):
    if not string: return None

    values = None
    if "." in string:
      values = [ int(v) for v in string.split(".") ]
      values.reverse()
    if not values:
      return cls(int(string), 1, 1)
    elif len(values) == 2:
      return cls(*values, 1)
    else: 
      return cls(*values)

  def __str__(self):
    hasMonth = self.month > 0
    hasDay = self.day > 0
    month = self.month if self.month > 9 else f"0{self.month}"
    day = self.day if self.day > 9 else f"0{self.day}"
    date = ""

    if hasDay and hasMonth:
      date += f"{day}."
    if hasMonth:
      date += f"{month}."
    date += f"{self.year}"

    return date

  def __float__(self):
    # NOTE: inaccurate
    return self.year * 365.25 + self.month * 30.5 + self.day
