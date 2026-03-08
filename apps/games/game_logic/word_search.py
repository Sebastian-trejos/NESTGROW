import random
import string


def generate_word_search(words, grid_size=12):
    """
    Generate a word search puzzle.
    Returns: {'grid': [[...]], 'placed_words': [...], 'size': int}
    """
    words = [w.upper().replace(' ', '') for w in words if len(w) <= grid_size]
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    placed_words = []
    directions = [(0, 1), (1, 0), (1, 1), (0, -1), (-1, 0), (-1, -1), (1, -1), (-1, 1)]

    for word in words[:10]:  # Max 10 words
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            attempts += 1
            direction = random.choice(directions)
            dr, dc = direction
            max_r = grid_size - (len(word) * dr if dr > 0 else 0) - (abs(len(word) * dr) if dr < 0 else 0)
            max_c = grid_size - (len(word) * dc if dc > 0 else 0) - (abs(len(word) * dc) if dc < 0 else 0)
            if max_r <= 0 or max_c <= 0:
                continue
            row = random.randint(0, max_r - 1)
            col = random.randint(0, max_c - 1)

            # Check if word fits
            can_place = True
            for i, letter in enumerate(word):
                r, c = row + i * dr, col + i * dc
                if not (0 <= r < grid_size and 0 <= c < grid_size):
                    can_place = False
                    break
                if grid[r][c] not in (' ', letter):
                    can_place = False
                    break

            if can_place:
                positions = []
                for i, letter in enumerate(word):
                    r, c = row + i * dr, col + i * dc
                    grid[r][c] = letter
                    positions.append([r, c])
                placed_words.append({'word': word, 'positions': positions})
                placed = True

    # Fill remaining with random letters
    for r in range(grid_size):
        for c in range(grid_size):
            if grid[r][c] == ' ':
                grid[r][c] = random.choice(string.ascii_uppercase)

    return {
        'grid': grid,
        'placed_words': placed_words,
        'size': grid_size,
    }
