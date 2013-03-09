import pygame, random
from pygame.locals import *

pygame.init()
fpsClock = pygame.time.Clock()

size = (640,480)
windowSurfaceObj = pygame.display.set_mode(size)
pygame.display.set_caption('Hello PyGame')

red = pygame.image.load('images/red.png')
white = pygame.Color(255,255,255)
blue = pygame.image.load('images/blue.png')
green = pygame.image.load('images/green.png')
yellow = pygame.image.load('images/yellow.png')
purple = pygame.image.load('images/purple.png')
gray_map = {'red': pygame.image.load('images/red_clear.png'),
            'blue': pygame.image.load('images/blue_clear.png'),
            'green': pygame.image.load('images/green_clear.png'),
            'yellow': pygame.image.load('images/yellow_clear.png'),
            'purple': pygame.image.load('images/purple_clear.png')}
testFont = pygame.font.Font('freesansbold.ttf', 32)

def three_consecutive_same(li):
    for i in range(len(li) - 2):
        if li[i] == li[i+1] and li[i+1] == li[i+2]:
            return True
    return False

class Block:
    fall_delay_time = 40
    gravity_time = 2 # Number of frames to fall 1 cell
    clear_color = pygame.Color(150, 150, 150)
    def __init__(self, color_info):
        self.color_name, self.color = color_info
        self.timestep = 0
        self.clear_time = 45
        self.fall_delay = self.fall_delay_time
        self.is_falling = False # Changed by Board class
        self.fell_from_match = False # Changed to True by Board class
        self.clearing = False
        self.score_on_clear = 10
    def step(self):
        if self.is_falling or self.clearing:
            self.timestep += 1
        else:
            self.timestep = 0
    
class Board:
    width = 7
    height = 9
    def __init__(self):
        self.cells = [[None] * self.width for _ in range(self.height)]
        self.tile_colors = [('red', red), ('blue', blue), ('green', green), ('yellow', yellow), ('purple', purple)]
        self.next_row = [None] * self.width
        self.generate_next_row()
        self.has_lost = False
        self.time = 0 # Number of frames since start
        self.time_to_spawn = 150
        self.chain = 0
        self.num_matched = 0
        self.score = 0
    def get_cell(self, x, y):
        block = self.cells[y][x]
        if block:
            return block.color
        else:
            return None
    def generate_next_row(self):
        for i in range(self.width):
            self.next_row[i] = random.choice(self.tile_colors)
        if three_consecutive_same(self.next_row):
            self.generate_next_row()
        else:
            for i in range(self.width):
                self.next_row[i] = Block(self.next_row[i])
    def is_going_to_lose(self):
        for cell in self.cells[0]:
            if cell is not None:
                return True
        return False
    def add_next_row(self):
        if self.is_going_to_lose():
            # Do something to cause losing
            print("FAIL")
            pygame.quit()
        else:
            # Swap each row up
            for i in range(self.height - 1):
                self.cells[i] = self.cells[i+1]
            self.cells[self.height - 1] = list(self.next_row)
            self.generate_next_row()
    def swap_cells(self, x1, y1, x2, y2):
        if self.cells[y1][x1] is None or (not self.cells[y1][x1].clearing and not self.cells[y1][x1].is_falling):
            if self.cells[y2][x2] is None or (not self.cells[y2][x2].clearing and not self.cells[y2][x2].is_falling):
                self.cells[y1][x1], self.cells[y2][x2] = self.cells[y2][x2], self.cells[y1][x1]
    def clear_cells(self):
        # DEBUG PURPOSES ONLY
        self.cells = [[None] * self.width for _ in range(self.height)]
    def is_valid(self, x, y):
        return x in range(self.width) and y in range(self.height)
    def find_matched(self, x, y):
        # Checks right + down, adds all cells it finds in match 3
        block_type = self.get_cell(x,y)
        matched = set()
        if block_type != None and not self.cells[y][x].clearing:
            if x + 2 < self.width:
                if self.get_cell(x+1, y) == block_type and not self.cells[y][x+1].is_falling and not self.cells[y][x+1].clearing:
                    if self.get_cell(x+2, y) == block_type and not self.cells[y][x+2].is_falling and not self.cells[y][x+2].clearing:
                        matched.add((x+1,y))
                        matched.add((x+2,y))
                        matched.add((x,y))
            if y + 2 < self.height:
                if self.get_cell(x, y+1)==block_type and not self.cells[y+1][x].is_falling and not self.cells[y+1][x].clearing:
                    if self.get_cell(x, y+2)==block_type and not self.cells[y+2][x].is_falling and not self.cells[y+2][x].clearing:
                        matched.add((x, y+1))
                        matched.add((x, y+2))
                        matched.add((x,y))
        return matched
    def matched_blocks(self):
        # Returns a list of coordinates, where each coordinate represents the start of a match
        used_blocks = set()
        for i in range(self.width):
            for j in range(self.height):
                used_blocks = used_blocks.union(self.find_matched(i, j))
        if len(used_blocks) > 0:
            self.num_matched = len(used_blocks)
        return used_blocks
    def clear_matches(self):
        matched = self.matched_blocks()
        self.chain += 1
        if matched:
            for x, y in matched:
                self.cells[y][x].clearing = True
                self.cells[y][x].shown_color = Block.clear_color
            print("Matched %d blocks" % self.num_matched)
            print("Chain %d" % self.chain)
    def reset_chain(self):
        self.chain = 0
    def timestep(self):
        """
        Order of events
        
        Blocks fall
        Matches get cleared
        New lines get spawned
        Values get reset
        
        Implement by checking every block multiple times. Probably optimizable.
        """
    
        # First find which blocks are falling. Default to not falling
        for i in range(self.width):
            for j in range(self.height):
                if self.cells[j][i]:
                    self.cells[j][i].is_falling = False
                if self.cells[j][i] is None:
                    for k in range(0, j):
                        if self.cells[k][i]:
                            if self.cells[k][i].clearing:
                                break
                            self.cells[k][i].is_falling = True
                    
        # Then timestep each falling block
        # Doing bottom up makes it work as intended
        for i in range(self.width):
            for j in range(self.height - 1, -1, -1):
                cell = self.cells[j][i]
                if cell:
                    cell.step()
                    if cell.clearing:
                        if cell.timestep >= cell.clear_time:
                            self.cells[j][i] = None
                            self.score += cell.score_on_clear * (self.chain ** 2)
                            # Tell all above that they are falling from a match
                            for k in range(j):
                                if self.cells[k][i]:
                                    self.cells[k][i].fell_from_match = True
                    elif cell.fall_delay > 0 and cell.timestep >= cell.fall_delay:
                        # Hope that this will only occur in valid situations. Probably does...
                        cell.fall_delay = 0
                        cell.timestep = 0
                    elif cell.timestep >= cell.gravity_time:
                        self.cells[j+1][i] = cell
                        self.cells[j][i] = None
                        # Recompute is falling
                        cell.is_falling = False
                        for k in range(j+2, self.height):
                            if self.cells[k][i] is None:
                                cell.is_falling = True
                        if not cell.is_falling:
                            cell.fall_delay = Block.fall_delay_time
                        
        self.clear_matches()
        self.time += 1
        if self.time % self.time_to_spawn == 0:
            self.add_next_row()
        should_reset = True
        for i in range(self.width):
            for j in range(self.height):
                if self.cells[j][i] and self.cells[j][i].clearing:
                    should_reset = False
        if should_reset:
            self.reset_chain()
                
class Cursor:
    """Represents the cursor for the self."""
    width = 7
    height = 9
    def __init__(self):
        # x, y reprsent the left box of the cursor
        self.x = 2
        self.y = 2
    def move_left(self):
        self.x = max(self.x - 1, 0)
    def move_right(self):
        self.x = min(self.x + 1, self.width - 2)
    def move_up(self):
        self.y = max(self.y - 1, 0)
    def move_down(self):
        self.y = min(self.y + 1, self.height - 1) 

cellSize = 40
leftOffset = 10
topOffset = 50
board = Board()
cursor = Cursor()
for _ in range(5):
    board.add_next_row()
time_held = {K_UP: 0, K_LEFT: 0, K_RIGHT: 0, K_DOWN: 0}

while True:
    windowSurfaceObj.fill(white)
    pygame.draw.line(windowSurfaceObj, (0,0,0), (5,10), (5,410), 5)
    pygame.draw.line(windowSurfaceObj, (0,0,0), (294,10), (294, 410), 5)
    pygame.draw.line(windowSurfaceObj, (0,0,0), (5,10), (294,10), 5)
    pygame.draw.line(windowSurfaceObj, (0,0,0), (5,410), (294, 410), 5)
    board.timestep()
    scoreObj = testFont.render("Score: %d" % board.score, False, (0,0,0))
    windowSurfaceObj.blit(scoreObj, (400, 150))
    botVisiblePixels = int(cellSize * (board.time % board.time_to_spawn) / board.time_to_spawn)
    netTopOffset = topOffset - botVisiblePixels
    for i in range(board.width):
        for j in range(board.height):
            color = board.get_cell(i,j)
            if color is None:
                color = (255,255,255)
                pygame.draw.rect(windowSurfaceObj, color, (leftOffset + cellSize * i, netTopOffset + cellSize * j, cellSize, cellSize))
            elif board.cells[j][i].clearing:
                windowSurfaceObj.blit(gray_map[board.cells[j][i].color_name], (leftOffset + cellSize * i, netTopOffset + cellSize * j, cellSize, cellSize))
            else:
                windowSurfaceObj.blit(color, (leftOffset + cellSize * i, netTopOffset + cellSize * j, cellSize, cellSize))
    row = board.next_row
    for i in range(board.width):
        cell = row[i]
        windowSurfaceObj.blit(cell.color, (leftOffset + cellSize * i, netTopOffset + cellSize * 9), (0,0,cellSize, botVisiblePixels))
    
    minutes = board.time // 1800
    sec = (board.time - 1800 * minutes) // 30
    timeObj = testFont.render("Time %d:%02d" % (minutes, sec), False, (0,0,0))
    windowSurfaceObj.blit(timeObj, (400,100))
    
    cursorObj = pygame.image.load('images/cursor.png')
    windowSurfaceObj.blit(cursorObj, (cellSize * cursor.x + leftOffset - 10, cellSize * cursor.y + netTopOffset - 10))
    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
        elif event.type == KEYDOWN:
            if event.key == K_UP:
                cursor.move_up()
            if event.key == K_DOWN:
                cursor.move_down()
            if event.key == K_LEFT:
                cursor.move_left()
            if event.key == K_RIGHT:
                cursor.move_right()
            if event.key == K_SPACE:
                board.swap_cells(cursor.x, cursor.y, cursor.x + 1, cursor.y)
    pygame.display.update()
    fpsClock.tick(30)
    