#   Change these to change the speed of falling blocks in each stage and after
#   how many lines cleared the next stage will begin
speed=[0.5,0.4,0.3]   #the numbers are delay between block moving down 1
afterlines=[40,80]
#
#
from random import randrange,shuffle
from math import floor
from statistics import mean
import time
import pygame
from pygame.locals import *
#dimensions of the game grid
dimx=10
dimy=20
#colors corresponding to specific pieces
colorshape={"line":(0,255,255),"l":(0,0,255),"li":(255,125,0),"z":(255,0,0),"zi":(0,255,0),"square":(255,255,0),"t":(255,0,255)}
#setting up the arrays
gamegrid=[]
shapes=[]
for i in range(0,dimy):
    gamegrid.append([])
    shapes.append([])
    for j in range(0,dimx):
        gamegrid[i].append(0)
        shapes[i].append(0)
#class for each shape
class Shape:
    def __init__(self,shape):
        self.shape=shape
        mid=floor(dimx/2)
        #start positions of each piece of the shape based on type
        if self.shape=="line":
            self.a=[mid-1,1];self.b=[mid,1];self.c=[mid+1,1];self.d=[mid+2,1];self.e=[mid+1,1]
        elif self.shape=="t":
            self.a=[mid-1,1];self.b=[mid,1];self.c=[mid,0];self.d=[mid+1,1];self.e=[mid,1]
        elif self.shape=="l":
            self.a=[mid-1,1];self.b=[mid,1];self.c=[mid+1,1];self.d=[mid+1,0];self.e=[mid,1]
        elif self.shape=="li":
            self.a=[mid-1,0];self.b=[mid-1,1];self.c=[mid,1];self.d=[mid+1,1];self.e=[mid,1]
        elif self.shape=="square":
            self.a=[mid,0];self.b=[mid+1,0];self.c=[mid,1];self.d=[mid+1,1];self.e=[mid,1]
        elif self.shape=="z":
            self.a=[mid-1,0];self.b=[mid,0];self.c=[mid,1];self.d=[mid+1,1];self.e=[mid,1]
        elif self.shape=="zi":
            self.a=[mid-1,1];self.b=[mid,1];self.c=[mid,0];self.d=[mid+1,0];self.e=[mid,1]
        self.pieces=[self.a,self.b,self.c,self.d]
    #rotates the pieces clockwise
    def rotate(self):
        #square pieces don't rotate
        if self.shape=="square":
            pass
        #line pieces have special rotation
        elif self.shape=="line":
            if self.a[1]==self.b[1]:
                if self.a[0]+2<dimx and self.a[1]+1<dimy and self.b[0]+1<dimx and self.c[1]-1>=0 and self.d[0]-1>=0:
                    self.a[0]+=2;self.a[1]+=1;self.b[0]+=1;self.c[1]-=1;self.d[0]-=1;self.d[1]-=2
            else:
                if self.a[0]-2>=0 and self.b[0]-1>=0 and self.c[1]+1<dimy and self.d[0]+1<dimx and self.d[1]+2<dimy:
                    self.a[0]-=2;self.a[1]-=1;self.b[0]-=1;self.c[1]+=1;self.d[0]+=1;self.d[1]+=2
        else:
            #doesn't rotate if rotating would interfere with other pieces on the grid
            for i in self.pieces:
                if (self.e[0]-(i[1]-self.e[1]))>=0 and (self.e[0]-(i[1]-self.e[1]))<dimx:
                    pass
                else:
                    return
                for j in range(0,dimy):
                    for k in range(0,dimx):
                        if (self.e[0]-(i[1]-self.e[1]))==k and (self.e[1]-(i[1]-self.e[1]))==j and Tetris.shapes[j][k]==1:
                            return
            #rotates each piece around the center piece
            for i in self.pieces:
                tempi=i.copy()
                i[1]=self.e[1]-(tempi[0]-self.e[0])
                i[0]=self.e[0]+(tempi[1]-self.e[1])
    #moves the shape down
    def movedown(self):
        for i in self.pieces:
            i[1]+=1
        self.e[1]+=1
    #moves the shape down as far as possible
    def harddrop(self):
        while True:
            for i in self.pieces:
                if i[1]<dimy:
                    for j in range(0,dimy):
                        for k in range(0,dimx):
                            if Tetris.shapes[j][k]!=0 and j==i[1] and k==i[0]:
                                return
                else:
                    return
            self.movedown()
    #moves the shape left
    def moveleft(self):
        for i in self.pieces:
            if not i[0]>0:
                return
            for j in range(0,dimy):
                for k in range(0,dimx):
                    if Tetris.shapes[j][k]!=0 and j==i[1] and k==i[0]-1:
                        return
        for i in self.pieces:
            i[0]-=1
        self.e[0]-=1
    #moves the shape right
    def moveright(self):
        for i in self.pieces:
            if not i[0]<dimx-1:
                return
            for j in range(0,dimy):
                for k in range(0,dimx):
                    if Tetris.shapes[j][k]!=0 and j==i[1] and k==i[0]+1:
                        return
        for i in self.pieces:
            i[0]+=1
        self.e[0]+=1
#game class
class Game:
    def __init__(self,grid,shapes):
        self.grid=grid
        self.shapes=shapes
        self.held=""
        self.score=0
        self.linescl=0
        self.running=True
        self.speed=1
        self.heldal=0
        self.shapez=6
        self.shapenum=["line","t","l","li","square","z","zi"]
        self.nextp=Shape(self.shapenum[randrange(0,len(self.shapenum))])
    #prints the game screen. this is what the user sees
    def prtscr(self):
        screen.fill((0,0,0))
        scoretext=font.render("Score-{} Lines-{}".format(self.score,self.linescl),True,(255,255,255),(0,0,0))
        heldtext=sfont.render("Held:",True,(255,255,255),(0,0,0))
        nexttext=sfont.render("Next:",True,(255,255,255),(0,0,0))
        screen.blit(heldtext,(5,0))
        screen.blit(nexttext,(310,0))
        screen.blit(scoretext,(75,10))
        pygame.draw.line(screen,(255,255,255),(50,0),(50,550))
        pygame.draw.line(screen,(255,255,255),(300,0),(300,550))
        pygame.draw.line(screen,(255,255,255),(50,50),(300,50))
        pygame.draw.rect(screen,(255,255,255),(50,550,250,5))
        pg=[]
        for i in range(0,4):
            pg.append(self.s.pieces[i][0])
        if initr==False:
            pygame.draw.line(screen,(255,255,255),(50+25*min(pg),50),(50+25*min(pg),550))
            pygame.draw.line(screen,(255,255,255),(50+25*(max(pg)+1),50),(50+25*(max(pg)+1),550))
        #displays the held shape
        if self.held!="":
            for i in [self.held.a,self.held.b,self.held.c,self.held.d]:
                pygame.draw.rect(screen,colorshape[self.held.shape],(i[1]*15,i[0]*15,15,15))
        #displays the next shape
        for i in [self.nextp.a,self.nextp.b,self.nextp.c,self.nextp.d]:
            pygame.draw.rect(screen,colorshape[self.nextp.shape],(335-i[1]*15,i[0]*15,15,15))
        for i in range(0,dimy):
            for j in range(0,dimx):
                if i>=0 and i<=dimy:
                    #displays the shapes already in the grid
                    if self.shapes[i][j]!=0:
                        pygame.draw.rect(screen,colorshape[self.shapes[i][j]],(50+j*25,50+i*25,25,25))
                    #displays the current shape
                    elif self.grid[i][j]==1:
                        pygame.draw.rect(screen,colorshape[self.shape],(50+j*25,50+i*25,25,25))
                    else:
                        pygame.draw.rect(screen,(25,25,25),(51+j*25,51+i*25,23,23))
    #creates a new shape
    def newshape(self):
        self.shape=self.shapenum[self.shapez]
        if self.shapez==6:
            shuffle(self.shapenum)
            self.shapez=-1
        self.s=Shape(self.shape)
        self.nextp=Shape(self.shapenum[self.shapez+1])
        self.shapez+=1
    #holds the current shape and brings the held shape into play
    def holdshape(self):
        if self.held=="":
            self.held=Shape(self.shape)
            self.newshape()
        #will hold only if you haven't already held a shape this round
        elif self.heldal==0:
            hshape=self.held.shape
            self.held=Shape(self.shape)
            self.shape=hshape
            self.s=Shape(self.shape)
            self.heldal=1
    #clears a line if it's filled in all the way horizontally
    def clearlines(self):
        n=0
        for i in range(0,dimy):
            m=0
            for j in range(0,dimx):
                if self.shapes[i][j]!=0:
                    m+=1
            if m==dimx:
                n+=1
                #clears pieces
                for j in range(0,dimx):
                    self.shapes[i][j]==0
                #brings pieces above the cleared line down
                for h in range(i,0,-1):
                    for j in range(0,dimx):
                        self.shapes[h][j]=self.shapes[h-1][j]
        #updates score based on how many lines have been cleared this round
        if n==1:
            self.score+=100
        elif n==2:
            self.score+=300
        elif n==3:
            self.score+=500
        elif n==4:
            self.score+=800
        self.linescl+=n
    #checks if the current piece is at the bottom of the screen or has hit a piece already in the grid
    def checkend(self):
        for j in range(0,dimy):
            for k in range(0,dimx):
                for i in self.pieces:
                    #locks the shape in and creates a new shape
                    if self.shapes[j][k]!=0 and j==i[1] and k==i[0]:
                        for l in self.pieces:
                            l[1]-=1
                            self.shapes[l[1]][l[0]]=self.shape
                        self.heldal=0;self.score+=10
                        self.newshape()
                        return 
        for i in self.pieces:
            #locks the shape in and creates a new shape
            if i[1]>dimy-1:
                for k in self.pieces:
                    self.shapes[k[1]-1][k[0]]=self.shape
                self.heldal=0;self.score+=10
                self.newshape()
                return
    #the main loop for the bame
    def gameloop(self):
        self.pieces=[self.s.a,self.s.b,self.s.c,self.s.d]
        self.checkend()
        self.clearlines()
        #updates the grid based on the position of the shapes in the grid
        for i in range(0,dimy):
            for j in range(0,dimx):
                if self.shapes[i][j]==0:
                    self.grid[i][j]=0
                else:
                    self.grid[i][j]=1
        #updates the grid based on the position of the current shape
        for i in self.pieces:
            if i[1]<dimy:
                self.grid[i[1]][i[0]]=1
        #pieces will fall faster after enough lines have been cleared
        if self.linescl>=afterlines[0]:
            self.speed=2
        if self.linescl>=afterline[1]:
            self.speed=3
        #checks if the game is over
        for i in range(0,dimy):
            for j in range(0,dimx):
                if shapes[i][j]!=0 and i<=0:
                    self.running=False
                    print("Score: {}\nLines cleared: {}".format(self.score,self.linescl))
                    return
#initializes pygame and its fonts and events
pygame.init()
screen=pygame.display.set_mode([350,555])
pygame.display.set_caption("Tetris")
font=pygame.font.Font("freesansbold.ttf",20)
sfont=pygame.font.Font("freesansbold.ttf",15)
MOVE1=pygame.USEREVENT+1
MOVE2=pygame.USEREVENT+2
MOVE3=pygame.USEREVENT+3
pygame.time.set_timer(MOVE1,speeds[0])
pygame.time.set_timer(MOVE2,speeds[1])
pygame.time.set_timer(MOVE3,speeds[2])
pygame.mixer.init()
#loads and plays music
pygame.mixer.music.load("Tetris_theme.ogg")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(loops=-1)
#creates a new game
Tetris=Game(gamegrid,shapes)
Tetris.newshape()
initr=True
#initial loop, before user starts game
while initr:
    screen.fill((0,0,0))
    for i in pygame.event.get():
        if i.type==pygame.QUIT:
            quit()
            pygame.quit()
        if i.type==pygame.KEYDOWN and i.key==pygame.K_RETURN:
            initr=False
    Tetris.prtscr()
    starttext=font.render("Press ENTER to Start",True,(255,255,255))
    frac=float(time.clock())-int(time.clock())
    if (frac<0.25 and frac>0) or (frac<0.75 and frac>0.5):
        screen.blit(starttext,(75,150))
    pygame.display.flip()
#game loop for pygame to run the game and check user input
while Tetris.running:
    screen.fill((0,0,0))
    for i in pygame.event.get():
        #quits game if exit button is pressed
        if i.type==pygame.QUIT:
            Tetris.running=False
            pygame.quit()
            quit()
        #checking keypress
        elif i.type==pygame.KEYDOWN:
            if i.key==pygame.K_SPACE:
                Tetris.s.harddrop()
            elif i.key==pygame.K_UP:
                Tetris.s.rotate()
            elif i.key==pygame.K_RIGHT:
                Tetris.s.moveright()
            elif i.key==pygame.K_LEFT:
                Tetris.s.moveleft()
            elif i.key==pygame.K_c:
                Tetris.holdshape()
        #increases speed after certain number of lines
        elif (i.type==MOVE1 and Tetris.speed==1) or (i.type==MOVE2 and Tetris.speed==2) or (i.type==MOVE3 and Tetris.speed==3):
                Tetris.s.movedown()
    key=pygame.key.get_pressed()
    if key[K_DOWN]:
        pygame.time.wait(60)
        Tetris.s.movedown()
    Tetris.gameloop()
    Tetris.prtscr()
    pygame.display.flip()
