import numpy as np
import pygame
import math
import sys
import button as button
import random

# Initialize Pygame
pygame.init()

# Constants for screen dimensions
SQUARESIZE = 100
COLUMN_COUNT = 7
ROW_COUNT = 6
RADIUS = int(SQUARESIZE / 2 - 5)
SCREEN_WIDTH = COLUMN_COUNT*SQUARESIZE
SCREEN_HEIGHT = (ROW_COUNT+1)*SQUARESIZE


depth = 1
size=(SCREEN_WIDTH,SCREEN_HEIGHT)


# Colors
BACKGROUND=(202, 228, 241)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Player constants
PLAYER = 0
AI = 1
PLAYER_PIECE = 1
AI_PIECE = 2
EMPTY = 0

# Font
pygame.font.init()
font = pygame.font.SysFont("arial", 75)

# Function to create the game board
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

# Function to drop a piece onto the board
def drop_piece(board, row, col, piece):
    board[row][col] = piece

# Function to check if a location is valid for dropping a piece
def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == EMPTY

# Function to get the next open row in a column
def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r

# Function to print the board
def print_board(board):
    print(np.flip(board, 0))

# Function to check if a player has won
def winning_move(board, piece):
    
    # Check horizontal
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - connect + 1):
            if all(board[r][c + i] == piece for i in range(connect)):
                return True

    # Check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - connect + 1):
            if all(board[r + i][c] == piece for i in range(connect)):
                return True

    # Check positively sloped diagonals
    for r in range(ROW_COUNT - connect + 1):
        for c in range(COLUMN_COUNT - connect + 1):
            if all(board[r + i][c + i] == piece for i in range(connect)):
                return True

    # Check negatively sloped diagonals
    for r in range(connect - 1, ROW_COUNT):
        for c in range(COLUMN_COUNT - connect + 1):
            if all(board[r - i][c + i] == piece for i in range(connect)):
                return True

    return False

# Function to evaluate a window for scoring
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == connect:
        score += 100
    elif window.count(piece) == connect-1 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == connect-2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == connect-1 and window.count(EMPTY) == 1:
        score -= 4

    return score

# Function to score the position of a board
def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT // 2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - connect + 1):  # Adjusted range
            window = row_array[c:c + connect]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - connect + 1):  # Adjusted range
            window = col_array[r:r + connect]
            score += evaluate_window(window, piece)

    # Score positively sloped diagonals
    for r in range(ROW_COUNT - connect + 1):  # Adjusted range
        for c in range(COLUMN_COUNT - connect + 1):  # Adjusted range
            window = [board[r + i][c + i] for i in range(connect)]
            score += evaluate_window(window, piece)

    # Score negatively sloped diagonals
    for r in range(ROW_COUNT - connect + 1):  # Adjusted range
        for c in range(COLUMN_COUNT - connect + 1):  # Adjusted range
            window = [board[r + connect - 1 - i][c + i] for i in range(connect)]  # Adjusted range
            score += evaluate_window(window, piece)

    return score

# Function to check if the game is in a terminal state
def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

# Function to get valid locations for dropping a piece
def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

# Function for the AI to pick the best move using minimax algorithm
def minimax(board, depth, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return None, 100000
            elif winning_move(board, PLAYER_PIECE):
                return None, -100000
            else:
                return None, 0
        else:
            return None, score_position(board, AI_PIECE)

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
        return best_col, value
    else:  # MinimizingPlayer
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
        return best_col, value

# Function to pick the best move for the AI
def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

# Function to draw the Connect Four board
def draw_board(board, screen):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BACKGROUND, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), SCREEN_HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), SCREEN_HEIGHT - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

# Function to play the Connect Four game
def play_game(screen):
    # Create the Connect Four board
    board = create_board()

    # Draw the initial empty board
    draw_board(board, screen)
    pygame.display.update()

    game_over = False
    turn = random.randint(PLAYER, AI)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BACKGROUND, (0, 0, SCREEN_WIDTH, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
                pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BACKGROUND, (0, 0, SCREEN_WIDTH, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    col = int(math.floor(posx / SQUARESIZE))
                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)

                        if winning_move(board, PLAYER_PIECE):
                            label = font.render("Player 1 wins!!!", 1, RED)
                            screen.blit(label, (40, 10))
                            game_over = True
                        elif len(get_valid_locations(board)) == 0:  # Check for draw
                            label = font.render("It's a draw!", 1, BACKGROUND)
                            screen.blit(label, (40, 10))
                            game_over = True

                        turn += 1
                        turn %= 2

                        print_board(board)
                        draw_board(board, screen)
                        pygame.display.update()

        if turn == AI and not game_over:
            print(depth)
            col, minimax_score = minimax(board, depth, True)
            if is_valid_location(board, col):
                pygame.time.wait(500)
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                if winning_move(board, AI_PIECE):
                    label = font.render("Player 2 wins!!!", 1, YELLOW)
                    screen.blit(label, (40, 10))
                    game_over = True
                elif len(get_valid_locations(board)) == 0:  # Check for draw
                    label = font.render("It's a draw!", 1, BACKGROUND)
                    screen.blit(label, (40, 10))
                    game_over = True

                print_board(board)
                draw_board(board, screen)
                pygame.display.update()

                turn += 1
                turn %= 2

        if game_over:
            pygame.time.wait(1500)

# Function to select the difficulty level
def select_level(screen):
    while True:
        screen.fill(BACKGROUND)  # Fill screen with white

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                global depth
                if easy_button.draw(screen):
                    depth = 1
                elif medium_button.draw(screen):
                    depth = 2
                elif hard_button.draw(screen):
                    depth = 3
                main_menu(screen)

        # Update display
        screen.fill(BACKGROUND)  # Fill screen with background color
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)
        pygame.display.update()

# Function for the main menu
def main_menu(screen):
    # Game loop
    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:
                global connect
                if conn4_button.draw(screen):
                    connect=4
                    play_game(screen)
                elif conn5_button.draw(screen):
                    connect=5
                    play_game(screen)
                elif level_button.draw(screen):
                    select_level(screen)
                elif exit_button.draw(screen):
                    pygame.quit()
                    return

        # Update display
        screen.fill(BACKGROUND)  # Fill screen with background color
        conn4_button.draw(screen)
        conn5_button.draw(screen)
        level_button.draw(screen)
        exit_button.draw(screen)
        pygame.display.update()

# Set up screen
screen_width=COLUMN_COUNT*SQUARESIZE
screen_height=(ROW_COUNT+1)*SQUARESIZE

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Button Demo')

# Load images
conn4_img = pygame.image.load('Connect/conn4.png').convert_alpha()
conn5_img = pygame.image.load('Connect/conn5.png').convert_alpha()
level_img = pygame.image.load('Connect/level.png').convert_alpha()
exit_img = pygame.image.load('Connect/exit.png').convert_alpha()
easy_img = pygame.image.load('Connect/easy.png').convert_alpha()
medium_img = pygame.image.load('Connect/medium.png').convert_alpha()
hard_img = pygame.image.load('Connect/hard.png').convert_alpha()

# Create button instances
conn4_button=button.Button(250, 200, conn4_img,1.2)
conn5_button=button.Button(250, 300, conn5_img, 1.2)
level_button = button.Button(250, 400, level_img, 1.2)
exit_button = button.Button(250, 500, exit_img, 1.2)
easy_button = button.Button(250, 200, easy_img, 1.2)
medium_button = button.Button(250, 300, medium_img, 1.2)
hard_button = button.Button(250, 400, hard_img, 1.2)

# Call main menu function to run the game
if __name__ == "__main__":
    main_menu(screen)
