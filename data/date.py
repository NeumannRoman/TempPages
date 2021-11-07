class Date:
  def __init__(self, year, month, day):
    self.year = year
    self.month = month
    self.day = day

  @classmethod
  def fromString(cls, string : str):
    if not string: return None
    values = [ int(v) for v in string.split(".") ]
    if len(values) == 3:
      day, month, year = values
    elif len(values) == 2:
      day, month, year = 1, values
    else:
      day, month, year = 1, 1, values[0]
    return cls(year, month, day)

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
