import pygame
import sys

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
        return color

    def update(self):
        moude_buttons = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        if moude_buttons[0] and self.rect.collidepoint(mouse_pos):
            self.p = (mouse_pos[0] - self.rect.left - self.rad) / self.pwidth
            self.p = (max(0, min(self.p, 1)))

    def draw(self, surf):
        surf.blit(self.image, self.rect)
        center = self.rect.left + self.rad + self.p * self.pwidth, self.rect.centery
        pygame.draw.circle(surf, self.get_color(), center, self.rect.height // 2)
# Initialize Pygame
pygame.init()

# Set up the canvas (width, height)
width, height = 1000, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Polygon Drawing")

WHITE = (255, 255, 255)

# Create a blank surface
screen.fill(WHITE)
clock = pygame.time.Clock()
cp = ColorPicker(20, 20, 400, 50)
cp_show = False

# List to store selected points
points = []
poly = []

def draw_polygon(screen, points, color):
    if len(points) > 2:
        pygame.draw.polygon(screen, color, points, 1) 

def scanline_calc(points, y_min, y_max):
    nv = len(points) # Numero de vertices
    ns = y_max - y_min # Numero de scanlines
    for p in range(nv):
        for i in range(p, nv):
            m = (points[p][1]-points[i][1])/(points[p][0]-points[i][0])

def fillpoly(screen, points, color, y_min, y_max):
    scanline_calc(points, y_min, y_max)


# Main loop
running = True
while running:
    y_min = 0
    y_max = 0
    clock.tick(100)
    color = cp.get_color()[:3]
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if pos[1] > 150:
                if pos[1] < y_min:
                    y_min = pos[1]
                elif pos[1] > y_max:
                    y_max = pos[1]
                points.append(pos)  # Add point to the list
                pygame.draw.circle(screen, color, pos, 3)  # Mark the selected point
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Press 'Enter' to finish the selection
                poly.append(points)
                # You can process points with your algorithm here before drawing
                draw_polygon(screen, points, color, y_min, y_max)  # Draw the polygon from selected points
                points = []
            elif event.key == pygame.K_r:  # Press 'R' to reset the canvas
                screen.fill(WHITE)
                points = []
                poly = []

    cp.update()
    cp.draw(screen)

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
sys.exit()
