#!/usr/bin/env python3
"""Slide puzzle game using the Pygame library."""

import sys
import random
import pygame as pg

# constants
TILE_SIZE = 128
TILES_PER_SIDE = 3
SCREEN_SIZE = TILE_SIZE * TILES_PER_SIDE
FPS = 30

SHUFFLE = 40

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
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

        DEBUG = False
        if DEBUG:
            for row in range(TILES_PER_SIDE):
                for col in range(TILES_PER_SIDE):
                    coord = (col, row)
                    print("{}: {}".format(coord, self.tiles[coord]), end=' ')
            print()
            print("blank at {}".format(self.blank_xy))

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

        DEBUG = True
        if DEBUG:
            print(self.moves_list)

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
        self.screen = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        pg.display.set_caption("PygSlidePuzzle")
        self.fps_clock = pg.time.Clock()
        self.font = pg.font.Font(None, 24)

        self.board = Board()
        self.tile_sprites = self.init_tile_sprites()

        self.running = True
        self.command = None

    def init_tile_sprites(self):

        tile_sprites =[]
        for i in range(TILES_PER_SIDE * TILES_PER_SIDE - 1):
            tile_sprite = pg.sprite.Sprite()
            tile_sprite.image = pg.Surface((TILE_SIZE, TILE_SIZE))
            tile_sprite.rect = tile_sprite.image.get_rect()
            tile_sprite.image.fill(SILVER)
            tile_label = self.font.render(str(i), True, GREY)
            tile_sprite.image.blit(tile_label, tile_label.get_rect(center=tile_sprite.rect.center))
            tile_sprites.append(tile_sprite)
        # create the blank
        tile_sprite = pg.sprite.Sprite()
        tile_sprite.image = pg.Surface((TILE_SIZE, TILE_SIZE))
        tile_sprite.rect = tile_sprite.image.get_rect()
        tile_sprite.image.fill(GREY)
        tile_sprites.append(tile_sprite)

        return tile_sprites

    def event_get(self):

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

                DEBUG = False
                if DEBUG :
                    print("Mouse click at {},{}".format(mouse_x, mouse_y), end=' ')

                board_x = mouse_x // TILE_SIZE
                board_y = mouse_y // TILE_SIZE

                if DEBUG:
                    print("i.e. board ({},{})\n".format(board_x, board_y))

                return (board_x, board_y)

    def update(self):

        DEBUG = False
        if DEBUG:
            print("Command {} is valid :".format(self.command, self.board.get_valid_moves()))

        if self.command in self.board.get_valid_moves():
            self.board.move_tile(self.command)

        if self.board.is_game_won():
            print("Congratulations! You win!")

    def render(self):

        self.screen.fill(GREY)
        for row in range(TILES_PER_SIDE):
            for col in range(TILES_PER_SIDE):
                coord = (col, row)
                tile = self.board.tiles[coord]
                self.screen.blit(self.tile_sprites[tile].image, (col * TILE_SIZE, row * TILE_SIZE))
        self.draw_grid()
        pg.display.flip()

    def draw_grid(self):

        for x in range(TILE_SIZE, SCREEN_SIZE, TILE_SIZE):
            pg.draw.line(self.screen, GREY, (x, 0), (x, SCREEN_SIZE))
        for y in range(TILE_SIZE, SCREEN_SIZE, TILE_SIZE):
            pg.draw.line(self.screen, GREY, (0, y), (SCREEN_SIZE, y))

    def exit(self):

        pg.quit()
        sys.exit()


def main():

    game = Game()

    while game.running:

        game.command = game.event_get()
        game.update()
        game.render()
        game.fps_clock.tick(FPS)

    game.exit()

if __name__ == "__main__":

    main()
