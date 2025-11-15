import pygame.image
from pygame import *
import socket
import json
from threading import Thread
from pygame import mixer
mixer.init()

# ---ПУГАМЕ НАЛАШТУВАННЯ ---
WIDTH, HEIGHT = 800, 600
init()
screen = display.set_mode((WIDTH, HEIGHT))
clock = time.Clock()
display.set_caption("Пінг-Понг")
# ---СЕРВЕР ---
def connect_to_server():
    while True:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(('localhost', 8080)) # ---- Підключення до сервера
            buffer = ""
            game_state = {}
            my_id = int(client.recv(24).decode())
            return my_id, game_state, buffer, client
        except:
            pass


def receive():
    global buffer, game_state, game_over
    while not game_over:
        try:
            data = client.recv(1024).decode()
            buffer += data
            while "\n" in buffer:
                packet, buffer = buffer.split("\n", 1)
                if packet.strip():
                    game_state = json.loads(packet)
        except:
            game_state["winner"] = -1
            break

# --- ШРИФТИ ---
font_win = font.Font(None, 72)
font_main = font.Font(None, 36)
# --- ЗОБРАЖЕННЯ ----
background = pygame.image.load("R.png.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
ball_img = pygame.image.load("ball.png")
ball_img = pygame.transform.scale(ball_img, (40, 40))
paddle1_img = pygame.image.load("11.png")
paddle1_img = pygame.transform.scale(paddle1_img, (20,100))
paddle2_img = pygame.image.load("22.png")
paddle2_img = pygame.transform.scale(paddle2_img, (20,100))
background_wait = pygame.image.load("waiting_bg.png")
background_wait = pygame.transform.scale(background_wait, (WIDTH, HEIGHT))
win_bg = pygame.image.load("win_bg.png")
lose_bg = pygame.image.load("lose_bg.png")
win_bg = pygame.transform.scale(win_bg, (WIDTH, HEIGHT))
lose_bg = pygame.transform.scale(lose_bg, (WIDTH, HEIGHT))

# --- ЗВУКИ ---


# --- ГРА ---
game_over = False
winner = None
you_winner = None
my_id, game_state, buffer, client = connect_to_server()
Thread(target=receive, daemon=True).start()
mixer.init()
if my_id == 0:
    mixer.music.load("game_music.mp3")
    mixer.music.play(-1)
    mixer.music.set_volume(0.5)
    sound_lose = mixer.Sound("lose.mp3")
while True:
    for e in event.get():
        if e.type == QUIT:
            exit()

    if "countdown" in game_state and game_state["countdown"] > 0:
        screen.fill((0, 0, 0))
        countdown_text = font.Font(None, 72).render(str(game_state["countdown"]), True, (255, 255, 255))
        screen.blit(countdown_text, (WIDTH // 2 - 20, HEIGHT // 2 - 30))
        display.update()
        continue  # Не малюємо гру до завершення відліку

    if "winner" in game_state and game_state["winner"] is not None:
        screen.fill((20, 20, 20))

        if you_winner is None:  # Встановлюємо тільки один раз
            if game_state["winner"] == my_id:
                you_winner = True
            else:
                you_winner = False
                sound_lose.play()

        if "winner" in game_state and game_state["winner"] is not None:

            if you_winner is None:  # хто виграв — визначаємо один раз
                you_winner = (game_state["winner"] == my_id)

            if you_winner:
                screen.blit(win_bg, (0, 0))
            else:
                screen.blit(lose_bg, (0, 0))

        text = font_win.render("K - рестарт", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
        screen.blit(text, text_rect)

        display.update()
        continue  # Блокує гру після перемоги


    if game_state:
        screen.blit(background, (0, 0))
        screen.blit(paddle1_img, (20, game_state['paddles']['0']))
        screen.blit(paddle2_img, (WIDTH - 40, game_state['paddles']['1']))
        screen.blit(ball_img, (game_state['ball']['x'] - 10, game_state['ball']['y'] - 10))
        score_text = font_main.render(f"{game_state['scores'][0]} : {game_state['scores'][1]}", True, (0, 180, 255))
        screen.blit(score_text, (WIDTH // 2 -25, 20))

    else:
        screen.blit(background_wait, (0, 0))

    display.update()
    clock.tick(60)

    keys = key.get_pressed()
    if keys[K_w]:
        client.send(b"UP")
    elif keys[K_s]:
        client.send(b"DOWN")

