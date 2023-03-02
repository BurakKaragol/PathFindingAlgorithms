import math
import time

import pygame
from enum import Enum

pygame.init()

# region variables
# Colors
BLACK = 52, 73, 94
LIGHT_GREY = 65, 65, 65
GREY = 204, 204, 204
DARK_GREY = 190, 190, 190
WHITE = 242, 242, 242
GREEN = 231, 76, 60
YELLOW = 255, 255, 0
RED = 243, 156, 18
MAGENTA = 255, 0, 255
BLUE = 26, 188, 156
CYAN = 52, 152, 219

# Paddings
side_left = 20
side_right = 400
side_top = 20
side_bottom = 20

# General Values
grid_x_count = 30
grid_y_count = 30
grid_width = 20
grid_height = 20
grid_x_gap = 2
grid_y_gap = 2

buttons = []
# endregion

# region Classes
# For UI Buttons
class Button:
    color = LIGHT_GREY

    def __init__(self, x, y, text, color, func):
        self.x = x
        self.y = y
        self.width = text.get_width() + 20
        self.height = text.get_height() + 10
        self.text = text
        self.color = color
        self.func = func

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0)
        window.blit(self.text, (self.x + 10, self.y + 5))

    def mouse_over_grid(self, mouse_pos):
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        if mouse_x >= self.x and mouse_x <= self.x + self.width:
            if mouse_y >= self.y and mouse_y <= self.y + self.height:
                return True
        return False

# General Application Variables
class WindowData:
    color = WHITE

    font = pygame.font.SysFont('comicsans', 15)
    medium_font = pygame.font.SysFont('comicsans', 20)
    large_font = pygame.font.SysFont('comicsans', 25)

    def __init__(self, width, height, speed, mode):
        self.width = width
        self.height = height
        self.speed = speed
        self.mode = mode
        self.running = False
        self.step = False
        self.search_time = 0
        self.status = 'Place Start / Finish Points to Start'
        self.start_grid = 0
        self.finish_grid = 0
        self.find_path = False

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pathfinding Algorithm Visualizer")

    def set_mode(self, mode):
        self.mode = mode

    def toggle_run(self):
        if self.running:
            self.running = False
        else:
            self.running = True

    def step(self):
        self.step = True

# Grid Types - DEFAULT / SEARCHING / SERACHED / SELECTED / USED / OBSTACLE / START / FINISH
class GridType(Enum):
    DEFAULT = GREY
    SEARCHING = RED
    SEARCHED = BLUE
    SELECTED = CYAN
    USED = DARK_GREY
    OBSTACLE = BLACK
    START = BLUE
    FINISH = GREEN

# Draw Types - DELETE / DRAW_OBSTACLE / SET_START / SET_FINISH
class DrawType(Enum):
    DELETE = GridType.DEFAULT
    DRAW_OBSTACLE = GridType.OBSTACLE
    SET_START = GridType.START
    SET_TARGET = GridType.FINISH

# All data about one grid: position in array, screen position, neighbors, size
class GridData:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.x_pos = (self.x * grid_width) + ((self.x - 1) * grid_x_gap) + side_left
        self.y_pos = (self.y * grid_height) + ((self.y - 1) * grid_y_gap) + side_top
        self.width = width
        self.height = height
        self.type = GridType.DEFAULT
        self.neighbors = []

    def update_neightbors(self, grid_map):
        self.neighbors = []
        if self.type == GridType.OBSTACLE:
            return
        if not self.x == 0:
            self.neighbors.append(grid_map[self.x - 1][self.y])
        if not self.x == grid_x_count - 1:
            self.neighbors.append(grid_map[self.x + 1][self.y])
        if not self.y == 0:
            self.neighbors.append(grid_map[self.x][self.y - 1])
        if not self.y == grid_y_count - 1:
            self.neighbors.append(grid_map[self.x][self.y + 1])

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def get_position(self):
        return self.x_pos, self.y_pos

    def mouse_over_grid(self, mouse_pos):
        mouse_x = mouse_pos[0]
        mouse_y = mouse_pos[1]
        if mouse_x >= self.x_pos and mouse_x <= self.x_pos + self.width:
            if mouse_y >= self.y_pos and mouse_y <= self.y_pos + self.height:
                return True
        return False

    def reiterate(self):
        if self.type != GridType.OBSTACLE and self.type != GridType.START and self.type != GridType.FINISH:
            self.type = GridType.DEFAULT

    def set_mode(self, mode):
        self.type = mode
# endregion

# region General Functions
# Returns the grid that in the click point
def get_clicked_grid(grids, mouse_pos):
    for i in range(grid_x_count):
        for j in range(grid_y_count):
            if grids[i][j].mouse_over_grid(mouse_pos):
                return grids[i][j]

# Creates the first grid map
def set_gridmap():
    grids = []
    for x in range(grid_x_count):
        grids.append([])
        for y in range(grid_y_count):
            x_pos = (x * grid_width) + ((x - 1) * grid_x_gap)
            y_pos = (y * grid_height) + ((y - 1) * grid_y_gap)
            grid = GridData(x, y, grid_width, grid_height)
            grids[x].append(grid)
    return grids

# Mouse drawing function: draws the selected Grid type
def draw_mouse(grid_map, window_data):
    clicked_grid = get_clicked_grid(grid_map, pygame.mouse.get_pos())
    if clicked_grid == None:
        return window_data.start_grid, window_data.finish_grid
    if window_data.mode == DrawType.DRAW_OBSTACLE:
        clicked_grid.set_mode(GridType.OBSTACLE)
    elif window_data.mode == DrawType.SET_START:
        if window_data.start_grid == 0:
            clicked_grid.set_mode(GridType.START)
        else:
            window_data.start_grid.set_mode(GridType.DEFAULT)
            clicked_grid.set_mode(GridType.START)
        window_data.start_grid = clicked_grid
    elif window_data.mode == DrawType.SET_TARGET:
        if window_data.finish_grid == 0:
            clicked_grid.set_mode(GridType.FINISH)
        else:
            window_data.finish_grid.set_mode(GridType.DEFAULT)
            clicked_grid.set_mode(GridType.FINISH)
        window_data.finish_grid = clicked_grid
    else:
        if clicked_grid.type == GridType.START:
            window_data.start_grid = 0
        elif clicked_grid.type == GridType.FINISH:
            window_data.finish_grid = 0
        clicked_grid.set_mode(GridType.DEFAULT)
    return window_data.start_grid, window_data.finish_grid

# General draw function: drawing the application window, grids and ui buttons
def draw(window_info, grid_info, buttons):
    window_info.window.fill(window_info.color)

    for i in range(grid_x_count):
        for j in range(grid_y_count):
            pygame.draw.rect(window_info.window, grid_info[i][j].type.value,
                             (grid_info[i][j].x_pos, grid_info[i][j].y_pos,
                              grid_info[i][j].width, grid_info[i][j].height))

    ui_draw_start = (side_left * 2) + (grid_x_count * grid_width + (grid_x_count - 1) * grid_x_gap)

    application_name_text = window_info.large_font.render("Pathfinding Algorithm Visualizer", 1, BLACK)
    window_info.window.blit(application_name_text, (ui_draw_start, side_top))

    mode_selection_text = window_info.medium_font.render("Active Mode:", 1, BLACK)
    window_info.window.blit(mode_selection_text, (ui_draw_start, 60))

    if(window_info.mode == DrawType.DRAW_OBSTACLE):
        active_mode_text = window_info.medium_font.render("Obstacle", 1, BLACK)
    elif(window_info.mode == DrawType.SET_START):
        active_mode_text = window_info.medium_font.render("Start", 1, BLUE)
    elif(window_info.mode == DrawType.SET_TARGET):
        active_mode_text = window_info.medium_font.render("Finish", 1, GREEN)
    else:
        active_mode_text = window_info.medium_font.render("Delete", 1, RED)
    window_info.window.blit(active_mode_text, (ui_draw_start + 150, 60))

    speed_visual_text = window_info.medium_font.render("Speed", 1, BLACK)
    window_info.window.blit(speed_visual_text, (ui_draw_start, 350))

    speed_text = window_info.medium_font.render(f'{window_info.speed}', 1, BLACK)
    window_info.window.blit(speed_text, (ui_draw_start + 100, 350))

    search_time_text = window_info.medium_font.render(f'Search Time: {window_info.search_time}', 1, BLACK)
    window_info.window.blit(search_time_text, (ui_draw_start, 550))

    status_text = window_info.medium_font.render('Status:', 1, BLACK)
    window_info.window.blit(status_text, (ui_draw_start, 600))

    status_text = window_info.medium_font.render(f'{window_info.status}', 1, BLACK)
    window_info.window.blit(status_text, (ui_draw_start, 640))

    for i in range(len(buttons)):
        buttons[i].draw(window_info.window)

    pygame.display.update()

# Calls the update_neightbors function in all of the grids
def update_all_neightbors(grid_map):
    for i in range(grid_x_count):
        for j in range(grid_y_count):
            grid_map[i][j].update_neightbors(grid_map)

# Resets the path
def reiterate_gridmap(grid_map):
    for i in range(grid_x_count):
        for j in range(grid_y_count):
            grid_map[i][j].reiterate()

# Clears the A* path
def clear_paths(grid_map):
    for x in range(grid_x_count):
        for y in range(grid_y_count):
            if grid_map[x][y].type == GridType.SEARCHING:
                grid_map[x][y].set_mode(GridType.DEFAULT)
            elif grid_map[x][y].type == GridType.USED:
                grid_map[x][y].set_mode(GridType.DEFAULT)
            elif grid_map[x][y].type == GridType.SELECTED:
                grid_map[x][y].set_mode(GridType.DEFAULT)

# Implementign the buttons
def create_buttons(window_data):
    ui_draw_start = (side_left * 2) + (grid_x_count * grid_width + (grid_x_count - 1) * grid_x_gap)
    obstacle_mode_button = Button(ui_draw_start, 100, window_data.medium_font.render("Place Obstacle (O)", 1, WHITE), BLACK, place_obstacle)
    buttons.append(obstacle_mode_button)
    start_mode_button = Button(ui_draw_start, 150, window_data.medium_font.render("Place Start (S)", 1, WHITE), BLUE, place_start)
    buttons.append(start_mode_button)
    finish_mode_button = Button(ui_draw_start, 200, window_data.medium_font.render("Place Finish (F)", 1, WHITE), GREEN, place_finish)
    buttons.append(finish_mode_button)
    delete_mode_button = Button(ui_draw_start, 250, window_data.medium_font.render("Delete (X)", 1, WHITE), RED, place_default)
    buttons.append(delete_mode_button)
    clear_button = Button(ui_draw_start, 300, window_data.medium_font.render("Clear All (C)", 1, WHITE), LIGHT_GREY, clear_all)
    buttons.append(clear_button)
    slow_button = Button(ui_draw_start, 400, window_data.medium_font.render("Slow (A)", 1, WHITE), LIGHT_GREY, slow_function)
    buttons.append(slow_button)
    fast_button = Button(ui_draw_start + 115, 400, window_data.medium_font.render("Fast (D)", 1, WHITE), LIGHT_GREY, fast_function)
    buttons.append(fast_button)
    start_button = Button(ui_draw_start, 450, window_data.medium_font.render("Start (Space)", 1, WHITE), RED, start_stop_function)
    buttons.append(start_button)
    exit_button = Button(ui_draw_start, 500, window_data.medium_font.render("Quit Application (Q)", 1, WHITE), BLACK, exit_function)
    buttons.append(exit_button)
# endregion

#region Pathfinding Algorithm
# A* function
def astar(window_data, grid_map, buttons, heuristic, cost):
    grid = convert_to_dict(grid_map)
    open_set = set([window_data.start_grid])
    closed_set = set()
    g_scores = {window_data.start_grid: 0}
    f_scores = {window_data.start_grid: heuristic(window_data.start_grid, window_data.finish_grid)}
    parents = {}
    stopped = False
    step = False
    start_time = time.time()

    while open_set:
        window_data.search_time = str(float('%.2f' % (time.time() - start_time))) + ' seconds'

        if not stopped or step:
            current = min(open_set, key=lambda x: f_scores[x])
            if current == window_data.finish_grid:
                path = [current]
                while current in parents:
                    current = parents[current]
                    path.append(current)
                path.reverse()
                return path
            open_set.remove(current)
            closed_set.add(current)
            for neighbor in current.neighbors:
                if neighbor in closed_set:
                    continue
                tentative_g_score = g_scores[current] + cost(current, neighbor)
                if neighbor not in open_set or tentative_g_score < g_scores[neighbor]:
                    parents[neighbor] = current
                    g_scores[neighbor] = tentative_g_score
                    f_scores[neighbor] = tentative_g_score + heuristic(neighbor, window_data.finish_grid)
                    if neighbor not in open_set:
                        open_set.add(neighbor)
                        mode_select(neighbor)
            step = False
            draw(window_data, grid_map, buttons)
            pygame.time.delay(120 - window_data.speed)
            window_data.search_time = 0
    return None

# Sets the grid type while on A* project
def mode_select(grid):
    if grid.type == GridType.START:
        grid.set_mode(GridType.START)
    elif grid.type == GridType.FINISH:
        grid.set_mode(GridType.FINISH)
    elif grid.type == GridType.OBSTACLE:
        grid.set_mode(GridType.OBSTACLE)
    else:
        grid.set_mode(GridType.SEARCHING)

# convert to dictionary
def convert_to_dict(grid_map):
    dictionary = {}
    i = 0
    for x in range(grid_x_count):
        for y in range(grid_y_count):
            dictionary[i] = grid_map[x][y]
            i += 1
    return dictionary

# Heuristic fuction
def manhattan_distance(node, goal):
    dx = abs(node.x - goal.x)
    dy = abs(node.y - goal.y)
    return dx + dy

# Cost function
def euclidean_cost(current_node, next_node):
    dx = abs(current_node.x - next_node.x)
    dy = abs(current_node.y - next_node.y)
    return math.sqrt(dx*dx + dy*dy)
#endregion

# region Button Functions
# Clears all grids to default
def clear_all(window_data, grid_map):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c))

# Set mode to place obstacle
def place_obstacle(window_data, grid_map):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_o))
    window_data.set_mode(DrawType.DRAW_OBSTACLE)

# Set mode to place start
def place_start(window_data, grid_map):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_s))
    window_data.set_mode(DrawType.SET_START)

# Set mode to place finish
def place_finish(window_data, grid_map):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_f))
    window_data.set_mode(DrawType.SET_TARGET)

# Set mode to place default (delete)
def place_default(window_data, grid_map):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x))
    window_data.set_mode(DrawType.DELETE)

# toggles application run logic
def start_stop_function(window_data, grid_map):
    window_data.toggle_run()

# Decreases the loop speed minimum 5
def slow_function(window_data, grid_map):
    if window_data.speed - 5 < 5:
        window_data.speed = 5
    else:
        window_data.speed = window_data.speed - 5

# Increases the loop speed maximum 115
def fast_function(window_data, grid_map):
    if window_data.speed + 5 > 115:
        window_data.speed = 115
    else:
        window_data.speed = window_data.speed + 5

# toggles the exit application keypress
def exit_function(window_data, grid_map):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
# endregion

def main():
    run = True
    clock = pygame.time.Clock()

    grid_map = set_gridmap()
    update_all_neightbors(grid_map)
    window_data = WindowData(side_left + (grid_x_count * grid_width) + ((grid_x_count - 1) * grid_x_gap) + side_right,
                             side_top + (grid_y_count * grid_height) + ((grid_y_count - 1) * grid_y_gap) + side_bottom,
                             60, DrawType.DRAW_OBSTACLE)
    create_buttons(window_data)

    is_drawing = False

    while run:
        clock.tick(window_data.speed)

        draw(window_data, grid_map, buttons)

        if window_data.running:
            update_all_neightbors(grid_map)
            reiterate_gridmap(grid_map)
            if window_data.start_grid == 0:
                window_data.status = 'Please define a start point'
                window_data.running = False
            elif window_data.finish_grid == 0:
                window_data.status = 'Please define a finish point'
                window_data.running = False
            else:
                window_data.status = 'Searching...'
                path = astar(window_data, grid_map, buttons, manhattan_distance, euclidean_cost)
                if path:
                    for cell in path:
                        if not cell.type == GridType.START and not cell.type == GridType.FINISH:
                            cell.set_mode(GridType.SELECTED)
                    window_data.running = False
                    window_data.find_path = True
                    window_data.status = 'Find path!'
                elif path == -1:
                    run = False
                else:
                    window_data.running = False
                    window_data.status = 'Couldn\'t find path'
                    window_data.find_path = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in range(len(buttons)):
                    if buttons[i].mouse_over_grid(pygame.mouse.get_pos()):
                        buttons[i].func(window_data, grid_map)
                is_drawing = True

            if is_drawing:
                window_data.start_grid, window_data.finish_grid = draw_mouse(grid_map, window_data)

            if event.type == pygame.MOUSEBUTTONUP:
                is_drawing = False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_q:
                run = False
            elif event.key == pygame.K_o:
                window_data.mode = DrawType.DRAW_OBSTACLE
            elif event.key == pygame.K_s:
                window_data.mode = DrawType.SET_START
            elif event.key == pygame.K_f:
                window_data.mode = DrawType.SET_TARGET
            elif event.key == pygame.K_x:
                window_data.mode = DrawType.DELETE
            elif event.key == pygame.K_c:
                window_data.running = False
                if window_data.find_path:
                    clear_paths(grid_map)
                    window_data.find_path = False
                else:
                    for i in range(grid_x_count):
                        for j in range(grid_y_count):
                            grid_map[i][j].set_mode(GridType.DEFAULT)
                    window_data.start_grid = 0
                    window_data.finish_grid = 0
                    window_data.search_time = 0
            elif event.key == pygame.K_a:
                slow_function(window_data, grid_map)
            elif event.key == pygame.K_d:
                fast_function(window_data, grid_map)
            elif event.key == pygame.K_SPACE:
                start_stop_function(window_data, grid_map)

    pygame.quit()

if __name__ == '__main__':
    main()