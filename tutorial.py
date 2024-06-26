import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 1600, 800
FPS = 60
PLAYER_VEL = 5
PLAYER1_VEL = 4

window = pygame.display.set_mode((WIDTH, HEIGHT))


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))

        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.original_x = x  # Store the original x position
        self.original_y = y  # Store the original y position
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.life = 3  # Player's life
        self.max_life = 3  # Maximum life
        self.heart_sprite = pygame.image.load(join("assets", "Heart.png")).convert_alpha()
        self.heart_empty_sprite = pygame.image.load(join("assets", "heart_empty.png")).convert_alpha()
        self.invulnerability_duration = FPS * 1  # 1 second invulnerability duration
        self.invulnerability_timer = 0  # Timer to track remaining invulnerability time


        # Initialize hearts display
        self.update_hearts()

    def update_hearts(self):
        heart_spacing = 10
        self.hearts = []  # List to store heart images
        for i in range(self.max_life):
            heart_x = WIDTH - 130 - (i * (self.heart_sprite.get_width() + heart_spacing))
            heart_y = 10
            if i < self.life:
                self.hearts.append((self.heart_sprite, (heart_x, heart_y)))
            else:
                self.hearts.append((self.heart_empty_sprite, (heart_x, heart_y)))

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def make_hit(self):
        if self.invulnerability_timer == 0:  # Check if player is not in invulnerable phase
            self.hit = True
            self.invulnerability_timer = self.invulnerability_duration  # Set invulnerability timer
            
    def loop(self, fps):
    # Apply gravity
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
    # Move the player
        self.move(self.x_vel, self.y_vel)

    # Check if the player is hit
        if self.hit:
            self.hit_count += 1
    # Check if the hit cooldown has expired
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

            
    # Increase fall count
        self.fall_count += 1

    # Decrease invulnerability timer if player is in invulnerable phase
        if self.invulnerability_timer > 0:
            self.invulnerability_timer -= 1

    # Update player sprite
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))
        self.draw_hearts(win)

    def draw_hearts(self, win):
        heart_sprite = pygame.image.load(join("assets", "Heart.png")).convert_alpha()
        heart_empty_sprite = pygame.image.load(join("assets", "heart_empty.png")).convert_alpha()
        heart_spacing = 10
        for i in range(self.max_life):
            heart_x = WIDTH - 130 - (i * (heart_sprite.get_width() + heart_spacing))
            heart_y = 10
            if i < self.life:
                win.blit(heart_sprite, (heart_x, heart_y))
            else:
                # Draw empty heart for remaining life
                win.blit(heart_empty_sprite, (heart_x, heart_y))


class Player1(pygame.sprite.Sprite):
    COLOR = (0, 255, 0)  # Green color
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "NinjaFrog", 32, 32, True)  # Assuming sprite sheets are similar to Player
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.original_x = x  # Store the original x position
        self.original_y = y  # Store the original y position
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "right"  # Default direction
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.move_delay = FPS * 2  # 2 seconds delay before changing direction
        self.move_timer = 0
        self.saved_direction = self.direction  # Store the initial direction

    def reset(self):
        self.rect.x = self.original_x
        self.rect.y = self.original_y
        self.x_vel = 0
        self.y_vel = 0
        self.direction = self.saved_direction  # Restore the initial direction
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.move_timer = 0


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

        # Update move timer
        self.move_timer += 1

        # Check if it's time to change direction
        if self.move_timer >= self.move_delay:
            self.move_timer = 0
            if self.direction == "left":
                self.move_right(PLAYER1_VEL)
            else:
                self.move_left(PLAYER1_VEL)

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("assets", "Background", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image


def draw(window, background, bg_image, players, objects, offset_x):
    for tile in background:
        window.blit(bg_image, tile)

    for obj in objects:
        obj.draw(window, offset_x)

    for player in players:
        player.draw(window, offset_x)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, objects):
    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()


def handle_move_player1(player1, objects):
    # Update movement based on direction and delay
    if player1.direction == "left":
        if player1.move_timer >= player1.move_delay:
            player1.move_timer = 0
            player1.move_right(PLAYER1_VEL)
        else:
            player1.move_left(PLAYER1_VEL)
    elif player1.direction == "right":
        if player1.move_timer >= player1.move_delay:
            player1.move_timer = 0
            player1.move_left(PLAYER1_VEL)
        else:
            player1.move_right(PLAYER1_VEL)

    # Update movement timer
    player1.move_timer += 0.3

    # Handle collisions
    player1.x_vel = 0
    collide_left = collide(player1, objects, -PLAYER1_VEL * 1)
    collide_right = collide(player1, objects, PLAYER1_VEL * 1)

    if not collide_left and player1.direction == "left":
        player1.move_left(PLAYER1_VEL)
    if not collide_right and player1.direction == "right":
        player1.move_right(PLAYER1_VEL)

    vertical_collide = handle_vertical_collision(player1, objects, player1.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "fire":
            player1.make_hit()


def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Blue.png")

    block_size = 96

    player = Player(-1500, 500, 50, 50)
    player1_positions = [(-900, -100), (192,200), (1050, 100),(1718,100),(2310,100)]  # Define positions for Player1
    players1 = [Player1(x, y, 50, 50) for x, y in player1_positions]  # Create Player1 instances

    fire = Fire(100, HEIGHT - block_size - 64, 16, 32)
    fire.on()

    

    floor = [
        *[
            Block(i * block_size, HEIGHT - block_size, block_size)
            for i in range(-(WIDTH // block_size), (WIDTH * 2) // block_size)
        ],
        *[
            Block(x, HEIGHT - block_size - y, block_size)
            for x, y in [(-1100, 210), (-800, 400), (-895, 400), (-705, 400), (-610, 400), (192, 288), (384, 288),
                          (480, 288),(2120,260),(2120,355),(2215,260),(2215,355),(2215,450),(2120,450),(2400,96),(2496,96),(2496,192),(2592,96),(2592,192),(2592,288),
                          (2688,96),(2688,192),(2688,288),(2688,384),(2784,96),(2784,192),(2784,288),(2784,384),(2784,480),(2880,96),(2880,192),(2880,288),(2880,384),(2880,480),(2976,96),(2976,192),(2976,288),(2976,384),(2976,480)]
        ]
    ]
 # Define the coordinates of blocks to delete
    blocks_to_delete = [(480,0),(384,0),(192,0),(288,0),(864,0),(768,0),(960,0),(1440,0),(1536,0),(1632,0)]

    # Remove blocks at specified coordinates from the floor
    for x, y in blocks_to_delete:
        for block in floor[:]:  # Use floor[:] to create a copy of the list to iterate over
            if block.rect.x == x and block.rect.y == HEIGHT - block_size - y:
                floor.remove(block)
    objects = [*floor, Block(0, HEIGHT - block_size * 2, block_size),
               Block(block_size * 3, HEIGHT - block_size * 4, block_size), fire]
    
    offset_x = 0  # Initialize offset_x to 0
    scroll_area_width = 500

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()

        # Update player and player1 positions
        player.loop(FPS)
        for player1 in players1:
            player1.loop(FPS)

        fire.loop()

        # Handle player movement
        handle_move(player, objects)
        for player1 in players1:
            handle_move_player1(player1, objects)

        # Collision detection with Player1
        for player1 in players1:
            # Check if player collides with player1 on the sides (x-axis)
            if pygame.sprite.collide_rect(player, player1):
                if player.rect.right >= player1.rect.left or player.rect.left <= player1.rect.right:
                    # Check if player is in invulnerable phase
                    if player.invulnerability_timer == 0:
                # Player is vulnerable, apply hit
                        player.make_hit()
                        player.life -= 1
                        if player.life <= 0:
                    # Game over logic here
                            pass
                # Set invulnerability timer
                player.invulnerability_timer = player.invulnerability_duration

                        

            # Check if player collides with player1 on top (y-axis)
            if player.rect.bottom <= player1.rect.top and pygame.sprite.collide_rect(player, player1):
                # Remove player1 from the list of players
                players1.remove(player1)
        # Update offset_x based on player's position
        if player.rect.x > offset_x + scroll_area_width:
            offset_x = player.rect.x - scroll_area_width
        elif player.rect.x < offset_x:
            offset_x = player.rect.x

        # Draw everything
        draw(window, background, bg_image, [player, *players1], objects, offset_x)

        # Check if player is below the floor and reset if necessary
        if player.rect.y > HEIGHT:
            # Reset player position
            player.rect.x = player.original_x
            player.rect.y = player.original_y
            player.x_vel = 0
            player.y_vel = 0

            # Reset player life
            player.life = 3
            # Reset Player1 positions
            for player1 in players1:
                player1.reset()
# Update player's hearts display after reset
            player.update_hearts()

    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
