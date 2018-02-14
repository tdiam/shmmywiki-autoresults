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
CREATE_SVG = True
SHOW_TEXTBOXES = True
LOG_TEXTS = True

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

# returns a pair containing the sorted horizontal and vertical lines of the grid
def createGrid(lines):
    horizontal = []
    vertical = []
    for l in lines:
        if l[0][1] == l[1][1]:
            horizontal.append(l)
        if l[0][0] == l[1][0]:
            vertical.append(l)
    # sort horizontal lines by y coordinate
    horizontal.sort(key = lambda x: x[0][1])
    # sort vertical lines by x coordinate
    vertical.sort()
    return (horizontal, vertical)

# returns a boolean value that indicates whether the two points A, B are in the same cell
def inSameCell(grid, A, B):
    # if lines do not form a grid, return False
    if len(grid[0]) < 2 or len(grid[1]) < 2:
        return False

    # if points are not in the table, return False
    leftLine, rightLine, topLine, bottomLine = grid[1][0], grid[1][-1], grid[0][0], grid[0][-1]
    if A[0] <= leftLine[0][0] or A[0] >= rightLine[0][0] or A[1] <= topLine[0][1] or A[1] >= bottomLine[0][1]:
        return False
    if B[0] <= leftLine[0][0] or B[0] >= rightLine[0][0] or B[1] <= topLine[0][1] or B[1] >= bottomLine[0][1]:
        return False

    # check horizontal lines
    for h in grid[0]:
        # this condition will catch the first line that will be just below A or B
        # the line is below both A, B iff A, B are in the same cell
        # since if they weren't the check would have already occurred
        # if the line is not below both of them, return False because we already
        # know the two points cannot be in the same cell
        if h[0][1] > A[1] or h[0][1] > B[1]:
            if not(h[0][1] > A[1] and h[0][1] > B[1]):
                return False

    # check vertical lines
    for v in grid[1]:
        if v[0][0] > A[0] or v[0][0] > B[0]:
            if not(v[0][0] > A[0] and v[0][0] > B[0]):
                return False

    # if both checks have succeeded
    return True

# merge texts from textboxes that are in the same cell
# textboxes array is sorted by left-to-right top-to-bottom order
# BUG: this will wrongly merge two different courses that may happen to be examined the same time and date
# temporary workaround uses splitSimultaneousCourses
def mergeTexts(grid, textboxes):
    lst = []
    for t in textboxes:
        # check if this textbox is in the same cell with any previously inserted ones
        appended = False
        for l in lst:
            if inSameCell(grid, t[0], l[0]):
                # maintain text order in merged textboxes so that texts with smaller y-coordinates
                # appear before texts larger y-coordinates
                # if this textbox is above the inserted one, prepend text and change coordinates
                if t[0][1] < l[0][1]:
                    # underscore (_) indicates a new line
                    l[1] = t[1] + " _ " + l[1]
                    l[0] = t[0]
                # else append text and keep coordinates
                else:
                    l[1] += " _ " + t[1]
                appended = True
                break
        if not appended:
            lst.append(t)
    return lst

def splitSimultaneousCourses(textboxes):
    bonus = []
    for t in textboxes:
        # if two instances of "Ηλ." occur in the text, this means that the cell
        # contains more than one course
        if t[1].count("Ηλ.") > 1:
            rows = t[1].split(" _ ")
            lst = [rows[0]]
            for r in rows[1:]:
                # when "Ηλ." occurs, consider next row as a separate course
                if "Ηλ." in lst[-1]:
                    lst.append(r)
                else:
                    lst[-1] += " " + r
            # replace this textbox content with the first part of the splitted courses
            t[1] = lst[0]
            # add rest parts to bonus
            bonus += [[t[0], l, ""] for l in lst[1:]]
        else:
            t[1] = t[1].replace(" _ ", " ")
    # append bonus textboxes and return
    textboxes += bonus
    return textboxes

# get y boundaries for each date in the current page
def calcDateBoundaries(grid):
    # grid[0] gives the horizontal lines sorted by y coordinate
    # dates should be in the same column, so check only lines with startpoint.x > firstdate.x
    datelines = [l for l in grid[0] if l[0][0] < dates[0]["coords"][0]]
    for i in range(len(dates)):
        y1, y2 = 0, 0
        for j in range(len(datelines)):
            # this condition will catch the first line that will be just below the date
            if datelines[j][0][1] > dates[i]["coords"][1]:
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

with open("pdf/{}".format(SCHEDULE_FILE), "rb") as fp:
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
                text = obj.get_text().replace('\n', ' ')
                # check if content contains a date
                match = re.search(r"\d{2}/\d{2}/\d{4}", text)
                if match:
                    dates.append({"date": match.group(), "coords": coor})
                textboxes.append([coor, text, ""])

            if isinstance(obj, LTRect):
                rects.append(getRectCoords(obj.bbox[0:4]))

            if isinstance(obj, LTFigure):
                parse_obj(obj._objs)

    if LOG_TEXTS:
        with open("outputs/pdf_texts.txt", "w", encoding="utf8") as log:
            log.write("")

    with open("outputs/pdf_svg.html", "w", encoding="utf8") as svg:
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

            # extract info from this page
            parse_obj(layout._objs)

            lines = rectsToLines(rects)

            lines = mergeLines(lines)
            lines.sort(key = lambda x: x[1][1])
            lines.sort(key = lambda x: x[0][1])

            grid = createGrid(lines)
            textboxes = mergeTexts(grid, textboxes)
            textboxes = splitSimultaneousCourses(textboxes)

            if dates:
                calcDateBoundaries(grid)

            # keyword matching for each textbox
            for t in textboxes:
                t[1] = " ".join(t[1].split())
                res = match_keywords(format_text(t[1]))
                if len(res["indexes"]) == 1:
                    courses[res["indexes"][0]] = {"coords": t[0], "date": getDate(t[0])}
                    t[2] = " (match: {})".format(res["titles"][0])

            ''' DRAW LINES '''
            if CREATE_SVG:
                for l in lines:
                    svg.write("<line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" stroke=\"#{}\"></line>\n".format(l[0][0], l[0][1], l[1][0], l[1][1], randomColor()))
                if SHOW_TEXTBOXES:
                    for t in textboxes:
                        svg.write("<text x=\"{}\" y=\"{}\" font-size=\"4\" font-weight=\"lighter\">{}</text>\n".format(t[0][0], t[0][1], t[1][:5]))
            if LOG_TEXTS:
                with open("outputs/pdf_texts.txt", "a", encoding="utf8") as log:
                    for t in textboxes:
                        log.write("{}, {}, {}{}\n".format(t[0][0], t[0][1], t[1], t[2]))

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

