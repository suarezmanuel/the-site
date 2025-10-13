from PIL import Image
import copy
# this is my very important information
matrix = [] 

def qr_image_to_matrix(image_path):
    global matrix
    im = Image.open(image_path)
    pix = im.load()
    for i in range(29):
        arr = []
        for j in range(29):
            ni = i*(im.size[0] // 29) + (im.size[0] // (29*2))
            nj = j*(im.size[1] // 29) + (im.size[1] // (29*2))
            arr.append(1 if pix[ni,nj][0] == 0 else 0)
        matrix.append(arr)

qr_image_to_matrix("image.png")
original_matrix = copy.deepcopy(matrix)

import pygame
pygame.init()

SCREEN_WIDTH = 493
SCREEN_HEIGHT = 493
SQUARE_SIZE_X = SCREEN_WIDTH // 29
SQUARE_SIZE_Y = SCREEN_HEIGHT // 29

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

background_image = pygame.transform.scale(pygame.image.load("background-2.png"), (SCREEN_WIDTH, SCREEN_HEIGHT))
background_image = background_image.convert_alpha()

transparent_block = pygame.Surface((SQUARE_SIZE_X, SQUARE_SIZE_Y), pygame.SRCALPHA)
transparent_block.fill((0, 0, 0, 0))

running = True
mouse_x, mouse_y = 0,0
current_event = None


def get_center_color(i,j, background_image):
    sx = j * (SQUARE_SIZE_X)
    sy = i * (SQUARE_SIZE_Y)
    sample_x = sx + (SQUARE_SIZE_X // 2)
    sample_y = sy + (SQUARE_SIZE_Y // 2)
    color = background_image.get_at((sample_x, sample_y))
    return color

def draw_grid(screen, background_image):
    for i in range(29):
        for j in range(29):

            curr_color = get_center_color(i, j, background_image)

            if i > 0: 
                up = get_center_color(i-1, j, background_image)
                if up != curr_color:
                    pygame.draw.line(screen, (189,168,0), (j*SQUARE_SIZE_X, i*SQUARE_SIZE_Y), ((j+1)*SQUARE_SIZE_X, i*SQUARE_SIZE_Y), 1) # target, color, start, end, width

            if j > 0:
                left = get_center_color(i, j-1, background_image)
                if left != curr_color:
                    pygame.draw.line(screen, (189,168,0), (j*SQUARE_SIZE_X, i*SQUARE_SIZE_Y), (j*SQUARE_SIZE_X, (i+1)*SQUARE_SIZE_Y), 1) # target, color, start, end, width

while running:
    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:
            current_event = event
        elif event.type == pygame.KEYUP:
            current_event = None
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos

        if current_event != None:
            if current_event.key == pygame.K_BACKSPACE or current_event.key == pygame.K_ESCAPE:
                running = False

            ni = mouse_x // (SQUARE_SIZE_X)
            nj = mouse_y // (SQUARE_SIZE_Y)
            if current_event.key == pygame.K_a:
                matrix[ni][nj] = 0
            if current_event.key == pygame.K_s:
                matrix[ni][nj] = 0 if matrix[ni][nj] == 1 else 1
            if current_event.key == pygame.K_d:
                matrix[ni][nj] = 1
            if current_event.key == pygame.K_f:
                matrix = copy.deepcopy(original_matrix)
                current_event = None

    screen.fill((112,112,112))
    background_image.set_alpha(128) 
    # screen.blit(background_image, (0, 0))

    for i in range(29):
        for j in range(29):
            if matrix[i][j] == 1:
                sx = i * (SQUARE_SIZE_X)
                sy = j * (SQUARE_SIZE_Y)

                sample_x = sx + (SQUARE_SIZE_X // 2)
                sample_y = sy + (SQUARE_SIZE_Y // 2)

                # color = background_image.get_at((sample_x, sample_y))

                # d = 70
                # color = (max(0,color.r - d), max(0,color.g - d), max(0,color.b - d))

                # pygame.draw.rect(screen, color, (sx, sy, SQUARE_SIZE_X, SQUARE_SIZE_Y))
                # screen.blit(transparent_block, (sx, sy))

                pygame.draw.rect(screen, (71,28,28), (sx, sy, SQUARE_SIZE_X, SQUARE_SIZE_Y))

    draw_grid(screen, background_image)

    pygame.display.flip()

pygame.quit()
