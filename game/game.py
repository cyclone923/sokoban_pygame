import pygame
import sys
from game.logic import SokobanLogic



class SokobanGame:
    def __init__(self, level, solver=None, limit=None):
        self.wall = pygame.image.load('images/wall.png')
        self.floor = pygame.image.load('images/floor.png')
        self.box = pygame.image.load('images/box.png')
        self.box_docked = pygame.image.load('images/box_docked.png')
        self.worker = pygame.image.load('images/worker.png')
        self.worker_docked = pygame.image.load('images/worker_dock.png')
        self.docker = pygame.image.load('images/dock.png')

        self.background = 255, 226, 191
        # pygame.init()
        pygame.font.init()
        # self.level = self.start_game()
        self.level = level
        self.logic = SokobanLogic('levels', self.level)
        if solver is not None:
            self.solver = solver(self.logic.matrix, time_limit=limit)

    def print_game(self, matrix, screen):
        screen.fill(self.background)
        x = 0
        y = 0
        for row in matrix:
            for char in row:
                if char == ' ':  # floor
                    screen.blit(self.floor, (x, y))
                elif char == '#':  # wall
                    screen.blit(self.wall, (x, y))
                elif char == '@':  # worker on floor
                    screen.blit(self.worker, (x, y))
                elif char == '.':  # dock
                    screen.blit(self.docker, (x, y))
                elif char == '*':  # box on dock
                    screen.blit(self.box_docked, (x, y))
                elif char == '$':  # box
                    screen.blit(self.box, (x, y))
                elif char == '+':  # worker on dock
                    screen.blit(self.worker_docked, (x, y))
                x = x + 32
            x = 0
            y = y + 32

    def get_key(self):
        while 1:
            event = pygame.event.poll()
            if event.type == pygame.KEYDOWN:
                return event.key
            else:
                pass

    def display_box(self, screen, message):
        "Print a message in a box in the middle of the screen"
        fontobject = pygame.font.Font(None, 18)
        pygame.draw.rect(screen, (0, 0, 0),
                         ((screen.get_width() / 2) - 100,
                          (screen.get_height() / 2) - 10,
                          200, 20), 0)
        pygame.draw.rect(screen, (255, 255, 255),
                         ((screen.get_width() / 2) - 102,
                          (screen.get_height() / 2) - 12,
                          204, 24), 1)
        if len(message) != 0:
            screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                        ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
        pygame.display.flip()

    def display_end(self, screen):
        message = "Level Completed"
        fontobject = pygame.font.Font(None, 18)
        pygame.draw.rect(screen, (0, 0, 0),
                         ((screen.get_width() / 2) - 100,
                          (screen.get_height() / 2) - 10,
                          200, 20), 0)
        pygame.draw.rect(screen, (255, 255, 255),
                         ((screen.get_width() / 2) - 102,
                          (screen.get_height() / 2) - 12,
                          204, 24), 1)
        screen.blit(fontobject.render(message, 1, (255, 255, 255)),
                    ((screen.get_width() / 2) - 100, (screen.get_height() / 2) - 10))
        pygame.display.flip()

    def ask(self, screen, question):
        "ask(screen, question) -> answer"
        current_string = []
        self.display_box(screen, question + ": " + "".join(current_string))
        while 1:
            inkey = self.get_key()
            if inkey == pygame.K_BACKSPACE:
                current_string = current_string[0:-1]
            elif inkey == pygame.K_RETURN:
                break
            elif inkey == pygame.K_MINUS:
                current_string.append("_")
            elif inkey <= 127:
                current_string.append(chr(inkey))
            self.display_box(screen, question + ": " + "".join(current_string))
        return int("".join(current_string))

    def start_game(self):
        start = pygame.display.set_mode((320, 240))
        level = self.ask(start, "Select Level")
        if level > 0:
            return level
        else:
            print("ERROR: Invalid Level: " + str(level))
            sys.exit(2)

    def play(self, solution=None):
        if solution is not None:
            solution = solution[::-1]
        self.size = self.logic.load_size()
        self.screen = pygame.display.set_mode(self.size)
        while 1:
            if self.logic.is_completed():
                self.display_end(self.screen)
            self.print_game(self.logic.get_matrix(), self.screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.logic.move(0, -1, True)
                    elif event.key == pygame.K_DOWN:
                        self.logic.move(0, 1, True)
                    elif event.key == pygame.K_LEFT:
                        self.logic.move(-1, 0, True)
                    elif event.key == pygame.K_RIGHT:
                        self.logic.move(1, 0, True)
                    elif event.key == pygame.K_q:
                        sys.exit(0)
                    elif event.key == pygame.K_SPACE and solution is not None:
                        control = solution.pop()
                        if control == "UP":
                            self.logic.move(0, -1, True)
                        elif control == "DOWN":
                            self.logic.move(0, 1, True)
                        elif control == "LEFT":
                            self.logic.move(-1, 0, True)
                        elif control == "RIGHT":
                            self.logic.move(1, 0, True)
            pygame.display.update()
