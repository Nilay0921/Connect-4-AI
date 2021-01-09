import numpy as np
import pygame
import sys
import math
import random

ROWS = 6
COLS = 7

BLUE = (0, 0, 255)
BLACK  = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
MAGENTA = (255, 0, 255)

PLAYER = 0
AI = 1

PLAYER_PEICE = 1
AI_PEICE = 2

WINDOW_LEN = 4
EMPTY = 0

def create_board():
    board = np.zeros((ROWS, COLS))
    return board

def is_valid_spot(board, col):
    return board[5][col] == 0

def get_open_row(board, col):
    for i in range(0, ROWS):
        if board[i][col] == 0:
            return i

def place_peice(board, row, col, peice):
    board[row][col] = peice 

def print_board(board):
    print(np.flip(board, 0))

def win_checker(board, peice):
    for c in range(COLS - 3):
        for r in range(ROWS):
            if board[r][c] == peice and board[r][c+1] == peice and board[r][c+2] == peice and board[r][c+3] == peice:
                return True
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] == peice and board[r+1][c] == peice and board[r+2][c] == peice and board[r+3][c] == peice:
                return True
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] == peice and board[r+1][c+1] == peice and board[r+2][c+2] == peice and board[r+3][c+3] == peice:
                return True
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if board[r][c] == peice and board[r-1][c+1] == peice and board[r-2][c+2] == peice and board[r-3][c+3] == peice:
                return True

def evaluate_window(window, peice):
    score = 0
    opposition_peice = PLAYER_PEICE
    if peice == PLAYER_PEICE:
        opposition_peice = AI_PEICE
    if window.count(peice) == 4:
        score += 100
    elif window.count(peice) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(peice) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opposition_peice) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score
    

def position_score(board, peice):
    score = 0

    center_array = [int(i) for i in list(board[:, COLS//2])]
    center_count = center_array.count(peice)
    score += center_count * 3

    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c:c+WINDOW_LEN]
            score += evaluate_window(window, peice)
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r:r+WINDOW_LEN]
            score += evaluate_window(window, peice)
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LEN)]
            score += evaluate_window(window, peice)
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r-i][c+i] for i in range(WINDOW_LEN)]
            score += evaluate_window(window, peice)
    return score

def terminal(board):
    return win_checker(board, PLAYER_PEICE) or win_checker(board, AI_PEICE) or check_tie(board)

def mini_max(board, depth, maximizing_player, alpha, beta):
    valid_locations = get_valid_locations(board)
    is_terminal = terminal(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if win_checker(board, AI_PEICE):
                return (None, 10000000000)
            elif win_checker(board, PLAYER_PEICE):
                return (None, -10000000000)
            else:
                return (None, 0)
        else:
            return (None, position_score(board, AI_PEICE))

    if maximizing_player:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_open_row(board, col)
            copy_board = board.copy()
            place_peice(copy_board, row, col, AI_PEICE)
            new_score = mini_max(copy_board, depth - 1, False, alpha, beta)[1]
            if new_score > value:
                value = new_score
                best_col = col

            alpha = max(value, alpha)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_open_row(board, col)
            copy_board = board.copy()
            place_peice(copy_board, row, col, PLAYER_PEICE)
            new_score = mini_max(copy_board, depth - 1, True, alpha, beta)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(value, beta)
            if alpha >= beta:
                break
        return best_col, value

def get_valid_locations(board):
    valid = []
    for col in range(COLS):
        if is_valid_spot(board, col):
            valid.append(col)
    return valid

def best_move(board, peice):
    valid_locations = get_valid_locations(board)
    optimal_score = -1000000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_open_row(board, col) 
        temp_board = board.copy()
        place_peice(temp_board, row, col, peice)
        score = position_score(temp_board, peice)
        if score > optimal_score:
            optimal_score = score
            best_col = col
    return best_col


def check_tie(board):
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 0:
                return False
    return True

def draw_board(board):
    for r in range(ROWS):
        for c in range(COLS):
            pygame.draw.rect(screen_display, BLUE, (c * SIZESQUARE, r * SIZESQUARE + SIZESQUARE, SIZESQUARE, SIZESQUARE))
            pygame.draw.circle(screen_display, BLACK, (int(c * SIZESQUARE + SIZESQUARE/2), int(r * SIZESQUARE + SIZESQUARE + SIZESQUARE/2)), RADIUS)

    for r in range(ROWS):
        for c in range(COLS):    
            if board[r][c] == 1:
                pygame.draw.circle(screen_display, RED, (int(c * SIZESQUARE + SIZESQUARE/2), height - int(r * SIZESQUARE + SIZESQUARE/2)), RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen_display, YELLOW, (int(c * SIZESQUARE + SIZESQUARE/2), height - int(r * SIZESQUARE + SIZESQUARE/2)), RADIUS)
    pygame.display.update()

def clear_board(board):
    for r in range(ROWS):
        for c in range(COLS):
            board[r][c] = 0

    
board = create_board()
is_game_over = False
turn = 0
AI_GAME_TURN = random.randint(PLAYER, AI)

pygame.init()
SIZESQUARE = 100

width = COLS * SIZESQUARE
height = (ROWS + 1) * SIZESQUARE

RADIUS = int(SIZESQUARE/2 - 3)

size = (width, height)

screen_display = pygame.display.set_mode(size)

font = pygame.font.SysFont("arial", 75)
menu_font = pygame.font.SysFont("arial", 150)
button_font = pygame.font.SysFont("arial", 50)

def main_menu():
    menu = True

    while menu:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
        
        label = menu_font.render("Connect 4", 1, RED)
        two_player_label = button_font.render("Player vs Player", 1, MAGENTA)
        ai_label = button_font.render("Player vs AI", 1, MAGENTA)
        screen_display.blit(label, (70, 100))
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if 200+300 > mouse[0] > 200 and 290+100 > mouse[1] > 290:
            pygame.draw.rect(screen_display, WHITE, (200, 290, 300, 100))
            if click[0] == 1:
                two_player_game(is_game_over, turn)
        else:
            pygame.draw.rect(screen_display, BLUE, (200, 290, 300, 100))
        if 200+300 > mouse[0] > 200 and 450+100 > mouse[1] > 450:    
            pygame.draw.rect(screen_display, WHITE, (200, 450, 300, 100))
            if click[0] == 1:
                ai_game(is_game_over, AI_GAME_TURN)
        else:
            pygame.draw.rect(screen_display, BLUE, (200, 450, 300, 100))
        screen_display.blit(two_player_label, (200, 310))
        screen_display.blit(ai_label, (240, 470))
        pygame.display.update()


def two_player_game(is_game_over, turn):

    draw_board(board)
    pygame.display.update()

    while not is_game_over:

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()

            if e.type == pygame.MOUSEMOTION:
                xpos = e.pos[0]
                pygame.draw.rect(screen_display, BLACK, (0, 0, width, SIZESQUARE))
                if turn == 0:
                    pygame.draw.circle(screen_display, RED, (xpos, int(SIZESQUARE/2)), RADIUS)
                else:
                    pygame.draw.circle(screen_display, YELLOW, (xpos, int(SIZESQUARE/2)), RADIUS)
            pygame.display.update()
                
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                xpos = e.pos[0]
                pygame.draw.rect(screen_display, BLACK, (0, 0, width, SIZESQUARE))
                if turn == 0:
                    col = int(math.floor(xpos/SIZESQUARE))
                    if is_valid_spot(board, col):
                        spot = get_open_row(board, col)
                        place_peice(board, spot, col, 1)
                        turn = 1

                        if win_checker(board, 1):
                            label = font.render("Player 1 wins!", 1, RED)
                            screen_display.blit(label, (140, 10))
                            is_game_over = True
                        elif check_tie(board):
                            label = font.render("Tie Game!", 1, RED)
                            screen_display.blit(label, (160, 10))
                            is_game_over = True
                            
                else:
                    col = int(math.floor(xpos/SIZESQUARE))
                    if is_valid_spot(board, col):
                        spot = get_open_row(board, col)
                        place_peice(board, spot, col, 2)
                        turn = 0

                        if win_checker(board, 2):
                            label = font.render("Player 2 wins!", 1, YELLOW)
                            screen_display.blit(label, (140, 10))
                            is_game_over = True
                        elif check_tie(board):
                            label = font.render("Tie Game!", 1, RED)
                            screen_display.blit(label, (160, 10))
                            is_game_over = True

                draw_board(board)

                if is_game_over:
                    pygame.time.wait(2000)
                    clear_board(board)
                    screen_display.fill(BLACK)

def ai_game(is_game_over, turn):

    draw_board(board)
    pygame.display.update()

    while not is_game_over:

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()

            if e.type == pygame.MOUSEMOTION:
                xpos = e.pos[0]
                pygame.draw.rect(screen_display, BLACK, (0, 0, width, SIZESQUARE))
                if turn == PLAYER:
                    pygame.draw.circle(screen_display, RED, (xpos, int(SIZESQUARE/2)), RADIUS)
            pygame.display.update()
                
            
            if e.type == pygame.MOUSEBUTTONDOWN:
                xpos = e.pos[0]
                pygame.draw.rect(screen_display, BLACK, (0, 0, width, SIZESQUARE))
                if turn == PLAYER:
                    col = int(math.floor(xpos/SIZESQUARE))
                    if is_valid_spot(board, col):
                        spot = get_open_row(board, col)
                        place_peice(board, spot, col, PLAYER_PEICE)
                        turn = AI

                        if win_checker(board, PLAYER_PEICE):
                            label = font.render("Player 1 wins!", 1, RED)
                            screen_display.blit(label, (140, 10))
                            is_game_over = True
                        elif check_tie(board):
                            label = font.render("Tie Game!", 1, RED)
                            screen_display.blit(label, (160, 10))
                            is_game_over = True
                        draw_board(board)
                            
        if turn == AI and not is_game_over:
            col, minimax_score = mini_max(board, 5, True, -math.inf, math.inf)
            if is_valid_spot(board, col):
                pygame.time.wait(400)
                spot = get_open_row(board, col)
                place_peice(board, spot, col, AI_PEICE)
                turn = PLAYER

                if win_checker(board, AI_PEICE):
                    label = font.render("AI wins!", 1, YELLOW)
                    screen_display.blit(label, (180, 10))
                    is_game_over = True
                elif check_tie(board):
                    label = font.render("Tie Game!", 1, RED)
                    screen_display.blit(label, (160, 10))
                    is_game_over = True

                draw_board(board)

        if is_game_over:
            pygame.time.wait(2000)
            clear_board(board)
            screen_display.fill(BLACK)
                    
main_menu()
