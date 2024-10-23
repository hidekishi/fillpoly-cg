import pygame
import sys

pygame.font.init()
font = pygame.font.SysFont(None, 24)

def display_coordinates(screen, x, y):
    text_surface = font.render(f"X: {x}, Y: {y}", True, (0, 0, 0))  # Black text
    screen.blit(text_surface, (10, 70))  # Display the text at position (10, 70)

class Polygon:
    def __init__(self, x, y, color, yMin, yMax):
        self.x = x
        self.y = y
        self.color = color
        self.yMin = yMin
        self.yMax = yMax

class ColorPicker:
    def __init__(self, x, y, w, h, surf):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h))
        self.width = w
        self.height = h
        for i in range(w):
            color = pygame.Color(0)
            color.hsla = (int(360 * i / w), 100, 50, 100)
            pygame.draw.rect(self.image, color, (i, 0, 1, h))
        surf.blit(self.image, self.rect)
        self.p = 0

    def get_color(self):
        color = pygame.Color(0)
        color.hsla = (int(self.p * 360), 100, 50, 100)
        return color, self.p

    def set_color(self, p, screen):
        self.p = p

    def update(self):
        moude_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if moude_buttons[0] and self.rect.collidepoint(mouse_pos):
            self.p = (mouse_pos[0] - self.rect.left) / self.width
            self.p = (max(0, min(self.p, 1)))


def is_in_poly(point, polygon):
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

def scanline_calc(points, y_min, y_max):
    nv = len(points) # Numero de vertices
    ns = y_max - y_min # Numero de scanlines

    scanline_list = []
    for i in range(ns):
        scanline = []
        scanline_list.append(scanline)

    for i in range(nv):
        x1, y1 = points[i]
        x2, y2 = points[(i+1)%nv]
        if y2 < y1:
            xa, ya = x2, y2
            x2, y2 = x1, y1
            x1, y1 = xa, ya
        y1, y2 = y1-y_min, y2-y_min
        xn = x1
        if x1 == x2 or y1 == y2:
            tx = 0
        else:
            tx = (x2-x1)/(y2-y1)

        scanline_list[y1].append(x1)
        for c in range(y1+1, y2):
            xn = xn+tx
            scanline_list[c].append(int(xn))
    for sl in scanline_list:
        sl.sort()
    return scanline_list

def fillpoly(screen, points, color, y_min, y_max):
    scanlines = scanline_calc(points, y_min, y_max)
    row = y_min
    for sl in scanlines:
        for i in range(0, len(sl)-1, 2):
            rect = pygame.Rect(sl[i], row, sl[i+1]-sl[i]+1, 1)
            pygame.draw.rect(screen, color, rect)
        row = row+1


pygame.init()

WHITE = (255, 255, 255)
GREY = (220, 220, 220)
width, height = 1000, 800
boxWidth, boxHeight = 1000, 720
boxRect = pygame.Rect(0, 80, 1000, 720)
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fillpoly")

screen.fill(GREY)
screen.fill(WHITE, boxRect)
clock = pygame.time.Clock()
cp = ColorPicker(20, 30, 400, 20, screen)

points = []
poly = []
poly_colors = []
selected = False
sel_poly = []
edit_mode = False
change_color = False
del_poly = False

running = True
while running:
    clock.tick(100)
    color, color_p = cp.get_color()[:3]
    pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:         
            if not edit_mode:                
                if pos[1] > 80:
                    points.append(pos)  # Add point to the list
                    pygame.draw.circle(screen, color, pos, 3)  # Mark the selected point
            else:
                yMin = width
                yMax = 0
                for i, polygon in enumerate(poly):
                    if is_in_poly(pos, polygon):
                        yMax = 0
                        yMin = width
                        for point in polygon:
                            if point[1] < y_min:
                                yMin = point[1]
                            elif point[1] > y_max:
                                yMax = point[1]
                                sel_poly = i
                        selected = True
                        sel_poly = [i, yMin, yMax]
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Press 'Enter' to finish the selection   
                if len(points) >= 3:
                    poly.append(points)
                    
                    y_max = 0
                    y_min = width
                    for point in points:
                        if point[1] < y_min:
                            y_min = point[1]
                        elif point[1] > y_max:
                            y_max = point[1]

                    fillpoly(screen, points, color, y_min, y_max)  # Draw the polygon from selected points
                    poly_colors.append(color)
                    points = []

            elif event.key == pygame.K_SPACE:
                edit_mode = not edit_mode

            elif event.key == pygame.K_DELETE:
                if selected:
                    poly.pop(sel_poly[0])
                    poly_colors.pop(sel_poly[0])

            elif event.key == pygame.K_r:  # Press 'R' to reset the canvas
                screen.fill(WHITE, boxRect)
                points = []
                poly = []
            elif event.key == pygame.K_c:
                change_color = not change_color

    if edit_mode:
        #print(sel_poly)
        if selected:
            print(sel_poly[0])
        if change_color and selected:
            fillpoly(screen, poly[sel_poly[0]], color, sel_poly[1], sel_poly[2])
        if del_poly:
            poly.pop(i)

    pygame.draw.rect(screen, WHITE, (0, 60, 200, 40))  # Clear previous coordinates
    display_coordinates(screen, pos[0], pos[1])

    cp.update()

    pygame.display.flip()

pygame.quit()
sys.exit()
