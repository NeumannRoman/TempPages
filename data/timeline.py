from json import load as json_load
from math import inf

from numpy import concatenate, flip, repeat
import plotly.graph_objects as go
import plotly.io as pio

from data.util import read, readPlotly, adjustHTML, colorIsLighter
from data.date import Date


CONS : dict = readPlotly()
CONS.update({
  "margin" : CONS["timestrip-height"] / 8. + CONS["timestrip-height"],
  "offset" : CONS["timestrip-height"] / 2.
})

class Timestrip:
  def __init__(self, start, end, event, special, index, color):
    self.start = start
    self.end = end
    self.event = event
    self.showStart = "Start" in special
    self.showEnd = "End" in special
    self.showEvent = "Label" in special
    self.isFiller = "Filler" in special
    
    self.index = index
    self.color = CONS["default-timestrip-color"] if not color else color

  def createText(self):
    return f"<b>Start</b>: {str(self.start)}<br>" \
      f"<b>End</b>: {str(self.end)}<br>" \
      f"<b>Event</b>: {self.event}<br>"

  def addTrace(self, fig):
    if not self.isFiller and (self.start is not None or self.end is not None):
      x = [float(self.start), float(self.end)] # from [0, 10]
      x = concatenate((x, flip(x, 0)))         # to   [0, 10, 10, 0]

      y0 = self.index * CONS["margin"] + CONS["offset"]
      y = [y0, y0 + CONS["timestrip-height"]] # from [0.5, 1.5]
      y = repeat(y, 2)                # to   [0.5, 0.5, 1.5, 1.5]

      fig.add_trace(go.Scatter(
        x = x,
        y = y,
        fill = "toself",
        fillcolor = self.color,
        line_color = "rgba(255, 255, 255, 0)",
        showlegend = False,
        opacity = CONS["timestrip-opacity"],
        hovertemplate = "%{text}<extra></extra>", # NOTE: empty <extra> tag (should) remove trace name
        name = "", # NOTE: remove trace name from hover data
        text = self.createText(),
      ))

  def addLabel(self, fig):
    if self.showEvent and not self.isFiller and (self.start is not None or self.end is not None):
      fig.add_annotation(
        text = f"<b>{self.event}</b>",
        showarrow = False,
        x = (float(self.start) + float(self.end)) * 0.5,
        y = self.index * CONS["margin"] + CONS["offset"] + CONS["timestrip-height"] / 2.0,
        font = dict(
          color = CONS["dark-font-color"] if colorIsLighter(self.color) else CONS["light-font-color"],
          size = CONS["label-font-size"]
        )
      )

  def getTickList(self):
    ticks = []
    if self.showStart and self.start is not None:
      ticks.append( [float(self.start), str(self.start)] )
    if self.showEnd and self.end is not None:
      ticks.append( [float(self.end), str(self.end)] )
    return ticks

class Timeline:
  CONS = readPlotly()

  def __init__(self):
    self.figure : go.Figure = go.Figure()
    self.strips : list[Timestrip] = []
    self.minValue = inf if not CONS["min-date"] else float(Date.fromString(CONS["min-date"]))
    self.maxValue = -inf if not CONS["max-date"] else float(Date.fromString(CONS["max-date"]))

  def addStrip(self, obj):
    strip = Timestrip(index = len(self.strips), **obj)
    self.strips.append(strip)

    if strip.start is not None and not CONS["min-date"]:
      self.minValue = float(strip.start) if float(strip.start) < self.minValue else self.minValue
    if strip.end is not None and not CONS["max-date"]:
      self.maxValue = float(strip.end) if float(strip.end) > self.maxValue else self.maxValue

  def initFromJSON(self, content):
    for obj in content:
      obj["start"] = Date.fromString(obj["start"])
      obj["end"] = Date.fromString(obj["end"])
      self.addStrip(obj)

  def updateLayout(self):
    x_width = self.maxValue - self.minValue
    y_width = len(self.strips) * CONS["margin"] + CONS["offset"]
    y_frac = CONS["offset"] / float(y_width)
    x_offset = x_width * (y_frac / 4.0)

    tickLists = [ strip.getTickList() for strip in self.strips ]
    ticks = { 
      "vals" : [ pair[0] for lst in tickLists for pair in lst ], # NOTE : nested list comprehension is rather confusing
      "text" : [ pair[1] for lst in tickLists for pair in lst ]
    }

    axisColor = CONS["dark-font-color"] if colorIsLighter(CONS["background-color"]) else CONS["light-font-color"]
    tickFont = dict(size = CONS["tick-font-size"])
    self.figure.update_layout(
      xaxis = dict(
        range = [self.minValue - x_offset, self.maxValue + x_offset],
        tickmode = "array",
        tickvals = ticks["vals"],
        ticktext = ticks["text"],
        tickangle = 90 if CONS["static-tick-angle"] else None,
        zeroline = False,
        color = axisColor,
        tickfont = tickFont
      ),
      yaxis = dict(
        range = [0, y_width],
        tickmode = "array",
        tickvals = [],
        ticktext = [],
        zeroline = False,
        color = axisColor,
        tickfont = tickFont
      ),
      paper_bgcolor = CONS["background-color"],
      plot_bgcolor = CONS["background-color"],
      margin = dict(b = 50, l = 50, r = 50, t = 50),
      hoverlabel = dict(
        font = dict(size = CONS["hover-font-size"])
      ),
      font = dict(
        family = CONS["font-family"]
      )
    )
  
  def updateTraces(self):
    self.figure.update_traces(
      mode = "lines", # only show lines, not scatterpoints
      textposition = "middle center"
    )

  def show(self):
    for strip in self.strips:
      strip.addTrace(self.figure)
      strip.addLabel(self.figure)

    self.updateLayout()
    self.updateTraces()

    pio.write_html(
      self.figure, 
      file = "data/html/local/timeline.html", 
      validate = False, 
      auto_open = False,
      config = dict(
        scrollZoom = True, 
        displaylogo = False,
        modeBarButtonsToRemove = ["resetScale"]
    ))
    adjustHTML()


# NOTE : static
def redrawTimeline():
  timeline = Timeline()

  with read("content.json") as file:
    content = json_load(file)
    timeline.initFromJSON(content)

  timeline.show()
