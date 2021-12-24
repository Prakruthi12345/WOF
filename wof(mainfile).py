# Wheel of Fortune

from cmu_112_graphics import *  # cmu_112_graphics taken from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
from widgets import *
from bic import *
from csg import *
from tkinter import *
import random
import string
import math

class GameBoard(Board):
    # assume answerStr has been scrubbed. No duplicate spaces. Only
    # letters, space and specific punctuations (hyphen, comma, apostrophe,
    # ampersand, question mark, period and exclamation)
    def __init__(self, app, placement, answerStr):
        self.lettersPerRow = 10
        self.maxRows = 4
        maxLen = self.maxRows * self.lettersPerRow
        strLen = len(answerStr)
        # answerStr containing only letters
        self.answerStr = ""
        if (strLen < maxLen):
            newStr = answerStr.upper() + ("*" * (maxLen - strLen))
        else:
            newStr = answerStr.upper()
        self.letterCounts = dict()
        for ch in newStr:
            if (ch.isalpha() == True):
                if (ch in self.letterCounts):
                    self.letterCounts[ch] = self.letterCounts[ch] + 1
                else:
                    self.letterCounts[ch] =  1
            if (ch != '*'):
               self.answerStr = self.answerStr + ch
        self.answerStr = self.answerStr.upper()
        super(GameBoard, self).__init__(
                app, placement, self.maxRows,
                self.lettersPerRow, newStr, hide = True)
        self.unHideStr("&'.?-!,")

    def removeLetter(self, ch):
        if (ch in self.letterCounts):
            self.letterCounts[ch] = 0

    def isPuzzleSolved(self):
        for ch in self.letterCounts:
            if (self.letterCounts[ch] != 0):
                return False
        return True

    def doesAnswerMatch(self, text):
        textStr = text.upper()
        textStr = textStr.strip()
        if (self.answerStr == textStr):
            return True
        return False

class KeyBoard(Board):
    def __init__(self, app, placement, hide = False):
        self.lettersPerRow = 10
        self.maxRows = 3
        self.app = app
        self.fillColor = "blue",
        self.txtColor = "black",
        keyStr = "QWERTYUIOPASDFGHJKL**ZXCVBNM**"
        super(KeyBoard, self).__init__(
                app, placement, self.maxRows,
                self.lettersPerRow, keyStr, fillColor = self.fillColor,
                txtColor = self.txtColor, hide = hide)

class Wheel:
    def __init__(self, placement, wedgeInfo, wedgeTextAngles):
        assert(len(wedgeInfo) == len(wedgeTextAngles))
        self.wedgeInfo = wedgeInfo
        self.wedgeTextAngles = wedgeTextAngles
        self.placeWheel(placement)
        self.largeFont = "Arial 16 bold"
        self.mediumFont = "Arial 9 bold"
        self.smallFont = "Arial 8 bold"
        self.tinyFont = "Arial 4 bold"
        self.firstWedgeIndex = 0

    def updateWedges(self, wedgeInfo):
        self.wedgeInfo = wedgeInfo

    def spinWheel(self):
        self.firstWedgeIndex = random.randrange(len(self.wedgeInfo))

    def getFirstWedgeValue(self):
        return (self.wedgeInfo[self.firstWedgeIndex])[0]

    def placeWheel(self, placement):
        (x, y, r) = placement
        self.wheelCenter = (x, y)
        self.wheelRadius = r

    def drawWheel(self, canvas):
        arcAngle = 360/len(self.wedgeInfo)

        # start at the wedge that we stopped after the spin
        wedge = self.firstWedgeIndex
        coord = self.wheelCenter[0] - self.wheelRadius, \
                self.wheelCenter[1] - self.wheelRadius, \
                self.wheelCenter[0] + self.wheelRadius, \
                self.wheelCenter[1] + self.wheelRadius,
        for i in range(len(self.wedgeInfo)) :
            # draw the wedge
            if (i == 0):
                canvas.create_arc(coord, start = i * arcAngle,
                    extent = arcAngle,
                    fill = self.wedgeAttributes[wedge][2],
                    outline = "orange", width = 5)
            else:
                canvas.create_arc(coord, start = i * arcAngle,
                    extent = arcAngle,
                    fill = self.wedgeAttributes[wedge][2])

            # anchor text at the mid point the arc
            midAngle = (i + 0.5) * arcAngle
            x = self.wheelCenter[0] + \
                (self.wheelRadius * math.cos(midAngle/(180/(22/7))))
            y = self.wheelCenter[1] - \
                (self.wheelRadius * math.sin(midAngle/(180/(22/7))))

            # letters of  text should line up vertically.
            # https://stackoverflow.com/questions/17554960/vertical-text-in-tkinter-canvas
            wedgeText = "\n".join(self.wedgeAttributes[wedge][1])

            if (self.wheelRadius < 25):
                textFont = self.tinyFont
            elif (self.wheelRadius < 50 or (len(wedgeText) > 10)):
                textFont = self.smallFont
            elif (self.wheelRadius < 100 or (len(wedgeText) > 10)):
                textFont = self.mediumFont
            else:
                textFont = self.largeFont

            # text angles are dependent on the arc angle. It is independent
            # of the order in which the wedges are displayed
            canvas.create_text(x, y,
                text = wedgeText,
                fill = 'black',
                font = textFont,
                angle = self.wedgeTextAngles[i],
                anchor = NE)
            wedge += 1
            if (wedge >= len(self.wedgeInfo)):
                wedge = 0

class WheelRound(Wheel):

    def __init__(self, placement, wedgeValues):
        self. wedgeTextAngles = [-70, -40, -10, 20, 50, 80, 110,
                                 140, 170, 200, 230, 260]

        self.wedgeAttributes = []
        self.wedgeValues = wedgeValues
        assert(len(wedgeValues) == len(self.wedgeTextAngles))
        for i in range(len(wedgeValues)):
            if (wedgeValues[i] < 0):
                font = "Courier 8 bold"
                if (wedgeValues[i] == -1):
                    txt = "LOSE TURN"
                    color = "red"
                elif (wedgeValues[i] == -2):
                    txt = "BANKRUPT"
                    color = "red"
                elif (wedgeValues[i] == -3):
                    txt = "FREE PLAY"
                    color = "yellow"
                elif (wedgeValues[i] == -4):
                    txt = "GRANDPRIZE"
                    color = "purple"
                else:
                    assert(0)
            else:
                txt = "$" + str(wedgeValues[i])
                color = "green"
                font = "Arial 16 bold"
            self.wedgeAttributes.append((wedgeValues[i], txt, color, font))

        super(WheelRound, self).__init__(
                placement, self.wedgeAttributes, self.wedgeTextAngles)

    def replaceGrandPrizeWedge(self, value):
        assert(value > 0)
        for i in range(len(self.wedgeAttributes)):
            if (self.wedgeAttributes[i][0] == -4):
                txt = "$" + str(value)
                color = "green"
                font = "Arial 16 bold"
                self.wedgeAttributes[i] = (value, txt, color, font)
                self.updateWedges(self.wedgeAttributes)
                break

class Player:
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.cashWon = 0
        self.totalCashWon = 0
        self.grandPrize = False
        self.lostTurn = False
        self.roundsWon = 0

    def getName(self):
        return self.name

    def wonRound(self, minCash):
        if (self.cashWon < minCash):
            self.totalCashWon += minCash
        else:
            self.totalCashWon += self.cashWon
        self.cashWon = 0
        self.lostTurn = False
        self.roundsWon += 1

    def newRound(self):
        self.cashWon = 0
        self.lostTurn = False

    def loseTurn(self):
        self.lostTurn = True

    def unLoseTurn(self):
        self.lostTurn = False

    def canPlay(self):
        return (self.lostTurn == False)

    def bankrupt(self):
        self.cashWon = 0
        self.grandPrize = False

    def grandPrizeChance(self):
        self.grandPrize = True

    def hasGrandPrizeWedge(self):
        return (self.grandPrize == True)

    def addValue(self, value):
        self.cashWon += value

    def getPlayerInfo(self):
        return (self.totalCashWon, self.cashWon, self.roundsWon,
                self.grandPrize)

def getClues(fileName, numClues, maxCatLen, maxAnswerLen, specialChars): #taken from https://www.wheeloffortunecheats.com/classicmovie/
    f = open(fileName)
    catClues = dict()
    catFound = False
    catStr = None
    while True:
        line = f.readline()
        if (not line):
            break
        if (line.startswith("CATEGORY:")):
            catStr = line[9:]
            # strip leading and trailing whitespace
            catStr = catStr.strip()
            if (len(catStr) > maxCatLen):
                catFound = False
                continue
            catClues[catStr] = []
            catFound = True
            continue
        if (catFound == False):
            continue

        # strip leading and trailing whitespace
        clueStr = line.strip()
        newStr = ""
        space = False
        bad = False

        # eliminate duplicate spaces
        # make sure only specific non-alpha characters are allowed
        for ch in clueStr:
            if (ch.isalpha()):
                newStr += ch
                space = False
            elif (ch == ' '):
                if (space == True):
                    continue
                newStr += ch
                space = True
            elif (ch in specialChars):
                newStr += ch
                space = False
            else:
                bad = True
                break

        if ((bad == False) and (len(newStr) <= maxAnswerLen) and
            (len(newStr) > 0)) :
            catClues[catStr].append(newStr)

    f.close()

    i = 0
    clueList = []
    while (i < numClues):
        j = random.randrange(len(catClues))
        k = 0
        for cat in catClues:
            if (j == k):
                break
            k += 1
        j = random.randrange(len(catClues[cat]))
        clueList.append((cat, catClues[cat][j]))
        i += 1

    return (clueList)

class WoFMainGameMode(Mode):
    def appStarted(mode):
        mode.app.margin = 20
        mode.app.prevMode = None

        mode.gameOver = False

        # don't allow window to be resizable.
        # display becomes jumbled/unreadable at lower sizes
        mode.app.getRoot().resizable(0, 0)

        mode.numMinis = 2
        mode.launchMiniGame = False
        mode.switchMode = False

        mode.vowelPurchase = False
        mode.vowelCost = 250
        mode.vowelsRemaining = set(['A', 'E', 'I', 'O', 'U'])
        mode.noMoreVowelsLeft = False

        mode.numRounds = 3
        mode.roundPrizes = [
            [-4, 500, -2, 600, 700, 800, -3, 250, -1, 1000, 900, 250],
            [-4, 750, -2, 500, 650, 250, -3, 250, -1, 2000, 1000, 850],
            [-4, 800, -2, 700, 500, 900, -3, 250, -1, 3000, 950, 250]
            ]
        mode.delayBetweenRounds = 5 # seconds
        mode.nextRoundCountDown = 0

        mode.freePlay = False
        mode.freePlayValue = 500

        # min cash given to the winner of a round
        mode.minWinnerCash = 1000

        mode.grandPrizeValue = 10000
        mode.grandPrizeBasicValue = 1000
        mode.grandPrizeWedgePicked = False

        mode.spinTheWheel = False
        mode.spinAmount = 0
        mode.stdTimerDelay = mode.timerDelay
        mode.spinTimerIndex = 0
        mode.spinTimerValues = \
                [20, 20, 20, 20, 20, 50, 50, 50, 50, 100, 100, 100, 200, 200]

        mode.numPlayers = 3

        mode.hideNonCanvasWidgets = False

        clueList = getClues("clues.txt", mode.numRounds, 15, 40, "&'.?-!,")
        if ((clueList == None) or (len(clueList) != mode.numRounds)):
            print(f'Could not get required number ({mode.numRounds}) of clues')
            quit()

        # XXX: For debugging
        print (clueList)

        placementList = mode.computeBoardPlacement()

        mode.gameBoards = []
        mode.catBoards = []
        mode.inPlayBoards = []
        for i in range(mode.numRounds):
            mode.gameBoards.append(GameBoard(mode.app, placementList[0],
                                            clueList[i][1]))
            mode.catBoards.append(CaptionBoard(mode.app, placementList[1],
                                            clueList[i][0]))

            mode.inPlayBoards.append(KeyBoard(mode.app, placementList[2]))

        mode.inPlayTitleBoard = CaptionBoard(mode.app, placementList[3],
                                      "Available Letters")

        mode.vowelButton = MyButton(mode.app, "Buy A Vowel", mode.buyAVowel)
        mode.vowelButton.disable()

        mode.spinButton = MyButton(mode.app, "Spin", mode.spinWheel)

        mode.solveButton = MyButton(mode.app, "Solve", mode.solve,
                                    input = True)

        mode.wheelRound = []
        for i in range(mode.numRounds):
            mode.wheelRound.append(WheelRound(placementList[7],
                                            mode.roundPrizes[i]))

        mode.announce = CaptionBoard(mode.app, placementList[9],
                                      "We will resume after a brief break",
                                      fillColor = "orange")
        mode.currentRound = 0
        mode.currentWheel = mode.wheelRound[0]
        
        # keep track of current boards instead of having to index everywhere
        mode.gameBoard = mode.gameBoards[0]
        mode.catBoard = mode.catBoards[0]
        mode.inPlayBoard = mode.inPlayBoards[0]

        mode.players = []
        for i in range(mode.numPlayers):
            mode.players.append(Player(mode.app, "Player-" + str(i + 1)))
        mode.currentPlayer = mode.players[0]
        mode.currentPlayerIndex = 0

        mode.prompts = MyMessage(mode.app, f'Let\'s Play!!!')

        mode.gameTitleBoard = CaptionBoard(mode.app, placementList[10],
                                      "Wheel of Fortune")

        mode.roundInfo = MyMessage(mode.app,
                f'Round: 1, {mode.currentPlayer.getName()}')
        mode.playerScores = []
        for i in range(mode.numPlayers):
            pStr = mode.formatPlayerInfo(mode.players[i])
            mode.playerScores.append(MyMessage(mode.app, pStr))

    def modeActivated(mode):
        if (mode.launchMiniGame == True):
            mode.launchMiniGame = False
            mode.switchMode = False
            mode.hideNonCanvasWidgets = False
            mode.app.prevMode = None
            if (mode.app.miniWon == False):
                mode.prompts.displayMessage(
                  f'You didn\'t win minigame and are bankrupt. Move on to next player')
                mode.currentPlayer.bankrupt()
                mode.switchPlayer()
            else:
                mode.prompts.displayMessage(
                  f'You won the minigame and avoided bankruptcy. Pick/Buy/Solve?')

    def buyAVowel(mode):
        if (mode.launchMiniGame == True):
            return

        # allow only if player has enough cash
        if (mode.currentPlayer.cashWon < mode.vowelCost):
            mode.prompts.displayMessage(
                 f'You need at least ${mode.vowelCost} to buy a vowel. Pick/Solve?')
            return
        mode.vowelPurchase = True

        # disable all buttons
        mode.vowelButton.disable()
        mode.spinButton.disable()
        mode.solveButton.disable()

    def spinWheel(mode):
        if (mode.launchMiniGame == True):
            return
        mode.spinTheWheel = True
        mode.currentWheel.spinWheel()

        # disable all buttons
        mode.vowelButton.disable()
        mode.spinButton.disable()
        mode.solveButton.disable()

    def solve(mode):
        if (mode.launchMiniGame == True):
            return
        inputStr = mode.solveButton.getInput()
        if (mode.gameBoard.doesAnswerMatch(inputStr) == False):
            if (mode.freePlay == True):
                mode.prompts.displayMessage(
                        f'Incorrect Answer. Spin/Buy/Solve?')
                mode.freePlay = False
                mode.spinButton.enable()
            else:
                mode.prompts.displayMessage(
                        f'Incorrect Answer. Next player please')
                mode.switchPlayer()
            return
        mode.freePlay = False
        mode.puzzleSolved()

    def computeBoardPlacement(mode):
        L = []

        # 0: puzzle board
        (x, y, w, h) = (0, 0, mode.app.width/3, mode.app.height/4)
        L.append((x, y, w, h))

        # 1: caption
        (x, y, w, h) = (0, y + h + 20, mode.app.width/3, 30)
        L.append((x, y, w, h))

        # 2: 2: letters in play
        (x, y, w, h) = (0, y + h + 50, mode.app.width/3, mode.app.height/4)
        inPlay = (x, y, w, h)
        L.append((x, y, w, h))

        # 3: caption
        (x, y, w, h) = (0, y + h + 20, mode.app.width/3, 30)
        L.append((x, y, w, h))
        
        # 4: vowel button
        (x, y, w, h) = (0, y + h + 20, mode.app.width/12, mode.app.height/20)
        L.append((x, y, w, h))

        # 5: spin button
        (x, y, w, h) = (x + mode.app.width/5, y, mode.app.width/12,
                        mode.app.height/20)
        L.append((x, y, w, h))

        # 6: solve button
        (x, y, w, h) = (x + mode.app.margin, y + 50, mode.app.width/12,
                        mode.app.height/20)
        L.append((x, y, w, h))

        # 7: wheel
        (x, y, w, h) = inPlay
        (x, y, r) = (x + w + 70 + mode.app.width/3, y + h/2 + 40,
                     mode.app.width/6)
        L.append((x, y, r))

        # 8: prompts
        (x, y, w, h) = L[3]
        (x, y, w, h) = (x + w + 50, L[7][1] + r + 20, 0, 0)
        L.append((x, y, w, h))

        # 9: announce
        (x, y, w, h) = (mode.app.width/4, mode.app.height/2,
                        mode.app.width/2, 30)
        L.append((x, y, w, h))

        # 10: Game Title
        (x, y, w, h) = (L[0][2] + 80, 0,
                        mode.app.width/4, 30)
        L.append((x, y, w, h))

        # 11: Round Info
        (x, y, w, h) =  (x - 60, y + 50, 0, 0)
        L.append((x, y, w, h))

        # 12,13,14: Player Info. Assumes 3 players
        (x, y, w, h) =  (x, y + 30, 0, 0)
        L.append((x, y, w, h))

        (x, y, w, h) =  (x, y + 30, 0, 0)
        L.append((x, y, w, h))

        (x, y, w, h) =  (x, y + 30, 0, 0)
        L.append((x, y, w, h))

        return (L)

    def placeBoards(mode):
        L = mode.computeBoardPlacement()
        mode.gameBoard.placeBoard(L[0])
        mode.catBoard.placeBoard(L[1])
        mode.inPlayBoard.placeBoard(L[2])
        mode.inPlayTitleBoard.placeBoard(L[3])
        mode.vowelButton.placeButton(L[4])
        mode.spinButton.placeButton(L[5])
        mode.solveButton.placeButton(L[6])
        mode.currentWheel.placeWheel(L[7])
        mode.prompts.placeMessage(L[8])
        mode.announce.placeBoard(L[9])
        mode.gameTitleBoard.placeBoard(L[10])
        mode.roundInfo.placeMessage(L[11])

        for i in range(mode.numPlayers):
            mode.playerScores[i].placeMessage(L[12 + i])

    def keyPressed(mode, event):
        if (mode.gameOver == True):
            quit()

    def mousePressed(mode, event):
        if (mode.nextRoundCountDown != 0):
            return

        if (mode.gameOver == True):
            return

        if (mode.spinTheWheel == True):
            return

        # ignore if vowel is picked and vowel not being bought
        # 
        ch = mode.inPlayBoard.letterPicked(event.x, event.y)
        if (ch == None):
            return
        if (ch in "AEIOU"):
            if (mode.vowelPurchase == False):
                mode.prompts.displayMessage(
                        f'Vowels can be chosen only after purchase')
                return
        elif (mode.vowelPurchase == True):
            mode.prompts.displayMessage(
                        f'Only vowels can be chosen only after purchase')
            return
        elif (mode.spinAmount == 0):
            mode.prompts.displayMessage(
                        f'Spin before picking')
            return
        mode.inPlayBoard.hideStr(ch)
        numCh = mode.gameBoard.numOccurences(ch)
        if (numCh != 0):
            # if freePlay add to score
            # if vowel decrement vowelCost unless freeplay
            # if consonant add to score
            if (numCh == 1):
                mode.prompts.displayMessage(f'Yes, there is one {ch}')
            else:
                mode.prompts.displayMessage(f'Yes, there are {numCh} {ch}\'s')
            mode.gameBoard.removeLetter(ch)
            mode.gameBoard.unHideStr(ch)
            if (mode.vowelPurchase == True):
                mode.currentPlayer.addValue(-mode.vowelCost)
            else:
                mode.currentPlayer.addValue(numCh * mode.spinAmount)
            pStr = mode.formatPlayerInfo(mode.currentPlayer)
            mode.playerScores[mode.currentPlayerIndex].displayMessage(pStr)
        else:
            if (mode.freePlay == True):
                mode.prompts.displayMessage(
                        f'There is no {ch}. Spin/Buy/Solve?')
            else:
                 mode.prompts.displayMessage(
                        f'There is no {ch}. Next player please')
                 mode.switchPlayer()

        if (mode.vowelPurchase == True):
            mode.vowelPurchase = False
            mode.vowelsRemaining.remove(ch)
            if (len(mode.vowelsRemaining) == 0):
                # no more vowels
                mode.vowelButton.disable()
                mode.noMoreVowelsLeft = True
            else:
                mode.vowelButton.enable()
        elif (mode.noMoreVowelsLeft == False):
             mode.vowelButton.enable()

        if (mode.gameBoard.isPuzzleSolved() == True):
            mode.puzzleSolved()
        else:
            mode.spinButton.enable()
            mode.solveButton.enable()

        mode.freePlay = False
        mode.spinAmount = 0
        return

    def startMiniGame(mode):
        mode.app.prevMode = mode
        mode.app.miniWon = False
        mini = random.randrange(mode.numMinis)
        if (mini == 0):
            mode.app.setActiveMode(BICGameMode())
        elif (mini == 1):
            mode.app.setActiveMode(CSGameMode())
        else:
            assert(0)

    def timerFired(mode):
        if (mode.switchMode == True):
            print ("switching")
            mode.startMiniGame()
            return

        if (mode.nextRoundCountDown != 0):
            mode.nextRoundCountDown -= 1
            if (mode.nextRoundCountDown == 0):
                mode.playNextRound()
            return

        if (mode.spinTheWheel == True):
            if (mode.spinTimerIndex < len(mode.spinTimerValues)):
                mode.timerDelay = mode.spinTimerValues[mode.spinTimerIndex]
                mode.spinTimerIndex += 1
                mode.currentWheel.spinWheel()
            else:
                mode.spinTimerIndex = 0
                mode.spinTheWheel = False
                mode.timerDelay = mode.stdTimerDelay
                mode.applySpinRules()
        return

    def applySpinRules(mode):
        mode.spinAmount = mode.currentWheel.getFirstWedgeValue()
        mode.solveButton.enable()
        if (mode.spinAmount > 0):
            mode.prompts.displayMessage(
                f'You landed on ${mode.spinAmount}. Pick/Solve?')
            return
        if (mode.spinAmount == -1):
            mode.prompts.displayMessage(
                f'You lost your turn. Next player please')
            mode.spinAmount = 0
            mode.currentPlayer.loseTurn()
            mode.switchPlayer()
        elif (mode.spinAmount == -2):
            mode.prompts.displayMessage(
                f'Play minigame to avoid bankruptcy')
            mode.launchMiniGame = True
            mode.spinAmount = 0
        elif (mode.spinAmount == -3):
            mode.prompts.displayMessage(
                f'You get a free play. Pick/Buy/Solve')
            mode.freePlay = True
            mode.spinAmount = mode.freePlayValue
        elif (mode.spinAmount == -4):
            mode.prompts.displayMessage(
                f'You may win the grand prize. Pick/Solve')
            mode.currentWheel.replaceGrandPrizeWedge(
                    mode.grandPrizeBasicValue)
            mode.currentPlayer.grandPrizeChance()
            mode.grandPrizeWedgePicked = True
            mode.spinAmount = mode.grandPrizeBasicValue
        else:
            assert(0)

        if (mode.noMoreVowelsLeft == False):
            mode.vowelButton.enable()
        if (mode.spinAmount == 0):
            mode.spinButton.enable()
        mode.solveButton.enable()

    def puzzleSolved(mode):
        mode.prompts.displayMessage(
                    f'Yes, that\'s the right answer')
        mode.solveButton.txtClear()
        mode.gameBoard.unHideAll()
        mode.currentPlayer.wonRound(mode.minWinnerCash)
        pStr = mode.formatPlayerInfo(mode.currentPlayer)
        mode.playerScores[mode.currentPlayerIndex].displayMessage(pStr)
        mode.vowelButton.disable()
        mode.spinButton.disable()
        mode.solveButton.disable()

        if (mode.currentRound == mode.numRounds -1):
            maxCashWon = 0
            winningPlayers = set()
            gpWinner = None
            gpWinnerIndex = 0
            for i in range(mode.numPlayers):
                (t, c, r, g) = mode.players[i].getPlayerInfo()
                if (t != 0 and t >= maxCashWon):
                    maxCashWon = t
                    winningPlayers.add(mode.players[i])
                    if (g == True):
                        gpWinner = mode.players[i]
                        gpWinnerIndex = i
            if (len(winningPlayers) == 0):
                mode.announce.changeText("No winner!!!")
            else:
                if (len(winningPlayers) == 1):
                    if (gpWinner != None):
                        (t, c, r, g) = gpWinner.getPlayerInfo()
                        gpWinner.addValue(mode.grandPrizeValue)
                        pStr = mode.formatPlayerInfo(gpWinner)
                        mode.playerScores[gpWinnerIndex].displayMessage(pStr)
                    winningPlayer = winningPlayers.pop()
                    mode.announce.changeText(
                         f'Winner is {winningPlayer.getName()}. Press any key to quit')
                else:
                    pStr = "Joint winners are "
                    for winners in winningPlayers:
                        pStr += winners.getName() + " "
                    pStr += "\nPress any key to quit"
                    mode.announce.changeText(pStr)
            mode.gameOver = True
        else:
            mode.startNextRoundCountDown()

    def startNextRoundCountDown(mode):
        mode.nextRoundCountDown = \
            (mode.delayBetweenRounds * 1000) // mode.stdTimerDelay

    def playNextRound(mode):

        for i in range(mode.numPlayers):
            mode.players[i].newRound()
            pStr = mode.formatPlayerInfo(mode.players[i])
            mode.playerScores[i].displayMessage(pStr)

        i = mode.currentRound + 1
        mode.currentRound = i
        mode.currentWheel = mode.wheelRound[i]
        mode.gameBoard = mode.gameBoards[i]
        mode.catBoard = mode.catBoards[i]
        mode.inPlayBoard = mode.inPlayBoards[i]
        mode.roundInfo.displayMessage(
                f'Round: {i + 1}   Player: {mode.currentPlayerIndex + 1}')

        # Grand Prize wedge can be won only once per game
        if (mode.grandPrizeWedgePicked == True):
            mode.currentWheel.replaceGrandPrizeWedge(
                    mode.grandPrizeBasicValue)

        mode.switchPlayer()
        mode.prompts.displayMessage(f'Let\'s Play!!!')

    def formatPlayerInfo(mode, player):
        (t, c, r, g) = player.getPlayerInfo()
        pStr = "[" + player.getName() + ":" + " Total: $" + str(t) + \
               " Current: $" + str(c) + " Rounds Won: " + str(r)
        if (g == True):
            pStr += " GP Eligible]"
        else:
            pStr += "]"
        return pStr

    def switchPlayer(mode):
        pStr = mode.formatPlayerInfo(mode.currentPlayer)
        mode.playerScores[mode.currentPlayerIndex].displayMessage(pStr)
        i = mode.currentPlayerIndex + 1
        while (i != mode.currentPlayerIndex):
            if (i >= mode.numPlayers):
                i = 0
            if (mode.players[i].canPlay() == True):
                break
            mode.players[i].unLoseTurn()
            i += 1
        if (i == mode.currentPlayerIndex):
            # no eligible player. Simply choose next player
            i = (i + 1) % mode.numPlayers
            mode.players[i].unLoseTurn()
        mode.currentPlayerIndex = i
        mode.currentPlayer = mode.players[i]
        mode.vowelButton.enable()
        mode.spinButton.enable()
        mode.solveButton.enable()
        mode.roundInfo.displayMessage(
                f'Round: {mode.currentRound + 1},      {mode.currentPlayer.getName()}')
        return

    def redrawAll(mode, canvas):
        if (mode.launchMiniGame == True):
            mode.hideNonCanvasWidgets = True
        mode.placeBoards()
        mode.gameBoard.drawBoard(canvas)
        mode.catBoard.drawBoard(canvas)
        mode.inPlayBoard.drawBoard(canvas)
        mode.inPlayTitleBoard.drawBoard(canvas)
        mode.currentWheel.drawWheel(canvas)
        mode.vowelButton.drawButton(canvas, mode.hideNonCanvasWidgets)
        mode.spinButton.drawButton(canvas, mode.hideNonCanvasWidgets)
        mode.solveButton.drawButton(canvas, mode.hideNonCanvasWidgets)
        mode.prompts.drawMessage(canvas, mode.hideNonCanvasWidgets)
        mode.gameTitleBoard.drawBoard(canvas)
        mode.roundInfo.drawMessage(canvas, mode.hideNonCanvasWidgets)

        for i in range(mode.numPlayers):
            mode.playerScores[i].drawMessage(canvas,
                    mode.hideNonCanvasWidgets)

        if (mode.nextRoundCountDown != 0 or mode.gameOver == True):
            mode.announce.drawBoard(canvas)

        if (mode.launchMiniGame == True):
            mode.switchMode = True

class WoFSplashScreenMode(Mode):
    def redrawAll(mode, canvas):
        font = 'Arial 13 bold'
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "yellow")
        textStr = f'''
        The game consists of 3 rounds of puzzle solving involving 3 players
        The objective of the game is to solve the puzzle and win cash

        The category of the puzzle will give a clue to the likely answer
        The answer will consists only of letters A-Z. Any punctuation marks
        will be revealed in the puzzle board
        A virtual keyboard will be provided to select one letter at
        a time. The selection can be made using the mouse

        Cash can be won by spinning the wheel and correctly guessing
        a letter in the puzzle. The amount of cash won depends on the number
        of occurences of the letter and the dollar amount displayed in the
        wedge. If the guess is incorrect the turn passes on to the next player.

        The wheel consists fo 12 wedges. Most of the wedges have a $ amount.
        There are 4 special wedges - "Free Play", "Bankrupt", "Lose a Turn"
        and "Grand Prize"

        Free Play: Player is not penalized for an incorrect guess
        Bankrupt: Player loses all cash earned in the round and the grand prize
        However, bankruptcy can be avoided if the player wins the minigame
        that gets launched automatically
        Lose a Turn: Player will lose a subsequent turn
        Grand Prize: Available only once per game. A player landing on this
        wedge is eligible if, at the end of the game, that player has the most
        cash and has never been bankrupt in any round

        The wheel can be spun by hitting the Spin button.
        The first wedge highlighted in orange after the wheel stops will be
        the chosen wedge

        A vowel can be picked only by purchasing using the "Buy A Vowel" button
        The price is $250 irrespective of the number of occurences of the vowel

        If player knows the answer it can be input using normal keyboard into
        the text box alongside the Solve button and clicking the button
        Press any key to start the game'''
        canvas.create_text(mode.width/2, mode.height/2, text=textStr,
                           font = font)

    def keyPressed(mode, event):
        mode.app.setActiveMode(mode.app.mainGameMode)

class WheelOfFortune(ModalApp):
    def appStarted(app):
        app.splashScreenMode = WoFSplashScreenMode()
        app.mainGameMode = WoFMainGameMode()
        app.setActiveMode(app.splashScreenMode)

WheelOfFortune(width=900, height=600)
