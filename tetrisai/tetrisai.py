from random import randrange,shuffle
from math import floor
from statistics import mean,stdev
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
        self.heldal=0
        #multipliers for attributes
        self.maxhmult=-2.0     #-2.0
        self.scoremult=1.3     #1.3
        self.holemult=-1.8     #-1.8   
        self.agghmult=-4.85    #-4.9
        self.bumpymult=-1.0    #-1.1
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
        screen.blit(scoretext,(55,10))
        pygame.draw.line(screen,(255,255,255),(50,0),(50,550))
        pygame.draw.line(screen,(255,255,255),(300,0),(300,550))
        pygame.draw.line(screen,(255,255,255),(50,50),(300,50))
        pygame.draw.rect(screen,(255,255,255),(50,550,250,5))
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
    #checks if a certain move will score points
    def checkScore(self):
        gn=0
        for k in range(0,dimy):
            gm=0
            for j in range(0,dimx):
                if self.tshapes[k][j]!=0:
                    gm+=1
            if gm==dimx:
                gn+=1
        self.incscore=gn
    #checks if a certain move will add holes
    def checkHoles(self):
        for i in range(0,dimx):
            for j in range(0,dimy):
                if self.tshapes[j][i]==0 and self.tshapes[j-1][i]!=0:
                    self.holes+=1
    #checks the height of each column
    def getHeights(self):
        for i in range(0,dimx):
            self.heights.append(0)
            for j in range(dimy-1,0,-1):
                if self.tshapes[j][i]!=0:
                    self.heights[i]=dimy-j
    #goes through all possible moves to find the best one based on amount of holes, heights of columns, etc.
    def parsemoves(self):
        self.possible=[]
        self.getto=[]
        if self.shape=="line":
            ii=2
        elif self.shape=="square":
            ii=1
        else:
            ii=4
        #goes through every move and add it to a list
        for ii in range(0,4):
            for j in range(0,11):
                self.test=Shape(self.shape)
                for k in range(0,ii):
                    self.test.rotate()
                if j<7:
                    for k in range(0,j):
                        self.test.moveleft()
                else:
                    for k in range(0,j-6):
                        self.test.moveright()
                self.test.harddrop()
                for k in self.test.pieces:
                    k[1]-=1
                self.possible.append(self.test.pieces)
                if j<7:
                    self.getto.append([ii,j,True])
                else:
                    self.getto.append([ii,j-6,False])
        self.values=[]
        self.tshapes=[]
        self.check=[]
        #finds the value of each possible move
        for ii in range(0,len(self.possible)):
            self.tshapes=self.shapes.copy()
            self.nnn=[]
            for jj in range(0,len(self.possible[ii])):
                self.tshapes[self.possible[ii][jj][1]][self.possible[ii][jj][0]]=self.shape
            #attributes that determine the best move
            self.holes=0
            self.bumpiness=0
            self.heights=[]
            self.incscore=0
            self.aggheight=0
            self.maxheight=0
            self.getHeights()
            self.checkHoles()
            self.checkScore()
            self.aggheight=sum(self.heights)
            self.maxheight=max(self.heights)
            for i in range(0,len(self.heights)-1):
                self.bumpiness+=abs(self.heights[i]-self.heights[i+1])
            #adding together the attributes
            self.values.append(self.maxhmult*self.maxheight+self.scoremult*self.incscore+self.bumpymult*self.bumpiness+self.holemult*self.holes+self.agghmult*self.aggheight)
            for jj in range(0,len(self.possible[ii])):
                self.tshapes[self.possible[ii][jj][1]][self.possible[ii][jj][0]]=0
        #finds the best possible move based on the values
        lll=self.getto[self.values.index(max(self.values))]
        #moves the current shape to the best possible position
        for i in range(0,lll[0]):
            self.s.rotate()
        for i in range(0,lll[1]):
            if lll[2]==True:
                self.s.moveleft()
            else:
                self.s.moveright()
        #self.s.harddrop()
        self.prtscr()
    #creates a new shape
    def newshape(self):
        self.shape=self.shapenum[self.shapez]
        if self.shapez==6:
            shuffle(self.shapenum)
            self.shapez=-1
        self.s=Shape(self.shape)
        self.nextp=Shape(self.shapenum[self.shapez+1])
        self.shapez+=1
        self.parsemoves()
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
        #self.parsemoves()
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
pygame.time.set_timer(MOVE1,30)
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
        screen.blit(starttext,(60,150))
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
        #moves the piece down every certain amount of time
        elif i.type==MOVE1:
            Tetris.s.movedown()
            Tetris.prtscr()
    Tetris.gameloop()
    Tetris.prtscr()
    pygame.display.flip()
