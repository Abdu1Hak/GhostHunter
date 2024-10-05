import pygame, sys, math, random
from pygame.math import Vector2

# Start Game
pygame.init()

# Windows
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption('Shooter Game')
clock = pygame.time.Clock()
game_active = True

# Background
tiles = pygame.transform.rotozoom(pygame.image.load('../Assets/Floor Tile.png').convert(), 0, 2)
tile_size = 32*2

# Score
global_score = 0
score_font = pygame.font.Font('../Audio & Font/PoetsenOne-Regular.ttf', 28)
game_font = pygame.font.Font('../Audio & Font/PoetsenOne-Regular.ttf', 40)
retry_font = pygame.font.Font('../Audio & Font/PoetsenOne-Regular.ttf', 18)

# Music
bg_music = pygame.mixer.Sound('../Audio & Font/Ghost House.mp3')
bg_music.play(loops=-1)
# -1 means play Sound forever
bg_music.set_volume(0.2)


class Shooter(pygame.sprite.Sprite):
    # Both Constructors
    def __init__(self):
        super().__init__()

        # Every Class Object Requires an Image + Position
        self.image = pygame.transform.rotozoom(pygame.image.load('../Assets/Hunter.png').convert_alpha(), 0, 0.42)
        self.pos = Vector2(80, 80)
        self.speed = 5

        # Intro to Rotation and Rects
        self.copy_image = self.image
        self.rect = self.image.get_rect(center=self.pos)
        self.collision_rect = self.rect.copy()

        # Shoot
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_offset = Vector2(40, 17.25)

        # Sound
        self.shoot_sound = pygame.mixer.Sound('../Audio & Font/Gunshot.wav')
        self.shoot_sound.set_volume(0.2)


    def inputs(self):

        # Velocity = Change of Speed
        self.velocity_x = 0
        self.velocity_y = 0

        # Movement via Keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed

        # Fix diagonal Issue
        if self.velocity_y != 0 and self.velocity_x != 0:
            self.velocity_y /= math.sqrt(2)
            self.velocity_x /= math.sqrt(2)

        # Press to Shoot
        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shooting()
            self.shoot = True
        else:
            self.shoot = False

    def check_boundaries(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1280:
            self.rect.right = 1280
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > 720:
            self.rect.bottom = 720

    def shooting(self):
        # Implement Cooldown
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 40


            # Create Spawn + Offset for Bullet - Vector2()
            # Rotate the Vector2 values by dsdadadaa given angle in degrees
            spawn = self.pos + self.gun_offset.rotate(self.angle)

            # Create Instance and Call the Class with it Arguments
            self.bullet = Bullet(spawn.x, spawn.y, self.angle)
            self.shoot_sound.play()
            bullet_sprite.add(self.bullet)
            all_sprites.add(self.bullet)

    def rotations(self):

        # Get coordinates of Shooter and Mouse Cursor
        mouse_cords = pygame.mouse.get_pos()

        # Find Difference in Cords
        difference_in_x = (mouse_cords[0] - self.collision_rect.centerx)
        difference_in_y = (mouse_cords[1] - self.collision_rect.centery)

        # Find angle
        self.angle = math.degrees(math.atan2(difference_in_y, difference_in_x))
        # Implement Angle
        self.image = pygame.transform.rotate(self.copy_image, -self.angle)
        # Update Rect
        self.rect = self.image.get_rect(center=self.pos)

    def move(self):

        self.pos += self.velocity_x, self.velocity_y

        # reason why self.image is blit on self.rect
        self.rect.center = self.pos
        self.collision_rect.center = self.pos

    def you_lose(self):

        global game_active
        for enemy in enemy_group:
            if self.collision_rect.colliderect(enemy.rect):
                game_active = False

    def update(self):
        self.inputs()
        self.move()
        self.rotations()
        self.check_boundaries()
        self.you_lose()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 2


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()

        # X and Y Values will be passed into the Shooter Class
        self.image = pygame.image.load('../Assets/Bullet.png').convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))

        # Logistics
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10

        # Bullet Velocity - CAH for Horizontal and SOH for vertical
        self.horizontal_velocity = math.cos(self.angle * (2*math.pi/360)) * self.speed
        self.vertical_velocity = math.sin(self.angle * (2 * math.pi / 360)) * self.speed

        # Bullet Lifetime
        self.bullet_life = 750
        self.spawn_time = pygame.time.get_ticks() # time when bullet is created

    def bullet_travel(self):
        # Update Bullet Positions
        self.x += self.horizontal_velocity
        self.y += self.vertical_velocity
        # update rect position to display on screen
        # initially a float, convert to an int
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Implement a Bullet Lifetime
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_life:
            self.kill()
            # kills bullet sprite

    def update(self):
        self.bullet_travel()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(enemy_group, all_sprites)

        # The Three Ghost Images
        self.ghost_1 = pygame.transform.rotozoom(pygame.image.load('../Assets/ghost 1.png'), 0, 0.2)
        self.ghost_2 = pygame.transform.rotozoom(pygame.image.load('../Assets/ghost 2.png'), 0, 0.2)
        self.ghost_3 = pygame.transform.rotozoom(pygame.image.load('../Assets/ghost 3.png'), 0, 0.2)

        # Images, Indexes and Rects
        self.images = [self.ghost_1, self.ghost_2, self.ghost_3]
        self.image_index = 0
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=pos)
        self.position = Vector2(pos)

        self.direction = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.speed = 5

        # Time for animations
        self.clock_one = pygame.time.get_ticks()
        self.animate_time = 200

        # Sound
        self.ghost_sound = pygame.mixer.Sound('../Audio & Font/Kill.mp3')
        self.ghost_sound.set_volume(0.2)

    def check_collision(self):
        # Mention the Global Score
        global global_score

        for sprite in bullet_sprite:
            if self.rect.colliderect(sprite):
                self.kill()
                self.randomise_spawn()
                self.ghost_sound.play()
                global_score += 1

    def randomise_spawn(self):

        spawns = [(-20, 180),(-20, 360),(-20, 540), (-20, 720),
                (1300, 180), (1300, 360), (1300, 540), (1300, 720),
                (320, -20), (640, -20), (960, -20), (1280,-20),
                (320, 740), (640, 740), (960, 740), (1280, 740)]
        new_enemy = Enemy(spawns[random.randint(0,15)])
        # Make sure to add the upcoming ghost into the enemy group

    def hunt(self):

        player_vector = Vector2(shooter.rect.center)
        enemy_vector = Vector2(self.rect.center)
        distance = self.get_vector_distance(player_vector, enemy_vector)

        if distance > 0:
            self.direction = (player_vector - enemy_vector).normalize()
            # by normalizing the direction, you ensure that the direction is a 1 unit length
        else:
            self.direction = Vector2(0, 0)

        # by multiplying the normalized direction with speed, you normalize the velocity vector
        self.velocity = self.direction * self.speed

        # Update Enemy position by speed
        self.position += self.velocity
        self.rect.centerx = self.position.x
        self.rect.centery = self.position.y

    def get_vector_distance(self, vector1, vector2):
        return (vector1 - vector2).magnitude()
        # .magnitude() gets the length of the vector

    def animate_ghost(self):

        clock_two = pygame.time.get_ticks()
        if clock_two - self.clock_one > self.animate_time:
            self.clock_one = clock_two

            if self.image_index >= len(self.images) - 1 :
                self.image_index = 0
            else:
                self.image_index += 1

            self.image = self.images[self.image_index]
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        if game_active:
            self.hunt()
            self.check_collision()
            self.animate_ghost()


# Sprites
all_sprites = pygame.sprite.Group()
bullet_sprite = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()

# Instances
shooter = Shooter()
all_sprites.add(shooter)
enemy = Enemy((1300, 800))

def draw_score():

    score_text = global_score
    score_surface = score_font.render(f'Kills: {score_text}', True, (0,0,0))
    score_rect = score_surface.get_rect(center = (1170,50))

    ghost_surface = pygame.transform.rotozoom(pygame.image.load('../Assets/ghost 1.png'), 0, 0.1)
    ghost_rect = ghost_surface.get_rect(center=(1240,50))

    screen.blit(score_surface, score_rect)
    screen.blit(ghost_surface, ghost_rect)
    return score_text


def draw_map():
    # Calculate the number of tiles needed to cover the screen
    tiles_x = screen.get_width() // tile_size + 1
    tiles_y = screen.get_height() // tile_size + 1
    # +1 accounts for full coverage

    # Loop over number of tiles and draw them
    for x in range(tiles_x):
        for y in range(tiles_y):
            screen.blit(tiles, (x*tile_size, y*tile_size))


def reset_game():

    # Reset Player Stats
    global global_score, game_active
    global_score = 0
    game_active = True

    # Empty out all objects
    all_sprites.empty()
    enemy_group.empty()
    bullet_sprite.empty()

    # Add Shooter back and random spawn
    all_sprites.add(shooter)
    enemy.randomise_spawn()


# Event Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                reset_game()

    if game_active:
        # Draw
        draw_map()
        draw_score()
        all_sprites.draw(screen)
        # Update All Sprites
        all_sprites.update()

    else:

        screen.fill((0,0,0))
        you_lose_text = 'Game Over'
        you_lose_surface = game_font.render(you_lose_text, True, 'White')
        you_lose_rect = you_lose_surface.get_rect(center = (640, 324))
        screen.blit(you_lose_surface, you_lose_rect)

        score_text = global_score
        score_surface = score_font.render(f'Total Kills: {score_text}', True, "White")
        score_rect = score_surface.get_rect(center=(640, 400))
        screen.blit(score_surface, score_rect)

        retry_text = "Press 'r' to restart: "
        retry_surface = retry_font.render(retry_text, True, "White")
        retry_rect = retry_surface.get_rect(center=(640, 680))
        screen.blit(retry_surface, retry_rect)

    # Finish Line = update + fps
    pygame.display.flip()
    clock.tick(120)


























    # 400 LINES !!!!