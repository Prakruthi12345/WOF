from cmu_112_graphics import *
from tkinter import *
import random
import string
import math

def pointInGrid(width, height, margin, x, y):
    # return True if (x, y) is inside the grid defined by app.
    return ((margin <= x <= width-margin) and
            (margin <= y <= height-margin))

def getCell(width, height, margin, rows, cols, x, y):
    # aka "viewToModel"
    # return (row, col) in which (x, y) occurred or (-1, -1) if outside grid.
    if (not pointInGrid(width, height, margin, x, y)):
        return (-1, -1)
    gridWidth  = width - 2*margin
    gridHeight = height - 2*margin
    cellWidth  = gridWidth / cols
    cellHeight = gridHeight / rows

    # Note: we have to use int() here and not just // because
    # row and col cannot be floats and if any of x, y, app.margin,
    # cellWidth or cellHeight are floats, // would still produce floats.
    row = int((y - margin) / cellHeight)
    col = int((x - margin) / cellWidth)

    if ((row >= rows) or (col >= cols)):
        return (-1, -1)

    return (row, col)

def getCellBounds(width, height, margin, rows, cols, row, col):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = width - 2*margin
    gridHeight = height - 2*margin
    columnWidth = gridWidth / cols
    rowHeight = gridHeight / rows
    x0 = margin + col * columnWidth
    x1 = margin + (col+1) * columnWidth
    y0 = margin + row * rowHeight
    y1 = margin + (row+1) * rowHeight
    return (x0, y0, x1, y1)

def getTextCenter(width, height, margin, rows, cols, row, col):
    # aka "modelToView"
    # returns (x0, y0, x1, y1) corners/bounding box of given cell in grid
    gridWidth  = width - 2*margin
    gridHeight = height - 2*margin
    columnWidth = gridWidth / cols
    rowHeight = gridHeight / rows
    x0 = margin + col * columnWidth + columnWidth/2
    y0 = margin + row * rowHeight + rowHeight/2
    return (x0, y0)

class Board:
    def __init__(self, app, placement, nRows, nCols, text,
                 fillColor = "green",
                 txtColor = "black",
                 hide = True):
        assert(nRows * nCols == len(text))
        self.app = app
        self.placeBoard(placement)
        self.bgColor = "grey"
        self.fillColor = fillColor
        self.txtColor = txtColor
        self.largeFont = "Arial 24 bold"
        self.mediumFont = "Arial 12 bold"
        self.smallFont = "Arial 8 bold"
        self.nRows = nRows
        self.nCols = nCols
        self.text = text
        board = [[('*', hide) for j in range(nCols)] for i in range(nRows)]
        for i in range(nRows) :
            for j in range(nCols) :
                board[i][j] = (text[(i * nCols) + j], board[i][j][1])
        self.board = board

    def placeBoard(self, placement):
        (x, y, width, height) = placement
        self.margin = 0
        self.coord = (x + self.app.margin, y + self.app.margin)
        self.width = width
        self.height = height

    def numOccurences(self, ch):
        return self.text.count(ch)

    def getBoardCellBounds(self, row, col):
        (x0, y0, x1, y1) = getCellBounds(self.width, self.height, self.margin,
                             self.nRows, self.nCols, row, col)
        return ((x0 + self.coord[0], y0 + self.coord[1],
                 x1 + self.coord[0], y1 + self.coord[1]))

    def getBoardTextCenter(self, row, col):
        (x0, y0) =  getTextCenter(self.width, self.height, self.margin,
                             self.nRows, self.nCols, row, col)
        return ((x0 + self.coord[0], y0 + self.coord[1]))

    def hideStr(self, str):
        for row in range(self.nRows):
            for col in range(self.nCols):
                if (self.board[row][col][0] in str):
                    self.board[row][col] = (self.board[row][col][0], True)

    def unHideStr(self, str):
        for row in range(self.nRows):
            for col in range(self.nCols):
                if (self.board[row][col][0] in str):
                    self.board[row][col] = (self.board[row][col][0], False)

    def hideAll(self):
        for row in range(self.nRows):
            for col in range(self.nCols):
                self.board[row][col] = (self.board[row][col][0], True)

    def unHideAll(self):
        for row in range(self.nRows):
            for col in range(self.nCols):
                if (self.board[row][col][0] != '*'):
                    self.board[row][col] = (self.board[row][col][0], False)

    def drawBoard(self, canvas):
        if (self.width < 100 or self.height < 100):
            font = self.smallFont
        elif (self.width < 300 or self.height < 300):
            font = self.mediumFont
        else:
            font = self.largeFont
        for row in range(self.nRows):
            for col in range(self.nCols):
                (x0, y0, x1, y1) = self.getBoardCellBounds(row, col)
                if (self.board[row][col][0] == '*'):
                    canvas.create_rectangle(x0, y0, x1, y1, fill=self.bgColor)
                else:
                    canvas.create_rectangle(x0, y0, x1, y1, fill=self.fillColor)
                    if (self.board[row][col][1] == False):
                        (x0, y0) = self.getBoardTextCenter(row, col)
                        canvas.create_text(x0, y0, fill=self.txtColor,
                                text=self.board[row][col][0],
                                font=font)
        return None

    def letterPicked(self, x, y):
        x0 = x - self.coord[0]
        y0 = y - self.coord[1]
        (row, col) = getCell(self.width, self.height, self.margin,
                             self.nRows, self.nCols, x0, y0)
        ch = self.board[row][col][0]
        if (ch != '*'):
            return (ch)
        return None

class CaptionBoard:
    def __init__(self, app, placement, capStr,
            fillColor = "green", txtColor = "black"):
        self.app = app
        self.placeBoard(placement)
        self.fillColor = fillColor
        self.txtColor = txtColor
        self.largeFont = "Arial 24 bold"
        self.mediumFont = "Arial 12 bold"
        self.smallFont = "Arial 8 bold"
        self.tinyFont = "Arial 4 bold"
        self.capStr = capStr

    def changeText(self, capStr):
        self.capStr = capStr

    def placeBoard(self, placement):
        (x, y, width, height) = placement
        self.coord = (x + self.app.margin, y + self.app.margin)
        self.width = width
        self.height = height

    def drawBoard(self, canvas):
        if (self.width < 100 or self.height < 10):
            font = self.tinyFont
        elif (self.width < 200 or self.height < 20):
            font = self.smallFont
        elif (self.width < 300 or self.height < 40):
            font = self.mediumFont
        else:
            font = self.largeFont
        (x0, y0) = self.coord
        x1 = x0 + self.width
        y1 = y0 + self.height
        canvas.create_rectangle(x0, y0, x1, y1, fill=self.fillColor)
        x0 = x0 + self.width/2
        y0 = y0 + self.height/2
        canvas.create_text(x0, y0, fill=self.txtColor,
                            text=self.capStr,
                            font=font)

class MyButton:
    def __init__(self, app, buttonText, buttonCmd, input = False):
        self.app = app
        self.buttonText = buttonText
        self.textColor = "orange"
        self.largeFont = "Arial 16 bold"
        self.mediumFont = "Arial 12 bold"
        self.smallFont = "Arial 8 bold"
        self.buttonCmd = buttonCmd
        self.button = None
        self.entry = None
        self.enabled = True
        self.input = input
        self.txtEntry = None
        self.once = True

    def placeButton(self, placement):
        (x, y, width, height) = placement
        self.coord = (x + self.app.margin, y + self.app.margin)
        self.width = int(width)
        self.height = int(width)

    def drawButton(self, canvas, hide):
        if (self.width < 50 or self.height < 10):
            font = self.smallFont
        elif (self.width < 100 or self.height < 20):
            font = self.mediumFont
        else:
            font = self.largeFont
        if ((self.button != None) and (font != self.currentFont)):
            self.button.destroy()
            self.button = None
        if (self.button == None):
            self.currentFont = font
            # not passing width/height since for text Button expects
            # width/height in text units and not pixels
            # Button will implicitly size based on font
            self.button = Button(canvas, text=self.buttonText,
                                 command = self.buttonCmd,
                                 bg = self.textColor,
                                 font = font)
            if (self.input == True):
                self.txtEntry = Entry(canvas, fg = self.textColor, font = font,
                                   bd = 10)
        if (hide == True):
            self.button.place_forget()
        else:
            self.button.place(x = self.coord[0], y = self.coord[1])
        if (self.txtEntry != None):
            if (hide == True):
                self.txtEntry.place_forget()
            else:
                self.txtEntry.place(in_ = self.button, relx=0, anchor = NE,
                             bordermode = 'outside')

    def enable(self):
        self.enabled = True
        if (self.button != None):
            self.button.config(state = NORMAL)
            if (self.txtEntry != None):
                self.txtEntry.config(state = NORMAL)

    def disable(self):
        self.enabled = False
        if (self.button != None):
            self.button.config(state = DISABLED)
            if (self.txtEntry != None):
                self.txtEntry.config(state = DISABLED)

    def getInput(self):
        if (self.txtEntry != None):
            return (self.txtEntry.get())
        return ""

    def txtClear(self):
        if (self.txtEntry != None):
            self.txtEntry.delete(0, END)

class MyMessage:
    def __init__(self, app, msgStr):
        self.app = app
        self.msgStr = StringVar()
        self.label = Label(app.getCanvas(),
                           textvariable = self.msgStr,
                           bg = "yellow", font = "Arial 12 bold")
        self.displayMessage(msgStr)

    def displayMessage(self, msgStr):
        self.msgStr.set(msgStr)

    def placeMessage(self, placement):
        (x, y, width, height) = placement
        self.coord = (x + self.app.margin, y + self.app.margin)

    def drawMessage(self, canvas, hide):
        if (hide == True):
            self.label.place_forget()
        else:
            self.label.place(x = self.coord[0], y = self.coord[1], anchor = W)
        return

class MyClock(object):
    def __init__(self, mode, placement, maxTime):
        self.placement = placement
        self.startTime = datetime.datetime.now()
        self.maxTime = maxTime
        self.timeRemaining = maxTime

    def tick(self):
        elapsed = \
            int((datetime.datetime.now() - self.startTime).total_seconds())
        self.timeRemaining = self.maxTime - int(elapsed)
        if (self.timeRemaining < 0):
            self.timeRemaining = 0

    def remaining(self):
        return (self.timeRemaining)
    
    def draw(self,canvas):
        canvas.create_text(self.placement[0], self.placement[1],
                text = f'{self.timeRemaining}', font="Arial 30 bold")
