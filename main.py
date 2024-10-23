import pygame
import sys

pygame.font.init()
font = pygame.font.SysFont(None, 24)

def display_coordinates(screen, x, y):
    text_surface = font.render(f"X: {x}, Y: {y-75}", True, (0, 0, 0))  # Black text
    screen.blit(text_surface, (10, 70))  # Display the text at position (10, 70)

class ColorPicker:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.image = pygame.Surface((w, h))
        self.image.fill((255, 255, 255))
        self.rad = h // 2
        self.pwidth = w - self.rad * 2
        for i in range(self.pwidth):
            color = pygame.Color(0)
            color.hsla = (int(360 * i / self.pwidth), 100, 50, 100)
            pygame.draw.rect(self.image, color, (i + self.rad, h // 3, 1, h - 2 * h // 3))
        self.p = 0

    def get_color(self):
        color = pygame.Color(0)
        color.hsla = (int(self.p * self.pwidth), 100, 50, 100)
        return color, self.p

    def set_color(self, p, screen):
        self.p = p


    def update(self):
        moude_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if moude_buttons[0] and self.rect.collidepoint(mouse_pos):
            self.p = (mouse_pos[0] - self.rect.left - self.rad) / self.pwidth
            self.p = (max(0, min(self.p, 1)))

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        center = self.rect.left + self.rad + self.p * self.pwidth, self.rect.centery
        color, trash = self.get_color()
        pygame.draw.circle(surf, color, center, self.rect.height // 2)

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

def draw_polygon(screen, points, color):
    if len(points) > 2:
        pygame.draw.polygon(screen, color, points, 1) 

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
        for i in range(0, len(sl), 2):
            rect = pygame.Rect(sl[i], row, sl[i+1]-sl[i]+1, 1)
            pygame.draw.rect(screen, color, rect)
        row = row+1


pygame.init()

WHITE = (255, 255, 255)
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fillpoly")

screen.fill(WHITE)
clock = pygame.time.Clock()
cp = ColorPicker(20, 20, 400, 50)

points = []
poly = []
poly_colors = []
selected = False
edit_mode = False
change_color = False

running = True
while running:
    clock.tick(100)
    color, color_p = cp.get_color()[:3]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            if edit_mode:
                for i, polygon in enumerate(poly):
                    if is_in_poly(pos, polygon):
                        y_max = 0
                        y_min = width
                        for point in polygon:
                            if point[1] < y_min:
                                y_min = point[1]
                            elif point[1] > y_max:
                                y_max = point[1]
                                sel_poly = i
                        fillpoly(screen, polygon, color, y_min, y_max)
            else:                
                if pos[1] > 150:
                    points.append(pos)  # Add point to the list
                    pygame.draw.circle(screen, color, pos, 3)  # Mark the selected point
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Press 'Enter' to finish the selection
                
                poly.append(points)
                
                y_max = 0
                y_min = width
                for point in points:
                    if point[1] < y_min:
                        y_min = point[1]
                    elif point[1] > y_max:
                        y_max = point[1]

                fillpoly(screen, points, color, y_min, y_max)  # Draw the polygon from selected points
                points = []

            elif event.key == pygame.K_SPACE:
                edit_mode = not edit_mode

            elif event.key == pygame.K_r:  # Press 'R' to reset the canvas
                screen.fill(WHITE)
                points = []
                poly = []

    mouse_x, mouse_y = pygame.mouse.get_pos()
    pygame.draw.rect(screen, WHITE, (0, 60, 200, 40))  # Clear previous coordinates
    display_coordinates(screen, mouse_x, mouse_y)

    cp.update()
    cp.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
