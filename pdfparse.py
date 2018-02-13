from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
import pdfminer, pdfminer.layout
from pdfminer.layout import LAParams, LTTextBox, LTRect, LTLine, LTTextLine, LTFigure, LTTextLineHorizontal, LTTextBoxHorizontal
from pdfminer.converter import PDFPageAggregator
import json, time, re
from match_keywords import match_keywords
from utils import format_text, find_in
from numpy import random

SCHEDULE_FILE = "schedule_jan18.pdf"
FONT_SIZE = 5
CREATE_SVG = False
SHOW_TEXTBOXES = False

rects = []
dates = []
textboxes = []
courses = {}

def randomColor():
    de = "{:02x}".format(random.randint(256))
    re = "{:02x}".format(random.randint(256))
    we = "{:02x}".format(random.randint(256))
    return de + re + we

def getRectCoords(coords):
    ret = [round(c) for c in list(coords)]
    ret[1] = 600 - ret[1]
    ret[3] = 600 - ret[3]
    return ((ret[0], ret[3]), (ret[2], ret[1]))

def rectsToLines(rects):
    l = []
    for r in rects:
        # check if small rectangle
        if dist2(r[0], r[1]) < 8:
            continue
        # check if horizontal line
        if abs(r[0][1] - r[1][1]) < 4:
            l.append(((r[0][0], r[0][1]), (r[1][0], r[0][1])))
        # check if vertical line
        elif abs(r[0][0] - r[1][0]) < 4:
            l.append(((r[0][0], r[0][1]), (r[0][0], r[1][1])))
        # else break rectangle into four lines
        else:
            # top
            l.append(((r[0][0], r[0][1]), (r[1][0], r[0][1])))
            # right
            l.append(((r[1][0], r[0][1]), (r[1][0], r[1][1])))
            # bottom
            l.append(((r[0][0], r[1][1]), (r[1][0], r[1][1])))
            # left
            l.append(((r[0][0], r[0][1]), (r[0][0], r[1][1])))
    return l

def dist2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2

# lines should be sorted
def mergeLines(lines):
    # check close lines O(n^2)
    sortH = sorted(lines, key = lambda x: x[1][1])
    sortH.sort(key = lambda x: x[0][1])
    lst = []
    for candidate in sortH:
        flag = False
        for check in lst:
            if dist2(candidate[0], check[0]) < 8 and dist2(candidate[1], check[1]) < 8:
                flag = True
                break
        if not(flag):
            lst.append(candidate)

    # merge close horizontal segments -> sort horizontally
    sortH = sorted(lst, key = lambda x: x[1][1])
    sortH.sort(key = lambda x: x[0][1])
    lst = []
    prev = ((0, 0), (0, 0))
    for l in sortH:
        # if this and prev are horizontal lines and have their endpoints connected
        if l[0][1] == l[1][1] and prev[0][1] == prev[1][1] and dist2(prev[1], l[0]) < 8:
            prev = (prev[0], l[1])
        else:
            if prev != ((0, 0), (0, 0)):
                lst.append(prev)
            prev = l
    lst.append(prev)

    # merge close vertical segments -> sort vertically
    sortV = sorted(lst)
    lst = []
    prev = ((0, 0), (0, 0))
    for l in sortV:
        # if this and prev are vertical lines and have their endpoints connected
        if l[0][0] == l[1][0] and prev[0][0] == prev[1][0] and dist2(prev[1], l[0]) < 8:
            prev = (prev[0], l[1])
        else:
            if prev != ((0, 0), (0, 0)):
                lst.append(prev)
            prev = l
    lst.append(prev)
    return lst

def getTextCoords(coords):
    return (round(coords[0]), 600 - round(coords[1]) - FONT_SIZE)

# get y boundaries for each date in the current page
def calcDateBoundaries(lines):
    # check only horizontal lines
    # also, dates should be in the same column, so check only lines with startpoint.x > firstdate.x
    datelines = [l for l in lines if l[0][1] == l[1][1] and l[0][0] < dates[0]["coords"][0]]
    for i in range(len(dates)):
        y1, y2 = 0, 0
        for j in range(len(datelines)):
            if dates[i]["coords"][1] < datelines[j][0][1]:
                # datelines[j - 1] will always exist since all dates have a line above them
                y1 = datelines[j - 1][0][1]
                y2 = datelines[j][0][1]
                break
        dates[i]["boundaries"] = (y1, y2)

# get date from coordinates
def getDate(coords):
    if not dates:
        return "not assigned"
    for d in dates:
        if d["boundaries"][0] == 0 and d["boundaries"][1] == 0:
            return "ERROR"
        if coords[1] > d["boundaries"][0] and coords[1] < d["boundaries"][1]:
            return d["date"]

with open("db/courses.json") as f:
    coursenames = json.load(f)

with open("pdf-parse/{}".format(SCHEDULE_FILE), "rb") as fp:
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    device = PDFDevice(rsrcmgr)
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    def parse_obj(lt_objs):
        for obj in lt_objs:
            if isinstance(obj, LTTextBoxHorizontal):
                coor = getTextCoords(obj.bbox[0:2])
                text = obj.get_text().replace('\n', ' _')
                textboxes.append((coor, text[:5]))
                # check if content contains a date
                match = re.search(r"\d{2}/\d{2}/\d{4}", text)
                if match:
                    dates.append({"date": match.group(), "coords": coor})
                res = match_keywords(format_text(text))
                if len(res["indexes"]) == 1:
                    courses[res["indexes"][0]] = {"coords": coor}
                    # may append the same course multiple times
                    curr_courses.append(res["indexes"][0])

            if isinstance(obj, LTRect):
                rects.append(getRectCoords(obj.bbox[0:4]))

            if isinstance(obj, LTFigure):
                parse_obj(obj._objs)

    with open("pdf-parse/dump.html", "w", encoding="utf8") as svg:
        ''' SVG HEAD '''
        if CREATE_SVG:
            svg.write("<style type=\"text/css\">svg{stroke:#000;stroke-width:1;fill:none}</style>\n")
        i = 0

        # loop over all pages in the document
        for page in PDFPage.create_pages(document):

            # read the page into a layout object
            interpreter.process_page(page)
            layout = device.get_result()

            ''' CREATE SVG '''
            if CREATE_SVG:
                svg.write("<svg id=\"s{}\" width=\"1200\" height=\"600\">\n".format(i))
            
            rects = []
            textboxes = []
            dates = []
            curr_courses = []

            # extract info from this page
            parse_obj(layout._objs)

            lines = rectsToLines(rects)

            lines = mergeLines(lines)
            lines.sort(key = lambda x: x[1][1])
            lines.sort(key = lambda x: x[0][1])
            if dates:
                calcDateBoundaries(lines)

            ''' DRAW LINES '''
            if CREATE_SVG:
                for l in lines:
                    svg.write("<line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" stroke=\"#{}\"></line>\n".format(l[0][0], l[0][1], l[1][0], l[1][1], randomColor()))
                if SHOW_TEXTBOXES:
                    for t in textboxes:
                        svg.write("<text x=\"{}\" y=\"{}\" font-size=\"4\" font-weight=\"lighter\">{}</text>\n".format(t[0][0], t[0][1], t[1]))
            
            for c in curr_courses:
                courses[c]["date"] = getDate(courses[c]["coords"])

            ''' CLOSE SVG '''
            if CREATE_SVG:
                svg.write('</svg>' + "\n")
            i += 1

    with open("outputs/dates.json", "w", encoding="utf8") as out:
        coursedates = {}
        for key, c in courses.items():
            coursedates[key] = c["date"]
        out.write(json.dumps(coursedates))
        out.close()

