import pygame
import random
import queue

# Basado en el juego Snake visto en clase (presentación 9: Modelamiento y simulación)
pygame.init()

# ---------------- Colores (RGB) ----------------
black = (0, 0, 0)
white = (255, 255, 255)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
yellow = (255, 255, 0)
pink = (255, 0, 255)  # color que se vuelve transparente en la imagen

# ---------------- Resolución ----------------
diswidth = 600
disheight = 400

# ---------------- Ventana ----------------
dis = pygame.display.set_mode((diswidth, disheight))
pygame.display.set_caption("Snake")

# ---------------- Variables de la serpiente ----------------
snakeblock = 20
snakespeed = 15
compass = {
    "left": [-snakeblock, 0, "left"],
    "right": [snakeblock, 0, "right"],
    "up": [0, -snakeblock, "up"],
    "down": [0, snakeblock, "down"],
}

clock = pygame.time.Clock()
Q = queue.Queue(maxsize=10)

# ---------------- Fuentes ----------------
font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# ---------------- MODIFICACIÓN 1: imagen PNG para los segmentos ----------------
try:
    snake_image = pygame.image.load("01_image.png").convert()
    snake_image = pygame.transform.scale(snake_image, (snakeblock, snakeblock))
    snake_image.set_colorkey(pink)
except FileNotFoundError:
    snake_image = pygame.Surface((snakeblock, snakeblock))
    snake_image.fill(blue)

# ---------------- MODIFICACIÓN 2: imagen PNG para el fondo ----------------
try:
    bgd_image = pygame.image.load("background.png").convert()
    bgd_image = pygame.transform.scale(bgd_image, (diswidth, disheight))
except FileNotFoundError:
    bgd_image = pygame.Surface((diswidth, disheight))
    bgd_image.fill(black)


def yourscore(score):
    value = score_font.render(f"Score: {score}", True, yellow)
    dis.blit(value, [0, 0])


def oursnake(snakeblock, snakelist):
    # Cada segmento se dibuja con la imagen PNG (antes era un rectángulo negro)
    for x in snakelist:
        dis.blit(snake_image, (x[0], x[1]))


def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [diswidth / 10, disheight / 1.2])


def random_food():
    # Posición aleatoria alineada a la cuadrícula de bloques
    foodx = random.randrange(0, diswidth - snakeblock + 1, snakeblock)
    foody = random.randrange(0, disheight - snakeblock + 1, snakeblock)
    return foodx, foody


def gameLoop():
    game_over = False
    game_close = False

    # Limpiar movimientos pendientes en la cola al iniciar/reiniciar
    while not Q.empty():
        Q.get_nowait()

    direction = ""

    x1 = diswidth // 2
    y1 = disheight // 2
    x1_change = 0
    y1_change = 0

    snakelist = []
    snakelength = 1

    foodx, foody = random_food()

    while not game_over:

        # ---- Pantalla de "perdiste" ----
        while game_close:
            dis.blit(bgd_image, (0, 0))  # MODIFICACIÓN 2: fondo PNG también aquí
            message("You lost! Press Q to quit or C to play again", red)
            yourscore(snakelength - 1)
            pygame.display.update()

            for event in pygame.event.get():
                # MODIFICACIÓN 3: atender el botón de cerrar la ventana al perder
                if event.type == pygame.QUIT:
                    game_over = True
                    game_close = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()
                        return

        # ---- Eventos del juego ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                try:
                    if event.key == pygame.K_LEFT and direction != "right":
                        Q.put_nowait("left")
                    elif event.key == pygame.K_RIGHT and direction != "left":
                        Q.put_nowait("right")
                    elif event.key == pygame.K_UP and direction != "down":
                        Q.put_nowait("up")
                    elif event.key == pygame.K_DOWN and direction != "up":
                        Q.put_nowait("down")
                except queue.Full:
                    pass

        # ---- Procesar la cola de instrucciones ----
        if not Q.empty():
            next_command = Q.get()
            if next_command == "left" and direction != "right":
                x1_change, y1_change, direction = compass["left"]
            elif next_command == "right" and direction != "left":
                x1_change, y1_change, direction = compass["right"]
            elif next_command == "up" and direction != "down":
                x1_change, y1_change, direction = compass["up"]
            elif next_command == "down" and direction != "up":
                x1_change, y1_change, direction = compass["down"]

        # ---- Actualizar posición ----
        x1 += x1_change
        y1 += y1_change

        # ---- Choque con las paredes ----
        if x1 >= diswidth or x1 < 0 or y1 >= disheight or y1 < 0:
            game_close = True
            continue

        # ---- Dibujar ----
        dis.blit(bgd_image, (0, 0))  # MODIFICACIÓN 2: fondo PNG
        pygame.draw.rect(dis, green, [foodx, foody, snakeblock, snakeblock])

        snakehead = [x1, y1]
        snakelist.append(snakehead)
        if len(snakelist) > snakelength:
            del snakelist[0]

        # ---- Choque con el propio cuerpo ----
        for x in snakelist[:-1]:
            if x == snakehead:
                game_close = True

        oursnake(snakeblock, snakelist)
        yourscore(snakelength - 1)
        pygame.display.update()

        # ---- Comer ----
        if x1 == foodx and y1 == foody:
            foodx, foody = random_food()
            snakelength += 1

        clock.tick(snakespeed)

    pygame.quit()


if __name__ == "__main__":
    gameLoop()