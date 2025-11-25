import random
import sys
import time
import json
from datetime import datetime
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent 
# File paths
WORDS_EASY_FILE = SCRIPT_DIR / "words_easy_mode.txt"
WORDS_MEDIUM_FILE = SCRIPT_DIR / "words_medium_mode.txt"
ALL_WORDS_FILE = SCRIPT_DIR / "All_the_Words.txt"
PLACEMATE_FILE = SCRIPT_DIR / "placemate.json"

GREEN = "\x1b[42m\x1b[30m"   # green bg, black text
YELLOW = "\x1b[43m\x1b[30m"  # yellow bg, black text
GRAY = "\x1b[100m\x1b[37m"   # dark gray bg, white text
RESET = "\x1b[0m"

def load_words(path):
    if not path.exists(): # back up if the file is missing
        print(f"words file not found: {path}")
        sys.exit(1)
    words = []
    with path.open(encoding="utf-8") as f:
        # loop through each line in the file
        for line in f:
            w = line.strip().lower()
            # check if the word is 5 letters and alphabetic
            if len(w) == 5 and w.isalpha():
              words.append(w)
    # add to the list
    if not words:
        print("No valid 5-letter words found in words.txt")
        sys.exit(1)
    return words


def load_placemate(path: Path):
    """Load the leaderboard from placemate.json.

    Returns a list of dicts.
    """
    if not path.exists():
        return []
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def save_placemate(path: Path, name: str, seconds: float, mode: str):
    """Save or update a player's best time in the leaderboard for a specific mode.
    
    Now includes 'mode' (Easy/Medium) to distinguish records.
    """
    leaderboard = load_placemate(path)
    
    # Find if player already exists for this specific mode
    player_index = None
    for i, entry in enumerate(leaderboard):
        # We assume entries without a 'mode' key are 'Easy' (legacy support)
        entry_mode = entry.get("mode", "Easy")
        if entry.get("name") == name and entry_mode == mode:
            player_index = i
            break
    
    # Create new entry
    new_entry = {
        "name": name,
        "time": float(seconds),
        "date": datetime.utcnow().isoformat() + "Z",
        "mode": mode  # Save the difficulty mode
    }
    
    if player_index is not None:
        # Player exists in this mode; update only if new time is faster
        if seconds < leaderboard[player_index].get("time", float("inf")):
            leaderboard[player_index] = new_entry
    else:
        # New player for this mode
        leaderboard.append(new_entry)
    
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=2)
    except Exception:
        print("Warning: could not save placemate record.")


def display_top_10(leaderboard, mode):
    """Display the top 10 fastest times for the specific difficulty mode."""
    # Filter leaderboard for the requested mode
    # We treat missing 'mode' keys as 'Easy' so old records still show up in Easy
    filtered_board = [
        entry for entry in leaderboard 
        if entry.get("mode", "Easy") == mode
    ]
    
    # Sort by time
    filtered_board.sort(key=lambda x: x.get("time", float("inf")))

    print("\n" + "="*60)
    print(f"TOP 10 FASTEST TIMES - {mode.upper()} MODE")
    print("="*60)
    
    if not filtered_board:
        print(f"No records for {mode} mode yet.")
    
    for i, entry in enumerate(filtered_board[:10], 1):
        name = entry.get("name", "Unknown")
        time_sec = entry.get("time", 0)
        date = entry.get("date", "unknown")
        print(f"{i:2d}. {name:20s} - {time_sec:7.2f}s  ({date})")
    
    print("="*60 + "\n")


def format_feedback(guess, target):
    # Standard Wordle marking
    feedback = [""] * 5
    target_chars = list(target)
    used = [False] * 5

    # Greens
    for i, ch in enumerate(guess):
        if ch == target[i]:
            feedback[i] = GREEN + ch.upper() + RESET
            used[i] = True
            target_chars[i] = None

    # Yellows and grays
    for i, ch in enumerate(guess): 
        if feedback[i]:
            continue
        if ch in target_chars:
            j = target_chars.index(ch) 
            target_chars[j] = None
            feedback[i] = YELLOW + ch.upper() + RESET
        else:
            feedback[i] = GRAY + ch.upper() + RESET

    return "".join(feedback)

def get_difficulty():
    """Ask user to select difficulty."""
    while True:
        print("\nSelect Difficulty:")
        print("1. Easy (6 attempts)")
        print("2. Medium (4 attempts)")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return 6, "Easy"
        elif choice == "2":
            return 4, "Medium"
        else:
            print("Invalid choice. Please enter 1 or 2.")

def main():
    # Select difficulty first
    attempts_allowed, mode_name = get_difficulty()
    
    # Load the correct word list based on difficulty
    if mode_name == "Easy":
        target_words = load_words(WORDS_EASY_FILE)
    else:  # Medium
        target_words = load_words(WORDS_MEDIUM_FILE)
    
    # Load all valid words for guess validation
    valid_words = load_words(ALL_WORDS_FILE)
    
    target = random.choice(target_words)
    # Uncomment for debugging:
    # print("(debug) target:", target)

    # Load and display leaderboard for the selected mode
    leaderboard = load_placemate(PLACEMATE_FILE)
    display_top_10(leaderboard, mode_name)

    # Ask for player name
    player = input("Enter your name (used for the leaderboard): ").strip()
    if not player:
        player = "Anonymous"

    print(f"Guess the 5-letter word. You have {attempts_allowed} tries ({mode_name} Mode).")

    start_time = time.perf_counter()

    for turn in range(1, attempts_allowed + 1):
        while True:         
            guess = input(f"[{turn}/{attempts_allowed}] Enter guess: ").strip().lower()
            if len(guess) != 5 or not guess.isalpha():
                print("Please enter exactly 5 letters.")
                continue
            if guess not in valid_words:
                print("Word not in list.")
                continue
            break
        
        print(format_feedback(guess, target))
        
        if guess == target:             
            elapsed = time.perf_counter() - start_time
            print(f"Correct! You found the word in {turn} {'try' if turn==1 else 'tries'}.")
            print(f"Your time: {elapsed:.2f} seconds")

            # Reload to get latest data
            leaderboard = load_placemate(PLACEMATE_FILE)
            
            # Find best time for this specific mode
            player_best = None
            for entry in leaderboard:
                entry_mode = entry.get("mode", "Easy")
                if entry.get("name") == player and entry_mode == mode_name:
                    player_best = entry.get("time")
                    break
            
            # Check if record
            if player_best is None:
                save_placemate(PLACEMATE_FILE, player, elapsed, mode_name)
                print(f"🎉 New {mode_name} record! Saved {player} - {elapsed:.2f}s")
            elif elapsed < player_best:
                save_placemate(PLACEMATE_FILE, player, elapsed, mode_name)
                print(f"🎉 New {mode_name} personal best! {player} - {elapsed:.2f}s (was {player_best:.2f}s)")
            else:
                print(f"Good game! Your {mode_name} best is still {player_best:.2f}s")
            
            return

    print(f"Out of tries. The word was: {target.upper()}")

if __name__ == "__main__":
    main()