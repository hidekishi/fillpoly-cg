import pygame
import sys

#Configuracoes de fonte
pygame.font.init()
buttonFont = pygame.font.SysFont(None, 15)
coordFont = pygame.font.SysFont(None, 18)

# Funcoes e classes
def display_coordinates(screen, x, y): # Display das coordenadas no canto inferior esquerdo da tela
    y = y-80
    if y < 0:
        x = "- "
        y = "-"
    text_surface = coordFont.render(f"X: {x}, Y: {y}", True, (0, 0, 0))
    screen.blit(text_surface, (10, height-40))

class Button: # Botoes da interface 
    def __init__(self, x, y, w, h, surface, text):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.surface = surface
        self.text = text
        self.bound = pygame.Rect(x+3, y+3, w-6, h-6)
        self.color = RED
        pygame.draw.rect(self.surface, DARK_GREY, pygame.Rect(x, y, w, h))
        pygame.draw.rect(self.surface, self.color, self.bound)
        textSurface = buttonFont.render(text, True, (100, 100, 100))
        self.surface.blit(textSurface, (x-len(text)/2, y-20))
    def enable(self):
        self.color = GREEN
        pygame.draw.rect(self.surface, self.color, self.bound)
    def disable(self):
        self.color = RED
        pygame.draw.rect(self.surface, self.color, self.bound)
    def block(self):
        self.color = (100, 100, 100)
        pygame.draw.rect(self.surface, self.color, self.bound)

class Polygon: # Dados do poligono e seus metodos de calculo e preenchimento
    def __init__(self, points, color, colorP, yMin, yMax, paintedEdge, surface):
        self.points = points
        self.color = color
        self.colorP = colorP
        self.yMin = yMin
        self.yMax = yMax
        self.surface = surface
        self.paintedEdge = paintedEdge
        self.scanlineList = []
    
    def scanline_calc(self): # Codigo de calculo das scanlines de forma incremental
        if len(self.scanlineList) > 0:
            return self.scanlineList
        
        nv = len(self.points) # Numero de vertices
        ns = self.yMax - self.yMin # Numero de scanlines

        for i in range(ns):
            scanline = []
            self.scanlineList.append(scanline)

        for i in range(nv):
            x1, y1 = self.points[i]
            x2, y2 = self.points[(i+1)%nv]
            if y2 < y1:
                xa, ya = x2, y2
                x2, y2 = x1, y1
                x1, y1 = xa, ya
            y1, y2 = y1-self.yMin, y2-yMin
            xn = x1
            if x1 == x2 or y1 == y2:
                tx = 0
            else:
                tx = (x2-x1)/(y2-y1)

            self.scanlineList[y1].append(x1)
            for c in range(y1+1, y2):
                xn = xn+tx
                self.scanlineList[c].append(int(xn))
        for sl in self.scanlineList:
            sl.sort()
        return self.scanlineList
    
    def paint_edges(self): # Codigo para pintura das arestas de amarelo
        row = self.yMin
        for sl in self.scanlineList:
            for i in range(0, len(sl)):
                rect = pygame.Rect(sl[i], row, 3, 3)
                pygame.draw.rect(self.surface, (255, 255, 0), rect)
            row = row+1

    def fillpoly(self): # Algoritmo fillpoly em si. Pega a lista de scanlines e preenche linha por linha
        scanlines = self.scanline_calc()
        row = self.yMin
        for sl in scanlines:
            for i in range(0, len(sl)-1, 2):
                rect = pygame.Rect(sl[i], row, sl[i+1]-sl[i]+1, 1)
                pygame.draw.rect(self.surface, self.color, rect)
            row = row+1
        if self.paintedEdge:
            self.paint_edges()

    def change_color(self, newColor, newcolorP): # Codigo para mudanca de cor. Pinta novamente o poligono
        self.color = newColor
        self.colorP = newcolorP
        self.fillpoly()

class ColorPicker: # "Roda de cores"
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h))
        self.image.fill(GREY)
        self.rad = h//2
        self.pwidth = w-self.rad*2
        for i in range(self.pwidth):
            color = pygame.Color(0)
            color.hsla = (int(360*i/self.pwidth), 100, 50, 100)
            pygame.draw.rect(self.image, color, (i+self.rad, h//3, 1, h-2*h//3))
        self.p = 0

    def get_color(self):
        color = pygame.Color(0)
        color.hsla = (int(self.p * self.pwidth), 100, 50, 100)
        return color, self.p

    def update(self):
        moude_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if moude_buttons[0] and self.rect.collidepoint(mouse_pos):
            self.p = (mouse_pos[0] - self.rect.left - self.rad) / self.pwidth
            self.p = (max(0, min(self.p, 1)))

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        center = self.rect.left + self.rad + self.p * self.pwidth, self.rect.centery
        color, colorP = self.get_color()
        color = color[:3]
        pygame.draw.circle(surf, color, center, self.rect.height // 2)

    def set_color(self, colorP):
        self.p = colorP

def draw_all_polygons(polygonList): # Desenha todos os poligonos listados. Utilizado para delecao de poligonos especificos
    for i in range(len(polygonList)):
        polygonList[i].fillpoly()

def is_in_poly(point, polygon): # Retorna se se ha um poligono na posicao do mouse
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y >= min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

pygame.init() # Inicia o Pygame

# Parametros e constantes
WHITE = (255, 255, 255)
GREY = (220, 220, 220)
DARK_GREY = (190, 190, 190)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
width, height = 1000, 800
boxWidth, boxHeight = 1000, 720

# Construcao da interface
boxRect = pygame.Rect(0, 80, 1000, 720)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fillpoly")
screen.fill(GREY)
screen.fill(WHITE, boxRect)
clock = pygame.time.Clock()
cp = ColorPicker(20, 10, 400, 60)
edgeButton = Button(800, 30, 60, 30, screen, "Pintar arestas")
polyButton = Button(900, 30, 60, 30, screen, "Pintar poligono")
delText = coordFont.render("* <DEL> para deletar poligono selecionado", True, (100, 100, 100))
rText = coordFont.render("* <R> para limpar a tela e a lista de poligonos", True, (100, 100, 100))
enterText = coordFont.render("* <ENTER> para confirmar pontos e desenhar o poligono", True, (100, 100, 100))
screen.blit(enterText, (430, 10))
screen.blit(delText, (430, 30))
screen.blit(rText, (430, 50))

# Variaveis/flags para execucao
points = []
polygonList = []
selected = False
selectedPolyIndex = -1
editMode = True
paintedEdge = False
deletePoly = False

def painted_edge_event(paintedEdge):
    if not editMode:
        if paintedEdge:
            edgeButton.enable()
        else:
            edgeButton.disable()

def edit_mode_event(editMode):
    if editMode:
        polyButton.disable()
        edgeButton.block()
    else:
        polyButton.enable()
        edgeButton.disable()

if editMode:
    edgeButton.block()

# ----> Execucao <----
running = True
while running:
    clock.tick(100)
    color, colorP = cp.get_color()
    color = color[:3]
    mousePosition = pygame.mouse.get_pos() # Posicao do mouse

    for event in pygame.event.get(): # Eventos da execucao

        if event.type == pygame.QUIT: # Saida
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN: # Input de clique mouse   
            if event.button == 1:
                if edgeButton.bound.collidepoint(mousePosition):
                    paintedEdge = not paintedEdge
                    painted_edge_event(paintedEdge)
                if polyButton.bound.collidepoint(mousePosition):
                    editMode = not editMode
                    edit_mode_event(editMode)
                    if not editMode:
                        paintedEdge = False
                    selected = False

                if not editMode:                
                    if mousePosition[1] > 80:
                        samePoint = False
                        for point in points:
                            if mousePosition == point:
                                samePoint = True
                        if not samePoint:
                            points.append(mousePosition)
                        pygame.draw.circle(screen, color, mousePosition, 1) 
                else:
                    yMin = width
                    yMax = 0
                    for i, polygon in enumerate(polygonList):
                        insidePoly = is_in_poly(mousePosition, polygon.points)
                        if insidePoly:
                            yMax = 0
                            yMin = width
                            for point in polygon.points:
                                if point[1] < yMin:
                                    yMin = point[1]
                                elif point[1] > yMax:
                                    yMax = point[1]
                                    sel_poly = i
                            selected = True
                            selectedPolyIndex = i
                    if selected:
                        cp.set_color(polygonList[selectedPolyIndex].colorP)
            
        elif event.type == pygame.KEYDOWN: # Input teclado

            if event.key == pygame.K_RETURN:  # Enter para confirmar poligono 
                if len(points) >= 3:
                    yMax = 0

                    yMin = height
                    for point in points:
                        if point[1] < yMin:
                            yMin = point[1]
                        if point[1] > yMax:
                            yMax = point[1]

                    polygon = Polygon(points, color, colorP, yMin, yMax, paintedEdge, screen)
                    polygonList.append(polygon)
                    polygon.fillpoly()

                    points = []

            elif event.key == pygame.K_e: # E para ativar o contorno
                paintedEdge = not paintedEdge
                painted_edge_event(paintedEdge)

            elif event.key == pygame.K_SPACE:
                editMode = not editMode
                edit_mode_event(editMode)
                if not editMode:
                    paintedEdge = False
                selected = False

            elif event.key == pygame.K_DELETE: # DELETE para deletar poligono selecionado
                if selected:
                    polygonList.pop(selectedPolyIndex)
                    screen.fill(WHITE, boxRect)
                    draw_all_polygons(polygonList)
                    selected = False

            elif event.key == pygame.K_r:  # R para resetar a tela
                screen.fill(WHITE, boxRect)
                #changeColor = False
                editMode = False
                points = []
                polygonList = []

    if editMode: # Mudanca de cor do poligono selecionado
        if selected:
            color, colorP = cp.get_color()
            color = color[:3]
            polygonList[selectedPolyIndex].change_color(color, colorP)
            polygonList[selectedPolyIndex].fillpoly()

# Insercao das coordenadas na tela
    pygame.draw.rect(screen, WHITE, (10, height-50, 200, 40))  
    display_coordinates(screen, mousePosition[0], mousePosition[1])

    cp.update()
    cp.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
