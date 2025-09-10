import pygame
import math
import os
import random

pygame.init()
pygame.mixer.init()

cursor = pygame.image.load(os.path.join('images', 'Cosmic_Conquest', 'Crusader',"cursor.png"))
#pygame.mixer.music.load("game_music\\crusader_theme.mp3")
#laser_sound = pygame.mixer.Sound(os.path.join("game_music", "sound_effects", "laser_sound.wav"))

WIDTH, HEIGHT = 500, 500
FPS = 60
MAX_BULLETS = float('inf')

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, screen):
        screen.blit(self.sprite, self.rect.topleft)

class Bullet(Object):
    def __init__(self, x, y, dx, dy):
        super().__init__(x, y, 10, 5)
        self.dx = dx
        self.dy = dy
        self.collided = False
        self.distance = 0
        self.image.fill((255, 255, 255))
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.sprite = pygame.transform.rotate(self.image, self.angle)
        self.mask = pygame.mask.from_surface(self.sprite)

    def move(self, speed):
        self.rect.x += self.dx * speed
        self.rect.y += self.dy * speed

        self.distance += math.sqrt(self.dx**2 + self.dy**2) * speed

class Asteroid(Object):
    def __init__(self, shooterx, shootery, x, y, type):
        self.asteroid_images = {"small" : [pygame.image.load(os.path.join('images', 'Cosmic_Conquest', 'Crusader', 'crusader_small_asteroid.png')), (64, 64)], 
                   "medium" : [pygame.image.load(os.path.join('images', 'Cosmic_Conquest', 'Crusader', 'crusader_medium_asteroid.png')), (64, 64)],
                   "large" : [pygame.image.load(os.path.join('images', 'Cosmic_Conquest', 'Crusader', 'crusader_big_asteroid.png')), (64, 64)]}
        
        super().__init__(x, y, self.asteroid_images[type][1][0], self.asteroid_images[type][1][1])
        self.type = type
        self.health = ["small", "medium", "large"].index(type) + 1
        self.sprite = pygame.transform.scale(self.asteroid_images[type][0], (self.asteroid_images[type][1]))
        self.mask = pygame.mask.from_surface(self.image)

        self.dx, self.dy = shooterx - x, shootery - y
        self.vector = math.sqrt(self.dx**2 + self.dy**2)
        self.speed = 5 - (self.health)
        if self.vector:
            self.vel_x = (self.dx / self.vector) * self.speed
            self.vel_y = (self.dy / self.vector) * self.speed
        else:
            self.vel_x = 0
            self.vel_y = 0

    def collided(self, asteroids, asteroid):
        if self.type == "medium":
            self.type = "small"
        elif self.type == "large":
            self.type = "medium"
        elif self.type == "small" and asteroid in asteroids:
            asteroids.remove(asteroid)

        return asteroids

    def update_mask(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_img(self):
        self.type = ["small", "medium", "large"][self.health - 1]
        self.sprite = pygame.transform.scale(self.asteroid_images[self.type][0], (self.asteroid_images[self.type][1]))

    def move(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.update_mask()

class Shooter(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        shooter = pygame.transform.scale(pygame.image.load(os.path.join('images', 'Cosmic_Conquest', 'Player', "spaceship.png")), (32, 32))
        self.image.blit(shooter, (0,0))
        self.mask = pygame.mask.from_surface(self.image)
        self.x_vel = 0
        self.y_vel = 0
        self.VEL = 3
        self.invincible = False
        self.health = 3
        self.invincible_ticks = 0
        self.score = 0

    def update_mask(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def update_pos(self, xvel, yvel):
        self.rect.x += xvel
        self.rect.y += yvel

    def health_bar(self):
        for i in range(3):
            if i < self.health:
                screen.blit(pygame.image.load(os.path.join('images', 'Cosmic_Conquest', 'Player', 'health_point.png')), ((i * 50) + 300, 0 - 40))
            else:
                screen.blit(pygame.image.load(os.path.join('images', 'Cosmic_Conquest', 'Player', 'health_dead.png')), ((i * 50) + 300, 0 - 40))

    def move(self):
        keys = pygame.key.get_pressed()
        self.x_vel = 0
        self.y_vel = 0

        self.rect.x, self.rect.y = switch_sides(self.rect, self.image.get_width(), self.image.get_height())

        if keys[pygame.K_d]:
            self.x_vel += self.VEL
        if keys[pygame.K_a]:
            self.x_vel -= self.VEL
        if keys[pygame.K_w]:
            self.y_vel -= self.VEL
        if keys[pygame.K_s]:
            self.y_vel += self.VEL

    def point(self, dy, dx):
        self.angle = int(math.degrees(math.atan2(-dy, dx)))
        rotated_shooter = pygame.transform.rotate(self.image, self.angle)
        self.sprite = rotated_shooter
        self.update_mask()

def spawn_off_screen():
    side_coordinates = {
        'top': (random.randint(100, 500), -50),
        'bottom': (random.randint(100, 500), 650),
        'left': (-50, random.randint(100, 500)),
        'right': (850, random.randint(100, 500))
    }
    side = random.choice(['top', 'bottom', 'left', 'right'])
    x, y = side_coordinates[side]
    return (x, y)

def switch_sides(rect, width, height):
    if rect.right <= 0:
        rect.x = WIDTH
    elif rect.left >= WIDTH:
        rect.x = -width
    if rect.bottom <= 0:
        rect.y = HEIGHT
    elif rect.top >= HEIGHT:
        rect.y = -height

    return rect.x, rect.y

def check_collision(bullets, asteroids, shooter):
    bullets_remove = []
    for asteroid in asteroids:
        for bullet in bullets:
            if pygame.sprite.collide_mask(bullet, asteroid):
                bullets_remove.append(bullet)
                asteroid.health -= 1
                asteroids = asteroid.collided(asteroids, asteroid)
                shooter.score += random.randint(3, 5)

        if pygame.sprite.collide_mask(asteroid, shooter) and not shooter.invincible:
            shooter.invincible = True
            ast_xvel, ast_yvel = (asteroid.rect.centerx - shooter.rect.centerx) // 10, (asteroid.rect.centery - shooter.rect.centery) // 10
            asteroid.vel_x, asteroid.vel_y = (shooter.x_vel + ast_xvel), (shooter.y_vel + ast_yvel)
            shooter.rect.x, shooter.rect.y = shooter.rect.x - asteroid.vel_x, shooter.rect.y - asteroid.vel_y
            asteroid.health -= 1
            asteroids = asteroid.collided(asteroids, asteroid)

            shooter.health -= 1

    for bullet in bullets_remove:
        if bullet in bullets:
            bullets.remove(bullet)
    return bullets, shooter, asteroids

def movement(bullets, shooter, asteroids):
    shooter.move()
    for bullet in bullets:
        bullet.move(6)

        if bullet.distance >= 250:
            bullets.remove(bullet)

    for asteroid in asteroids:
        asteroid.move()
        switch_sides(asteroid.rect, asteroid.image.get_width(), asteroid.image.get_height())

def handle_level(ast_num, level, wave, levels, asteroids, asteroid_ticks, last_tick, shooterx, shootery):
    if ast_num < levels["waves"][level][wave] and asteroid_ticks - last_tick >= levels["delay"]:
        ast_num += 1
        random_coords = spawn_off_screen()
        asteroids.append(Asteroid(shooterx, shootery, random_coords[0], random_coords[1], random.choice(["small", "medium", "large"])))
        last_tick = asteroid_ticks
    elif ast_num == levels["waves"][level][wave]:
        ast_num = 0
        wave += 1
    if wave == len(levels["waves"][level]):
        wave = 0
        level += 1
    return level, wave, ast_num, asteroids, last_tick

def game_over(screen, font, color, shooter, cursor, mousex, mousey, bullets, asteroids):
    text = font.render("Game Over", True, color)
    shooter.rect.x, shooter.rect.y = WIDTH // 2, (HEIGHT //2) + 100
    draw(screen, shooter, cursor, mousex, mousey, bullets, asteroids)
    screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 2 - text.get_height() // 2))
    pygame.mouse.set_visible(True)
    pygame.display.update()
    pygame.time.delay(5000)
    return False

def draw(screen, shooter, cursor, mousex, mousey, bullets, asteroids):
    pygame.mouse.set_visible(False)
    screen.fill((255, 155, 50)) 
    screen.blit(cursor, (mousex - cursor.get_width() // 2, mousey - cursor.get_height() // 2))
    shooter.point(mousex - shooter.rect.centerx, shooter.rect.centery - mousey)
    shooter.draw(screen)

    font = pygame.font.Font("fonts\\pixel_font-1.ttf", 30)
    text = font.render(f"Score - {shooter.score}", True, (0, 0, 0))

    screen.blit(text, (10, 0))

    if shooter.invincible and shooter.invincible_ticks < FPS * 3:
        shooter.invincible_ticks += 1

    elif shooter.invincible_ticks >= FPS * 3:
        shooter.invincible = False
        shooter.invincible_ticks = 0
        shooter.image.set_alpha(255)

    for bullet in bullets:
        bullet.draw(screen)

    for asteroid in asteroids:
        asteroid.draw(screen)
        asteroid.update_img()

    shooter.health_bar()

def main(screen):
    shooter = Shooter(WIDTH//2, HEIGHT//2, 32, 32)
    last_tick = 0
    asteroid_num = 0
    level = 0
    wave = 0
    levels = {"delay" : 2000, "waves" : [[5, 7, 10], [7, 10, 13], [10, 20, 30], [50, 100]]}
    alpha = 0

    bullets = []
    asteroids = []
    running = True

    while running:
        pygame.display.set_caption(f"Cosmic Conquest - Crusader - {str(int(clock.get_fps()))}")
        clock.tick(FPS)

        if shooter.invincible:
            if alpha <= 0:
                alpha_x = 5
            elif alpha >= 255:
                alpha_x = -5
            alpha += alpha_x
            shooter.image.set_alpha(alpha)

        if shooter.health <= 0:
            running = game_over(screen, pygame.font.Font("fonts\\pixel_font-1.ttf", 60), (0, 0, 0), shooter, cursor, mousex, mousey, bullets, asteroids)
        
        asteroid_ticks = pygame.time.get_ticks()
        mousex, mousey = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and len(bullets) < MAX_BULLETS:
                dx, dy = mousex - shooter.rect.centerx, shooter.rect.centery - mousey
                bullet_dx, bullet_dy = math.cos(math.atan2(dy, dx)), -math.sin(math.atan2(dy, dx))
                bullets.append(Bullet(shooter.rect.centerx, shooter.rect.centery, bullet_dx, bullet_dy))

        bullets, shooter, asteroids = check_collision(bullets, asteroids, shooter)
        movement(bullets, shooter, asteroids)
        level, wave, asteroid_num, asteroids, last_tick = handle_level(asteroid_num, level, wave, levels, asteroids, asteroid_ticks, last_tick, shooter.rect.x, shooter.rect.y)
        shooter.update_pos(shooter.x_vel, shooter.y_vel)
        draw(screen, shooter, cursor, mousex, mousey, bullets, asteroids)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main(screen)