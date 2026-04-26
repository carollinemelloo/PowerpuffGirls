import pygame
import sys
import random
import math

pygame.init()

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 22)
font_big = pygame.font.SysFont("Arial", 50)


try:
    meninas = {
        "1": pygame.image.load("assets/florzinha.png").convert_alpha(),
        "2": pygame.image.load("assets/lindinha.png").convert_alpha(),
        "3": pygame.image.load("assets/docinho.png").convert_alpha()
    }
    professor_img = pygame.image.load("assets/professor.png").convert_alpha()
    enemy_img = pygame.image.load("assets/ele.png").convert_alpha()
    boss_img = pygame.image.load("assets/macacolouco.png").convert_alpha()
except:
    print("Erro ao carregar imagens!")
    sys.exit()

def resize(img, escala):
    w, h = img.get_size()
    return pygame.transform.scale(img, (int(w * escala), int(h * escala)))

for k in meninas:
    meninas[k] = resize(meninas[k], 0.3)

professor_img = resize(professor_img, 0.3)
enemy_img = resize(enemy_img, 0.3)
boss_img = resize(boss_img, 0.5)


def tela_selecao():
    while True:
        screen.fill((20, 20, 40))
        screen.blit(font.render("Escolha sua personagem (1,2,3)", True, (255,255,255)), (180,100))

        x_pos = [200, 350, 500]

        for i, key in enumerate(["1","2","3"]):
            img = meninas[key]
            screen.blit(img, img.get_rect(center=(x_pos[i], 300)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.unicode in ["1","2","3"]:
                    return meninas[event.unicode]

        pygame.display.flip()

player_base = tela_selecao()


mapa = []
for i in range(0, 2000, 100):
    mapa.append(pygame.Rect(i, 500, 100, 50))

mapa.append(pygame.Rect(600, 400, 100, 100))
mapa.append(pygame.Rect(900, 300, 100, 200))


def reset_game():
    return {
        "x": 200, "y": 200,
        "vida": 100,
        "fase": 1,
        "estado": "jogando",
        "bullets": [],
        "last_shot": 0,
        "enemies": [[random.randint(300,1800), random.randint(100,400), 20] for _ in range(5)],
        "boss_hp": 200,
        "boss_pos": [1000, 300],
        "dir": (1,0),
        "angulo": 0,
        "flip": False,
        "scale": 1.0,
        "boss_bullets": [],
        "boss_last_shot": 0,
    }

game = reset_game()


running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                game["flip"] = not game["flip"]

    keys = pygame.key.get_pressed()

    if keys[pygame.K_r]:
        game = reset_game()

    if game["estado"] != "jogando":
        screen.fill((10, 10, 20))

        if game["estado"] == "game_over":
            texto1 = font_big.render("GAME OVER", True, (255, 0, 0))
            texto2 = font.render("Pressione R para reiniciar", True, (255, 255, 255))

        elif game["estado"] == "vitoria":
            texto1 = font_big.render("VITÓRIA!", True, (0, 255, 0))
            texto2 = font.render("Pressione R para jogar novamente", True, (255, 255, 255))

        screen.blit(texto1, texto1.get_rect(center=(400, 260)))
        screen.blit(texto2, texto2.get_rect(center=(400, 320)))

        pygame.display.flip()
        clock.tick(60)
        continue


    if keys[pygame.K_z]:
        game["scale"] += 0.02
    if keys[pygame.K_x]:
        game["scale"] -= 0.02
        game["scale"] = max(0.2, game["scale"])

    dx, dy = 0,0
    if keys[pygame.K_a]: dx = -1
    if keys[pygame.K_d]: dx = 1
    if keys[pygame.K_w]: dy = -1
    if keys[pygame.K_s]: dy = 1

    if dx != 0 or dy != 0:
        length = math.hypot(dx, dy)
        game["dir"] = (dx/length, dy/length)

    new_x = game["x"] + dx * 5
    new_y = game["y"] + dy * 5

    player_rect_test = player_base.get_rect(center=(new_x, new_y))

    if not any(player_rect_test.colliderect(b) for b in mapa):
        game["x"] = new_x
        game["y"] = new_y

    if keys[pygame.K_q]: game["angulo"] += 5
    if keys[pygame.K_e]: game["angulo"] -= 5

    now = pygame.time.get_ticks()
    if keys[pygame.K_SPACE] and now - game["last_shot"] > 200:
        game["last_shot"] = now
        color = random.choice([(255,0,0),(0,255,0),(0,200,255),(255,255,0)])
        game["bullets"].append([game["x"], game["y"], game["dir"], color])

    cam_x = game["x"] - 400
    cam_y = game["y"] - 300

    player = pygame.transform.flip(player_base, game["flip"], False)
    player = pygame.transform.rotozoom(player, game["angulo"], game["scale"])
    player_rect = player.get_rect(center=(game["x"], game["y"]))

    screen.fill((15,15,30))

    # MAPA
    for bloco in mapa:
        pygame.draw.rect(screen, (100,60,30), (bloco.x - cam_x, bloco.y - cam_y, bloco.width, bloco.height))

    if game["fase"] == 1:

        prof_pos = (1500, 450)
        prof_rect = professor_img.get_rect(topleft=prof_pos)
        screen.blit(professor_img, (prof_pos[0]-cam_x, prof_pos[1]-cam_y))

        for enemy in game["enemies"][:]:
            dx = game["x"] - enemy[0]
            dy = game["y"] - enemy[1]
            dist = math.hypot(dx, dy)

            if dist != 0:
                enemy[0] += dx/dist * 2
                enemy[1] += dy/dist * 2

            enemy_rect = enemy_img.get_rect(topleft=(enemy[0], enemy[1]))

            if player_rect.colliderect(enemy_rect):
                game["vida"] -= 0.3
                game["vida"] = max(0, game["vida"])

            for bullet in game["bullets"][:]:
                if enemy_rect.collidepoint(bullet[0], bullet[1]):
                    game["enemies"].remove(enemy)
                    game["bullets"].remove(bullet)
                    break

            screen.blit(enemy_img, (enemy[0]-cam_x, enemy[1]-cam_y))

        if player_rect.colliderect(prof_rect):
            game["fase"] = 2

    elif game["fase"] == 2:

        dx = game["x"] - game["boss_pos"][0]
        dy = game["y"] - game["boss_pos"][1]
        dist = math.hypot(dx, dy)

        if dist != 0:
            game["boss_pos"][0] += dx/dist * 1.5
            game["boss_pos"][1] += dy/dist * 1.5

        if now - game["boss_last_shot"] > 1000:
            game["boss_last_shot"] = now

            if dist != 0:
                direcao = (dx/dist, dy/dist)
                game["boss_bullets"].append([
                    game["boss_pos"][0],
                    game["boss_pos"][1],
                    direcao
                ])

        boss_rect = boss_img.get_rect(center=game["boss_pos"])

        if player_rect.colliderect(boss_rect):
            game["vida"] -= 0.2
            game["vida"] = max(0, game["vida"])

        for bullet in game["bullets"][:]:
            if boss_rect.collidepoint(bullet[0], bullet[1]):
                game["boss_hp"] -= 8
                game["bullets"].remove(bullet)

        screen.blit(boss_img, (game["boss_pos"][0]-cam_x, game["boss_pos"][1]-cam_y))

        pygame.draw.rect(screen, (255,0,0), (200, 20, max(0, game["boss_hp"]), 12))

        for b in game["boss_bullets"][:]:
            b[0] += b[2][0] * 6
            b[1] += b[2][1] * 6

            if player_rect.collidepoint(b[0], b[1]):
                game["vida"] -= 1
                game["vida"] = max(0, game["vida"])
                game["boss_bullets"].remove(b)
                continue

            if b[0] < -100 or b[0] > 3000 or b[1] < -100 or b[1] > 3000:
                game["boss_bullets"].remove(b)
                continue

            pygame.draw.circle(screen, (255,100,100),
                               (int(b[0]-cam_x), int(b[1]-cam_y)), 6)

        if game["boss_hp"] <= 0:
            game["estado"] = "vitoria"

    if game["vida"] <= 0:
        game["estado"] = "game_over"

    for bullet in game["bullets"][:]:
        bullet[0] += bullet[2][0] * 8
        bullet[1] += bullet[2][1] * 8

        if bullet[0] < -100 or bullet[0] > 3000 or bullet[1] < -100 or bullet[1] > 3000:
            game["bullets"].remove(bullet)
            continue

        pygame.draw.circle(screen, bullet[3],
                           (int(bullet[0]-cam_x), int(bullet[1]-cam_y)), 4)

    screen.blit(player, player.get_rect(center=(400,300)))

    screen.blit(font.render(f"Vida: {int(game['vida'])}", True, (255,255,255)), (10,10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()