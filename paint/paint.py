import pygame
import sys

pygame.init()

# screen size
WIDTH  = 800
HEIGHT = 600
PANEL_H = 60  # height of toolbar at the bottom

# colors for palette
PALETTE = [
    (0,   0,   0),    # black
    (255, 255, 255),  # white
    (255, 0,   0),    # red
    (0,   200, 0),    # green
    (0,   0,   255),  # blue
    (255, 255, 0),    # yellow
    (255, 165, 0),    # orange
    (128, 0,   128),  # purple
    (0,   255, 255),  # cyan
    (255, 105, 180),  # pink
    (139, 69,  19),   # brown
    (128, 128, 128),  # gray
]

# tool names
TOOL_PENCIL = "pencil"
TOOL_RECT   = "rect"
TOOL_CIRCLE = "circle"
TOOL_ERASER = "eraser"

# window setup
screen = pygame.display.set_mode((WIDTH, HEIGHT + PANEL_H))
pygame.display.set_caption("Paint")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Verdana", 13)

# canvas - separate surface where we draw
canvas = pygame.Surface((WIDTH, HEIGHT))
canvas.fill((255, 255, 255))  # white background


# draws the toolbar at the bottom
def draw_toolbar(current_color, current_tool, brush_size):
    # toolbar background
    pygame.draw.rect(screen, (220, 220, 220), (0, HEIGHT, WIDTH, PANEL_H))
    pygame.draw.line(screen, (150, 150, 150), (0, HEIGHT), (WIDTH, HEIGHT), 2)

    # draw color palette
    for i, color in enumerate(PALETTE):
        x = 10 + i * 38
        y = HEIGHT + 10
        rect = pygame.Rect(x, y, 32, 32)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        # highlight selected color
        if color == current_color:
            pygame.draw.rect(screen, (0, 0, 0), rect, 3)

    # draw tool buttons
    tools = [TOOL_PENCIL, TOOL_RECT, TOOL_CIRCLE, TOOL_ERASER]
    for i, tool in enumerate(tools):
        x = 480 + i * 75
        y = HEIGHT + 15
        rect = pygame.Rect(x, y, 65, 25)
        # highlight selected tool
        color = (180, 180, 255) if tool == current_tool else (200, 200, 200)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 1)
        label = font.render(tool, True, (0, 0, 0))
        screen.blit(label, (x + 5, y + 5))

    # draw brush size indicator
    size_label = font.render(f"size: {brush_size}", True, (0, 0, 0))
    screen.blit(size_label, (WIDTH - 80, HEIGHT + 22))


# main variables
current_color = (0, 0, 0)   # starting color is black
current_tool  = TOOL_PENCIL  # starting tool is pencil
brush_size    = 5            # brush/eraser size
drawing       = False        # is mouse button held down
start_pos     = None         # starting position for rect and circle


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # scroll to change brush size
        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(50, brush_size + event.y))

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                mx, my = event.pos

                # check if clicked on toolbar
                if my > HEIGHT:
                    # check color palette clicks
                    for i, color in enumerate(PALETTE):
                        x = 10 + i * 38
                        y = HEIGHT + 10
                        if x <= mx <= x + 32 and y <= my <= y + 32:
                            current_color = color

                    # check tool button clicks
                    tools = [TOOL_PENCIL, TOOL_RECT, TOOL_CIRCLE, TOOL_ERASER]
                    for i, tool in enumerate(tools):
                        x = 480 + i * 75
                        y = HEIGHT + 15
                        if x <= mx <= x + 65 and y <= my <= y + 25:
                            current_tool = tool
                else:
                    # started drawing on canvas
                    drawing   = True
                    start_pos = (mx, my)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                mx, my = event.pos
                my = min(my, HEIGHT - 1)  # clamp to canvas area

                # draw rectangle on mouse release
                if current_tool == TOOL_RECT and start_pos:
                    x = min(start_pos[0], mx)
                    y = min(start_pos[1], my)
                    w = abs(mx - start_pos[0])
                    h = abs(my - start_pos[1])
                    pygame.draw.rect(canvas, current_color, (x, y, w, h), brush_size)

                # draw circle on mouse release
                if current_tool == TOOL_CIRCLE and start_pos:
                    cx = (start_pos[0] + mx) // 2
                    cy = (start_pos[1] + my) // 2
                    rx = abs(mx - start_pos[0]) // 2
                    ry = abs(my - start_pos[1]) // 2
                    if rx > 0 and ry > 0:
                        pygame.draw.ellipse(canvas, current_color,
                                            (cx - rx, cy - ry, rx * 2, ry * 2), brush_size)

                drawing   = False
                start_pos = None

        if event.type == pygame.KEYDOWN:
            # press c to clear the canvas
            if event.key == pygame.K_c:
                canvas.fill((255, 255, 255))

    # pencil and eraser work while mouse is held down
    if drawing and current_tool in (TOOL_PENCIL, TOOL_ERASER):
        mx, my = pygame.mouse.get_pos()
        if my < HEIGHT:  # only draw on canvas area
            color = (255, 255, 255) if current_tool == TOOL_ERASER else current_color
            pygame.draw.circle(canvas, color, (mx, my), brush_size)

    # draw canvas onto screen
    screen.blit(canvas, (0, 0))

    # draw preview for rect and circle while dragging
    if drawing and start_pos:
        mx, my = pygame.mouse.get_pos()
        my = min(my, HEIGHT - 1)

        if current_tool == TOOL_RECT:
            x = min(start_pos[0], mx)
            y = min(start_pos[1], my)
            w = abs(mx - start_pos[0])
            h = abs(my - start_pos[1])
            # draw dashed preview on screen (not canvas)
            pygame.draw.rect(screen, current_color, (x, y, w, h), 1)

        if current_tool == TOOL_CIRCLE:
            cx = (start_pos[0] + mx) // 2
            cy = (start_pos[1] + my) // 2
            rx = abs(mx - start_pos[0]) // 2
            ry = abs(my - start_pos[1]) // 2
            if rx > 0 and ry > 0:
                pygame.draw.ellipse(screen, current_color,
                                    (cx - rx, cy - ry, rx * 2, ry * 2), 1)

    # draw toolbar on top of everything
    draw_toolbar(current_color, current_tool, brush_size)

    pygame.display.update()
    clock.tick(60)
