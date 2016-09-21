#!/usr/bin/env python3
"""Slide puzzle game using the Pygame library."""

import os
import sys
import random
import pygame as pg

# constants
TILES_PER_SIDE = 4
FPS = 30

SHUFFLE = 40

# colors
SILVER = (192, 192, 192)
GREY = (128, 128, 128)


class Board():
    """The Board object simulates a set of puzzle pieces, one of which is
    a blank."""

    def __init__(self):

        ids = list(range(TILES_PER_SIDE * TILES_PER_SIDE - 1))
        random.shuffle(ids)
        ids.append(TILES_PER_SIDE * TILES_PER_SIDE - 1)

        self.tiles = dict()
        for col in range(TILES_PER_SIDE):
            for row in range(TILES_PER_SIDE):
                self.tiles[(col, row)] = row * TILES_PER_SIDE + col

        self.blank_xy = (TILES_PER_SIDE - 1, TILES_PER_SIDE - 1)
        self.moves_list = []
        self.shuffle()

    def get_valid_moves(self):

        valid_moves = []

        if self.blank_xy[0] - 1 >= 0:
            valid_moves.append((self.blank_xy[0] - 1, self.blank_xy[1]))
        if self.blank_xy[0] + 1 < TILES_PER_SIDE:
            valid_moves.append((self.blank_xy[0] + 1, self.blank_xy[1]))
        if self.blank_xy[1] - 1 >= 0:
            valid_moves.append((self.blank_xy[0], self.blank_xy[1] - 1))
        if self.blank_xy[1] + 1 < TILES_PER_SIDE:
            valid_moves.append((self.blank_xy[0], self.blank_xy[1] + 1))

        return valid_moves

    def move_tile(self, xy):

        tile = self.tiles[xy]
        self.tiles[xy] = TILES_PER_SIDE * TILES_PER_SIDE - 1
        self.tiles[self.blank_xy] = tile
        self.blank_xy = xy

    def shuffle(self):

        previous_blank_xy = self.blank_xy
        moves_nb = 0
        while moves_nb < SHUFFLE or self.blank_xy != (TILES_PER_SIDE - 1, TILES_PER_SIDE - 1):
            valid_moves = self.get_valid_moves()
            if previous_blank_xy in valid_moves:
                valid_moves.pop(valid_moves.index(previous_blank_xy))
            previous_blank_xy = self.blank_xy
            move = random.choice(valid_moves)
            self.moves_list.append(move)
            self.move_tile(move)
            moves_nb += 1

    def is_game_won(self):

        for col in range(TILES_PER_SIDE):
            for row in range(TILES_PER_SIDE):
                if self.tiles[(col, row)] != ((row * TILES_PER_SIDE) + col):
                    return False

        return True


class Game():
    """The Game object wraps most of the program's functionalities."""

    def __init__(self):

        pg.init()
        self.image = pg.image.load(os.path.join("img", "01.png"))
        image_rect = self.image.get_rect()
        self.screen_width = image_rect.width
        self.screen_height = image_rect.height
        self.tile_width = self.screen_width // TILES_PER_SIDE
        self.tile_height = self.screen_height // TILES_PER_SIDE

        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        self.image.convert()
        pg.display.set_caption("PygSlidePuzzle")
        self.fps_clock = pg.time.Clock()
        self.font = pg.font.Font(None, 24)

        self.board = Board()
        self.tile_sprites = self.init_tile_sprites()

        self.running = True
        self.do_render = True
        self.command = None
        self.game_won = False

    def init_tile_sprites(self):

        DEBUG = True

        tile_sprites =[]
        for i in range(TILES_PER_SIDE * TILES_PER_SIDE - 1):
            tile_sprite = pg.sprite.Sprite()
            tile_sprite.image = pg.Surface((self.tile_width, self.tile_height))
            tile_sprite.rect = tile_sprite.image.get_rect()
            source_rect = ((i % TILES_PER_SIDE) * self.tile_width, (i // TILES_PER_SIDE) * self.tile_height, self.tile_width, self.tile_height)
            tile_sprite.image.blit(self.image, (0, 0), source_rect)
            tile_sprites.append(tile_sprite)

        # create the blank
        tile_sprite = pg.sprite.Sprite()
        tile_sprite.image = pg.Surface((self.tile_width, self.tile_height))
        tile_sprite.rect = tile_sprite.image.get_rect()
        tile_sprite.image.fill(GREY)
        tile_sprites.append(tile_sprite)

        return tile_sprites

    def event_get(self):

        if not self.game_won:
            for event in pg.event.get():

                if event.type == pg.QUIT:
                    self.running = False
                    return None

                if event.type == pg.KEYDOWN:

                    if event.key == pg.K_ESCAPE:
                        self.running = False
                        return None

                if event.type == pg.MOUSEBUTTONDOWN:

                    mouse_x, mouse_y = pg.mouse.get_pos()
                    board_x = mouse_x // self.tile_width
                    board_y = mouse_y // self.tile_height
                    return (board_x, board_y)

        else:
            self.game_over()
            return None

    def update(self):

        if self.command in self.board.get_valid_moves():
            self.board.move_tile(self.command)

        if self.board.is_game_won():
            self.game_won = True

    def render(self):

        if self.do_render:

            self.screen.fill(GREY)
            for row in range(TILES_PER_SIDE):
                for col in range(TILES_PER_SIDE):
                    coord = (col, row)
                    tile = self.board.tiles[coord]
                    self.screen.blit(self.tile_sprites[tile].image, (col * self.tile_width, row * self.tile_height))
            self.draw_grid()
            pg.display.flip()

    def draw_grid(self):

        for x in range(self.tile_width, self.screen_width, self.tile_width):
            pg.draw.line(self.screen, GREY, (x, 0), (x, self.screen_height))
        for y in range(self.tile_height, self.screen_height, self.tile_height):
            pg.draw.line(self.screen, GREY, (0, y), (self.screen_width, y))

    def exit(self):

        pg.quit()
        sys.exit()

    def intro(self):

        self.screen.fill(SILVER)
        self.draw_text("PygameSlidePuzzle", 48, GREY, (self.screen_width // 2, self.screen_height // 4))
        self.draw_text("Click on a tile to move it", 24, GREY, (self.screen_width // 2, self.screen_height // 2))
        self.draw_text("Click to start playing", 24, GREY, (self.screen_width // 2, self.screen_height * 3 // 4))
        pg.display.flip()

        on_start = True
        while on_start:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    on_start = False
                if event.type == pg.MOUSEBUTTONDOWN:
                    on_start = False

    def game_over(self):

        overlay = pg.Surface((self.screen_width, self.screen_height))
        overlay.fill(GREY)
        overlay.set_alpha(200)
        self.screen.blit(overlay, (0, 0))
        self.draw_text("Congratulations!", 48, SILVER, (self.screen_width // 2, self.screen_height // 2))
        self.draw_text("Click to play again", 24, SILVER, (self.screen_width // 2, self.screen_height * 3 // 4))
        pg.display.flip()

        waiting = True
        while waiting:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.do_render = False
                    self.running = False
                    waiting = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    self.board = Board()
                    self.game_won = False
                    waiting = False

    def draw_text(self, text, size, color, center_pos):
        font = pg.font.Font(None, size)
        textsurf = font.render(text, True, color)
        rect = textsurf.get_rect(center=(center_pos))
        self.screen.blit(textsurf, rect)


def main():

    game = Game()

    game.intro()
    while game.running:

        game.command = game.event_get()
        game.update()
        game.render()
        game.fps_clock.tick(FPS)

    game.exit()

if __name__ == "__main__":

    main()
