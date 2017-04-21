import olpcgames,pygame,logging,traceback,sys,time,random,os
from olpcgames import mesh,textsprite,eventwrap,pausescreen
from olpcgames.util import get_traceback
import pygame, sys
from pygame.locals import *
from pygame.color import THECOLORS

from participantWatcher import *


log = logging.getLogger('JAMultiplos run')
log.setLevel(logging.DEBUG)


TIEMPO_TERRON = .5
TERRONES_POR_LINEA = 5
TIEMPO_ENTRE_TERRONES = .5
DURACION_TERRON = 3
TIEMPO_ULTIMO_TERRON_ANADIDO = 0
PUNTAJE = 0
MULTIPLOS_DE_FACIL = 1
MULTIPLOS_DE_NORMAL = 10
MULTIPLOS_DE_DIFICIL = 20
PUNTAJE_FIN_NIVEL = 20
EN_RED = False
NUEVO_JUEGO = True
DELIMITADOR = "&"
PUNTAJE_TOTAL = 0
OFFSET_X = 0
OFFSET_Y = 0
PORCENTAJE_OPORTUNIDAD_PREGUNTA = .06
ULTIMO_NIVEL_FACIL = 10
ULTIMO_NIVEL_NORMAL = 20
ULTIMO_NIVEL_DIFICIL = 30
TAMANO_FUENTE = 70


TERRON_ = pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + "/JAMultiplos/agujero.PNG")
AGUJERO = pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + "/JAMultiplos/agujero.PNG")
TERRON_WHACKED = pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + "/JAMultiplos/hit.PNG")
TERRON_MISSED = pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + "/JAMultiplos/miss.PNG")
TABLERO = pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + "/JAMultiplos/tablero.PNG")
FONDO = pygame.image.load(os.path.dirname(os.path.realpath(__file__)) + "/JAMultiplos/fondo.PNG")

def checkChangeLevel(screen,users):

    global TIEMPO_ENTRE_TERRONES,DURACION_TERRON,PUNTAJE_TOTAL
    
    amountOfUsers = len(users)
    if not EN_RED:
        amountOfUsers = 1
        
    updateTotalScore(users)

    if PUNTAJE_TOTAL >= PUNTAJE_FIN_NIVEL*amountOfUsers:
        newlevel = MULTIPLOS_DE_FACIL+1
        if newlevel > ULTIMO_NIVEL_FACIL:
            newlevel = 1
            setBonusRoundAttributes()
        
        for x in users:
            x.text = x.text.split("(")[0] + "(0)"

        doChangeLevel(screen,newlevel)

def checkChangeLevelNormal(screen,users):

    global TIEMPO_ENTRE_TERRONES,DURACION_TERRON,PUNTAJE_TOTAL
    
    amountOfUsers = len(users)
    if not EN_RED:
        amountOfUsers = 1
        
    updateTotalScore(users)

    if PUNTAJE_TOTAL >= PUNTAJE_FIN_NIVEL*amountOfUsers:
        newlevel = MULTIPLOS_DE_NORMAL+1
        if newlevel > ULTIMO_NIVEL_NORMAL:
            newlevel = 1
            setBonusRoundAttributes()
        
        for x in users:
            x.text = x.text.split("(")[0] + "(0)"

        doChangeLevel(screen,newlevel)


def checkChangeLevelDificil(screen,users):

    global TIEMPO_ENTRE_TERRONES,DURACION_TERRON,PUNTAJE_TOTAL
    
    amountOfUsers = len(users)
    if not EN_RED:
        amountOfUsers = 1
        
    updateTotalScore(users)

    if PUNTAJE_TOTAL >= PUNTAJE_FIN_NIVEL*amountOfUsers:
        newlevel = MULTIPLOS_DE_DIFICIL+1
        if newlevel > ULTIMO_NIVEL_DIFICIL:
            newlevel = 1
            setBonusRoundAttributes()
        
        for x in users:
            x.text = x.text.split("(")[0] + "(0)"

        doChangeLevel(screen,newlevel)

def setBonusRoundAttributes():
    
    global TIEMPO_ENTRE_TERRONES,DURACION_TERRON,PUNTAJE_FIN_NIVEL
    
    TIEMPO_ENTRE_TERRONES = .15
    DURACION_TERRON = 1
    PUNTAJE_FIN_NIVEL = 200
    
def doChangeLevel(screen,level,displayLevelChange=True):
   
    global MULTIPLOS_DE_FACIL, PORCENTAJE_OPORTUNIDAD_PREGUNTA

    MULTIPLOS_DE_FACIL = level
    if displayLevelChange:
        PORCENTAJE_OPORTUNIDAD_PREGUNTA = .03 * MULTIPLOS_DE_FACIL
        showLevelChange(screen)
        updateScore(0)

def doChangeLevelNormal(screen,level,displayLevelChange=True):
   
    global MULTIPLOS_DE_NORMAL, PORCENTAJE_OPORTUNIDAD_PREGUNTA

    MULTIPLOS_DE_NORMAL = level
    if displayLevelChange:
        PORCENTAJE_OPORTUNIDAD_PREGUNTA = .03 * MULTIPLOS_DE_NORMAL
        showLevelChange(screen)
        updateScore(0)

def doChangeDificil(screen,level,displayLevelChange=True):
   
    global MULTIPLOS_DE_DIFICIL, PORCENTAJE_OPORTUNIDAD_PREGUNTA

    MULTIPLOS_DE_DIFICIL = level
    if displayLevelChange:
        PORCENTAJE_OPORTUNIDAD_PREGUNTA = .03 * MULTIPLOS_DE_DIFICIL
        showLevelChange(screen)
        updateScore(0)


def showLevelChange(screen):
    
    screen.blit(FONDO,(0,0))
    drawScoreboard(screen)
    
    container = pygame.sprite.RenderUpdates()
    
    msg = textsprite.TextSprite(
        text = "Nivel Completado",
        color = (000,000,000),
        size = 50)
    msg.rect.center = screen.get_rect().center
    container.add(msg)
    
    container.draw(screen)
    pygame.display.flip()
    
    time.sleep(3)

def setupMoleFamily(screen,molefamily):

    for x in range(0,TERRONES_POR_LINEA):
        molefamily.append([])
        for y in range(0,TERRONES_POR_LINEA):
            molefamily[x].append([AGUJERO,0,0])

def updateMole(screen,molefamily):

    for x in range(0,TERRONES_POR_LINEA):
        for y in range(0,TERRONES_POR_LINEA):
            if (molefamily[x][y][0] == TERRON_WHACKED\
                    or molefamily[x][y][0] == TERRON_MISSED)\
                    and time.time()-molefamily[x][y][1] > TIEMPO_TERRON:
                molefamily[x][y][0] = AGUJERO
                
            elif molefamily[x][y][0] == TERRON_\
                    and time.time() - molefamily[x][y][1] > DURACION_TERRON:
                if molefamily[x][y][2] % MULTIPLOS_DE_FACIL == 0:
                    updateScore(PUNTAJE - 1)
                molefamily[x][y][0] = AGUJERO

def updateMoleNormal(screen,molefamily):

    for x in range(0,TERRONES_POR_LINEA):
        for y in range(0,TERRONES_POR_LINEA):
            if (molefamily[x][y][0] == TERRON_WHACKED\
                    or molefamily[x][y][0] == TERRON_MISSED)\
                    and time.time()-molefamily[x][y][1] > TIEMPO_TERRON:
                molefamily[x][y][0] = AGUJERO
                
            elif molefamily[x][y][0] == TERRON_\
                    and time.time() - molefamily[x][y][1] > DURACION_TERRON:
                if molefamily[x][y][2] % MULTIPLOS_DE_NORMAL == 0:
                    updateScore(PUNTAJE - 1)
                molefamily[x][y][0] = AGUJERO

def updateMoleDificil(screen,molefamily):

    for x in range(0,TERRONES_POR_LINEA):
        for y in range(0,TERRONES_POR_LINEA):
            if (molefamily[x][y][0] == TERRON_WHACKED\
                    or molefamily[x][y][0] == TERRON_MISSED)\
                    and time.time()-molefamily[x][y][1] > TIEMPO_TERRON:
                molefamily[x][y][0] = AGUJERO
                
            elif molefamily[x][y][0] == TERRON_\
                    and time.time() - molefamily[x][y][1] > DURACION_TERRON:
                if molefamily[x][y][2] % MULTIPLOS_DE_DIFICIL == 0:
                    updateScore(PUNTAJE - 1)
                molefamily[x][y][0] = AGUJERO



def refreshScreen(screen,molefamily,users,buddies):

    #Dibuja el fondo
    screen.blit(FONDO,(0,0))

    buddies.layout(screen.get_rect())
    users.draw(screen)

    # Dibuja el tablero
    drawBoard(screen,molefamily)

    # Dibuja el puntaje y el nivel
    drawScoreboard(screen)

    pygame.display.flip()

def refreshScreenNormal(screen,molefamily,users,buddies):

    #Dibuja el fondo
    screen.blit(FONDO,(0,0))

    buddies.layout(screen.get_rect())
    users.draw(screen)

    # Dibuja el tablero
    drawBoard(screen,molefamily)

    # Dibuja el puntaje y el nivel
    drawScoreboardNormal(screen)

    pygame.display.flip()

def refreshScreenDificil(screen,molefamily,users,buddies):

    #Dibuja el fondo
    screen.blit(FONDO,(0,0))

    buddies.layout(screen.get_rect())
    users.draw(screen)

    # Dibuja el tablero
    drawBoard(screen,molefamily)

    # Dibuja el puntaje y el nivel
    drawScoreboardDificil(screen)

    pygame.display.flip()

def drawBoard(screen,molefamily):

    font = pygame.font.Font("JAMultiplos/jamultiplos.ttf",60)
    for x in range(0,TERRONES_POR_LINEA):
        for y in range(0,TERRONES_POR_LINEA):
            screen.blit(molefamily[x][y][0],(x*100+OFFSET_X,y*100+OFFSET_Y))
            
            # Dibuja los numeros
            if (molefamily[x][y][0] == TERRON_):
                num = font.render(str(molefamily[x][y][2]),\
                                      True,(255,255,255))
                screen.blit(num,(OFFSET_X + x*100 + (100 - num.get_width()) / 2, OFFSET_Y + y*100 + (100 - num.get_height())/2 )) 

def drawScoreboard(screen):

    container = pygame.sprite.RenderUpdates()

    screen.blit(TABLERO,(OFFSET_X,OFFSET_Y-200))

    score = textsprite.TextSprite(
        text = str(PUNTAJE),
        color = (000,000,000),
        size = 15)
    score.rect.center = (OFFSET_X+103,OFFSET_Y-86)
    container.add(score)

    totalscore = textsprite.TextSprite(
        text = str(PUNTAJE_TOTAL),
        color = (000,000,000),
        size = 15)
    totalscore.rect.center = screen.get_rect().center
    totalscore.rect.center = (OFFSET_X+373,OFFSET_Y-86)
    container.add(totalscore)

    if MULTIPLOS_DE_FACIL == 1:
        display = "Clickea a todos!"
    else:
        display = "Clickea multiplos de " + str(MULTIPLOS_DE_FACIL) + "!"

    level = textsprite.TextSprite(
        text = display,
        color = (000,000,000),
        size = 15)
    level.rect.center = (OFFSET_X+244,OFFSET_Y-10)
    container.add(level)

    container.draw(screen)

    if MULTIPLOS_DE_FACIL == 1:
        display = "Nivel 1"
    else:
        display = "Nivel " + str(MULTIPLOS_DE_FACIL) + " "

    level = textsprite.TextSprite(
        text = display,
        color = (000,000,000),
        size = 15)
    level.rect.center = (OFFSET_X+244,OFFSET_Y-30)
    container.add(level)

    container.draw(screen)

def drawScoreboardNormal(screen):

    container = pygame.sprite.RenderUpdates()

    screen.blit(TABLERO,(OFFSET_X,OFFSET_Y-200))

    score = textsprite.TextSprite(
        text = str(PUNTAJE),
        color = (000,000,000),
        size = 15)
    score.rect.center = (OFFSET_X+103,OFFSET_Y-86)
    container.add(score)

    totalscore = textsprite.TextSprite(
        text = str(PUNTAJE_TOTAL),
        color = (000,000,000),
        size = 15)
    totalscore.rect.center = screen.get_rect().center
    totalscore.rect.center = (OFFSET_X+373,OFFSET_Y-86)
    container.add(totalscore)

    if MULTIPLOS_DE_NORMAL == 10:
        display = "Clickea multiplos de 10"
    else:
        display = "Clickea multiplos de " + str(MULTIPLOS_DE_NORMAL) + "!"

    level = textsprite.TextSprite(
        text = display,
        color = (000,000,000),
        size = 15)
    level.rect.center = (OFFSET_X+244,OFFSET_Y-10)
    container.add(level)

    container.draw(screen)

    if MULTIPLOS_DE_NORMAL == 10:
        display = "Nivel 10"
    else:
        display = "Nivel " + str(MULTIPLOS_DE_NORMAL) + " "

    level = textsprite.TextSprite(
        text = display,
        color = (000,000,000),
        size = 15)
    level.rect.center = (OFFSET_X+244,OFFSET_Y-30)
    container.add(level)

    container.draw(screen)

def drawScoreboardDificil(screen):

    container = pygame.sprite.RenderUpdates()

    screen.blit(TABLERO,(OFFSET_X,OFFSET_Y-200))

    score = textsprite.TextSprite(
        text = str(PUNTAJE),
        color = (000,000,000),
        size = 15)
    score.rect.center = (OFFSET_X+103,OFFSET_Y-86)
    container.add(score)

    totalscore = textsprite.TextSprite(
        text = str(PUNTAJE_TOTAL),
        color = (000,000,000),
        size = 15)
    totalscore.rect.center = screen.get_rect().center
    totalscore.rect.center = (OFFSET_X+373,OFFSET_Y-86)
    container.add(totalscore)

    if MULTIPLOS_DE_DIFICIL == 20:
        display = "Clickea multiplos de 20"
    else:
        display = "Clickea multiplos de " + str(MULTIPLOS_DE_DIFICIL) + "!"

    level = textsprite.TextSprite(
        text = display,
        color = (000,000,000),
        size = 15)
    level.rect.center = (OFFSET_X+244,OFFSET_Y-10)
    container.add(level)

    container.draw(screen)

    if MULTIPLOS_DE_DIFICIL == 20:
        display = "Nivel 20"
    else:
        display = "Nivel " + str(MULTIPLOS_DE_DIFICIL) + " "

    level = textsprite.TextSprite(
        text = display,
        color = (000,000,000),
        size = 15)
    level.rect.center = (OFFSET_X+244,OFFSET_Y-30)
    container.add(level)

    container.draw(screen)

def updateScore(action="update"):

    global PUNTAJE

    if action == TERRON_WHACKED:
        PUNTAJE = PUNTAJE+5
    elif action == TERRON_MISSED:
        PUNTAJE = PUNTAJE-2
    elif action == "update":
        pass
    else:
        PUNTAJE = action

    if PUNTAJE < 0:
        PUNTAJE = 0

    attemptBroadcast("updateScore"+DELIMITADOR+str(EN_RED)+DELIMITADOR+"("+str(PUNTAJE)+")")

def updateTotalScore(users):

    global PUNTAJE_TOTAL
    
    new_score = 0
    
    if not EN_RED:
        PUNTAJE_TOTAL = PUNTAJE
    else:
        for x in users:
            nameCheck = x.text.split("(")
            if len(nameCheck) < 2:
                pass
            else:
                new_score = new_score + int(nameCheck[1].split(")")[0])    

        PUNTAJE_TOTAL = new_score

def hitMole(screen,molefamily):


    posX = (pygame.mouse.get_pos()[0] -OFFSET_X) / 100
    posY = (pygame.mouse.get_pos()[1] -OFFSET_Y) / 100

    if (posX >= TERRONES_POR_LINEA or posY >= TERRONES_POR_LINEA\
            or posX < 0 or posY < 0):
        return
    

    if molefamily[posX][posY][0] == TERRON_:

        if molefamily[posX][posY][2]%MULTIPLOS_DE_FACIL == 0:
            molefamily[posX][posY][0] = TERRON_WHACKED
            updateScore(TERRON_WHACKED)
        else:
            molefamily[posX][posY][0] = TERRON_MISSED
            updateScore(TERRON_MISSED)

    else:
        molefamily[posX][posY][0] = TERRON_MISSED

    molefamily[posX][posY][1] = time.time()

def hitMoleNormal(screen,molefamily):


    posX = (pygame.mouse.get_pos()[0] -OFFSET_X) / 100
    posY = (pygame.mouse.get_pos()[1] -OFFSET_Y) / 100

    if (posX >= TERRONES_POR_LINEA or posY >= TERRONES_POR_LINEA\
            or posX < 0 or posY < 0):
        return
    

    if molefamily[posX][posY][0] == TERRON_:

        if molefamily[posX][posY][2]%MULTIPLOS_DE_NORMAL == 0:
            molefamily[posX][posY][0] = TERRON_WHACKED
            updateScore(TERRON_WHACKED)
        else:
            molefamily[posX][posY][0] = TERRON_MISSED
            updateScore(TERRON_MISSED)

    else:
        molefamily[posX][posY][0] = TERRON_MISSED

    molefamily[posX][posY][1] = time.time()

def hitDificil(screen,molefamily):


    posX = (pygame.mouse.get_pos()[0] -OFFSET_X) / 100
    posY = (pygame.mouse.get_pos()[1] -OFFSET_Y) / 100

    if (posX >= TERRONES_POR_LINEA or posY >= TERRONES_POR_LINEA\
            or posX < 0 or posY < 0):
        return
    

    if molefamily[posX][posY][0] == TERRON_:

        if molefamily[posX][posY][2]%MULTIPLOS_DE_DIFICIL == 0:
            molefamily[posX][posY][0] = TERRON_WHACKED
            updateScore(TERRON_WHACKED)
        else:
            molefamily[posX][posY][0] = TERRON_MISSED
            updateScore(TERRON_MISSED)

    else:
        molefamily[posX][posY][0] = TERRON_MISSED

    molefamily[posX][posY][1] = time.time()
    
def addMole(screen,molefamily):


    global TIEMPO_ULTIMO_TERRON_ANADIDO


    if time.time() - TIEMPO_ULTIMO_TERRON_ANADIDO > TIEMPO_ENTRE_TERRONES:
        randomX = random.randrange(0,TERRONES_POR_LINEA)
        randomY = random.randrange(0,TERRONES_POR_LINEA)
        

        if molefamily[randomX][randomY][0] != TERRON_:
            molefamily[randomX][randomY][0] = TERRON_
            molefamily[randomX][randomY][1] = time.time()
            numberChance = random.random()
            if numberChance < PORCENTAJE_OPORTUNIDAD_PREGUNTA:
                numberChance = random.randrange(1,12) * MULTIPLOS_DE_FACIL
            else:
                numberChance = random.randrange(1,12*MULTIPLOS_DE_FACIL)
            molefamily[randomX][randomY][2] = numberChance
            TIEMPO_ULTIMO_TERRON_ANADIDO = time.time()    

def addMoleNormal(screen,molefamily):


    global TIEMPO_ULTIMO_TERRON_ANADIDO


    if time.time() - TIEMPO_ULTIMO_TERRON_ANADIDO > TIEMPO_ENTRE_TERRONES:
        randomX = random.randrange(0,TERRONES_POR_LINEA)
        randomY = random.randrange(0,TERRONES_POR_LINEA)
        

        if molefamily[randomX][randomY][0] != TERRON_:
            molefamily[randomX][randomY][0] = TERRON_
            molefamily[randomX][randomY][1] = time.time()
            numberChance = random.random()
            if numberChance < PORCENTAJE_OPORTUNIDAD_PREGUNTA:
                numberChance = random.randrange(1,12) * MULTIPLOS_DE_NORMAL
            else:
                numberChance = random.randrange(1,12*MULTIPLOS_DE_NORMAL)
            molefamily[randomX][randomY][2] = numberChance
            TIEMPO_ULTIMO_TERRON_ANADIDO = time.time()    

def addMoleDificil(screen,molefamily):


    global TIEMPO_ULTIMO_TERRON_ANADIDO


    if time.time() - TIEMPO_ULTIMO_TERRON_ANADIDO > TIEMPO_ENTRE_TERRONES:
        randomX = random.randrange(0,TERRONES_POR_LINEA)
        randomY = random.randrange(0,TERRONES_POR_LINEA)
        

        if molefamily[randomX][randomY][0] != TERRON_:
            molefamily[randomX][randomY][0] = TERRON_
            molefamily[randomX][randomY][1] = time.time()
            numberChance = random.random()
            if numberChance < PORCENTAJE_OPORTUNIDAD_PREGUNTA:
                numberChance = random.randrange(1,12) * MULTIPLOS_DE_DIFICIL
            else:
                numberChance = random.randrange(1,12*MULTIPLOS_DE_DIFICIL)
            molefamily[randomX][randomY][2] = numberChance
            TIEMPO_ULTIMO_TERRON_ANADIDO = time.time()    


def interpretBroadcasts(event,users,screen):

    global NUEVO_JUEGO


    if event.content.startswith('updateScore'):
        content = event.content.split(DELIMITADOR)
        for x in users:
            if x.text.startswith(content[1]):
                x.set_text(content[1]+" "+content[2])
                

    elif event.content.startswith('broadcastLevel'):
        level = int(event.content.split(DELIMITADOR)[1])
        if (NUEVO_JUEGO == True):
            doChangeLevel(screen,level,False)
            NUEVO_JUEGO = False
    
def broadcastLevel():

    attemptBroadcast("broadcastLevel"+DELIMITADOR+str(MULTIPLOS_DE_FACIL))
    updateScore()

def broadcastLevelNormal():

    attemptBroadcast("broadcastLevel"+DELIMITADOR+str(MULTIPLOS_DE_NORMAL))
    updateScore()

def broadcastLevelDificil():

    attemptBroadcast("broadcastLevel"+DELIMITADOR+str(MULTIPLOS_DE_DIFICIL))
    updateScore()

def attemptBroadcast(msg):

    if EN_RED != False:
        mesh.broadcast(msg)

def checkSetEN_RED():


    if(EN_RED == False):
        def on_buddy(buddy):
            global EN_RED
            EN_RED = buddy.props.nick
        
        mesh.lookup_buddy(mesh.my_handle(),on_buddy)

def eventHandlers(screen,molefamily,users,buddies):

    for event in pygame.event.get():
        
        if event.type == pygame.QUIT: 
            return True
    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            hitMole(screen,molefamily)
        
        elif event.type == olpcgames.MESSAGE_MULTI:
            interpretBroadcasts(event,users,screen)
            
        elif event.type == olpcgames.PARTICIPANT_ADD:
            buddies.process(event)
            checkSetEN_RED()
            broadcastLevel()

        elif event.type == olpcgames.PARTICIPANT_REMOVE:
            buddies.process(event)

    pygame.event.pump()
            
    return False
        
def maingame():

    global OFFSET_X, OFFSET_Y,TAMANO_FUENTE
    
    size = (1200,850)
    if olpcgames.ACTIVITY:
        size = olpcgames.ACTIVITY.game_size
        TAMANO_FUENTE = 11

    screen = pygame.display.set_mode(size)

    OFFSET_X = size[0]/2 - TERRONES_POR_LINEA * 50
    OFFSET_Y = (size[1]/2 - TERRONES_POR_LINEA * 50) + 50

    users = pygame.sprite.RenderUpdates()
    buddies = ParticipantWatcher(groups=[users])

    molefamily = []
    setupMoleFamily(screen,molefamily)


    done = False
    while not done:
        done = eventHandlers(screen,molefamily,users,buddies)
        checkChangeLevel(screen,users)
        refreshScreen(screen,molefamily,users,buddies)
        updateMole(screen,molefamily)
        addMole(screen,molefamily)
        done = eventHandlers(screen,molefamily,users,buddies)

def maingamenormal():

    global OFFSET_X, OFFSET_Y,TAMANO_FUENTE
    
    size = (1200,850)
    if olpcgames.ACTIVITY:
        size = olpcgames.ACTIVITY.game_size
        TAMANO_FUENTE = 11

    screen = pygame.display.set_mode(size)

    OFFSET_X = size[0]/2 - TERRONES_POR_LINEA * 50
    OFFSET_Y = (size[1]/2 - TERRONES_POR_LINEA * 50) + 50

    users = pygame.sprite.RenderUpdates()
    buddies = ParticipantWatcher(groups=[users])

    molefamily = []
    setupMoleFamily(screen,molefamily)


    done = False
    while not done:
        done = eventHandlers(screen,molefamily,users,buddies)
        checkChangeLevelNormal(screen,users)
        refreshScreenNormal(screen,molefamily,users,buddies)
        updateMoleNormal(screen,molefamily)
        addMoleNormal(screen,molefamily)
        done = eventHandlers(screen,molefamily,users,buddies)


def maingamedificil():

    global OFFSET_X, OFFSET_Y,TAMANO_FUENTE
    
    size = (1200,850)
    if olpcgames.ACTIVITY:
        size = olpcgames.ACTIVITY.game_size
        TAMANO_FUENTE = 11

    screen = pygame.display.set_mode(size)

    OFFSET_X = size[0]/2 - TERRONES_POR_LINEA * 50
    OFFSET_Y = (size[1]/2 - TERRONES_POR_LINEA * 50) + 50

    users = pygame.sprite.RenderUpdates()
    buddies = ParticipantWatcher(groups=[users])

    molefamily = []
    setupMoleFamily(screen,molefamily)


    done = False
    while not done:
        done = eventHandlers(screen,molefamily,users,buddies)
        checkChangeLevelDificil(screen,users)
        refreshScreenDificil(screen,molefamily,users,buddies)
        updateMoleDificil(screen,molefamily)
        addMole(screen,molefamily)
        done = eventHandlers(screen,molefamily,users,buddies)

if __name__=="__main__":
    logging.basicConfig()
    maingame()
