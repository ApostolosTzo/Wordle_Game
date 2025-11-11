import random
import sys
import time
import json
from datetime import datetime
from pathlib import Path

WORDS_FILE = Path("words.txt")
ATTEMPTS = 6
PLACEMATE_FILE = Path("placemate.json")

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

    Returns a list of dicts with keys: name (str), time (float seconds), date (iso str)
    or an empty list if file doesn't exist or is invalid.
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


def save_placemate(path: Path, name: str, seconds: float):
    """Save or update a player's best time in the leaderboard.
    
    If the player already exists, update their time only if the new time is faster.
    If the player is new, add them to the list.
    """
    leaderboard = load_placemate(path)
    
    # Find if player already exists
    player_index = None
    for i, entry in enumerate(leaderboard):
        if entry.get("name") == name:
            player_index = i
            break
    
    # Create new entry
    new_entry = {
        "name": name,
        "time": float(seconds),
        "date": datetime.utcnow().isoformat() + "Z",
    }
    
    if player_index is not None:
        # Player exists; update only if new time is faster
        if seconds < leaderboard[player_index].get("time", float("inf")):
            leaderboard[player_index] = new_entry
    else:
        # New player
        leaderboard.append(new_entry)
    
    # Sort by time (fastest first)
    leaderboard.sort(key=lambda x: x.get("time", float("inf")))
    
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=2)
    except Exception:
        # If we can't write, don't crash the game; print a warning
        print("Warning: could not save placemate record.")


def display_top_10(leaderboard):
    """Display the top 10 fastest times from the leaderboard."""
    if not leaderboard:
        print("No placemate record yet. Be the first to set a fastest time!")
        return
    
    print("\n" + "="*50)
    print("TOP 10 FASTEST TIMES - LEADERBOARD")
    print("="*50)
    
    for i, entry in enumerate(leaderboard[:10], 1):
        name = entry.get("name", "Unknown")
        time_sec = entry.get("time", 0)
        date = entry.get("date", "unknown")
        print(f"{i:2d}. {name:20s} - {time_sec:7.2f}s  ({date})")
    
    print("="*50 + "\n")


def format_feedback(guess, target):
    # Standard Wordle marking: first mark greens, then mark yellows taking counts into account
    
    feedback = [""] * 5                 # Initialize feedback list
    target_chars = list(target)         # Make a mutable copy of target letters
    used = [False] * 5                  # Track which letters in target have been used

    # Greens
    for i, ch in enumerate(guess):
        if ch == target[i]:                             # check for green matches
            feedback[i] = GREEN + ch.upper() + RESET    # Mark green   RESET color back to normal
            used[i] = True                              # Mark this letter as used
            target_chars[i] = None                      # Remove from consideration

    # Yellows and grays
    for i, ch in enumerate(guess): 
        if feedback[i]:                                 # already marked green
            continue
        if ch in target_chars:                          # check for yellow matches
            # consume first unmatched occurrence
            j = target_chars.index(ch) 
            target_chars[j] = None                      # Remove from consideration
            feedback[i] = YELLOW + ch.upper() + RESET   # Mark yellow
        else:
            feedback[i] = GRAY + ch.upper() + RESET     # Mark gray

    return "".join(feedback)                            # Join feedback list into a string   

def main():
    words = load_words(WORDS_FILE)
    target = random.choice(words)
    # Uncomment for debugging:
    # print("(debug) target:", target)

    # Load and display leaderboard (top 10)
    leaderboard = load_placemate(PLACEMATE_FILE)
    display_top_10(leaderboard)

    # Ask for player name
    player = input("Enter your name (used for the placemate): ").strip()
    if not player:
        player = "Anonymous"

    print("Guess the 5-letter word. You have 6 tries.")

    # start timing from the beginning of the game (until correct guess)
    start_time = time.perf_counter()

    for turn in range(1, ATTEMPTS + 1):                                             # loop for each attempt
        while True:         
            guess = input(f"[{turn}/{ATTEMPTS}] Enter guess: ").strip().lower()     # get user input
            if len(guess) != 5 or not guess.isalpha():                              # check input validity
                print("Please enter exactly 5 letters.")
                continue
            if guess not in words:
                print("Word not in list. (Make sure words.txt contains common guesses.)")
                continue
            break
            # valid guess entered
        print(format_feedback(guess, target))
        if guess == target:             
            elapsed = time.perf_counter() - start_time                                # calculate elapsed time
            print(f"Correct! You found the word in {turn} {'try' if turn==1 else 'tries'}.")
            print(f"Your time: {elapsed:.2f} seconds")

            # Reload leaderboard to check current state
            leaderboard = load_placemate(PLACEMATE_FILE)
            
            # Find if player already exists
            player_best = None
            for entry in leaderboard:
                if entry.get("name") == player:
                    player_best = entry.get("time")
                    break
            
            # Check if this is a new personal best
            if player_best is None:
                # New player
                save_placemate(PLACEMATE_FILE, player, elapsed)
                print(f"🎉 New player record! Saved {player} - {elapsed:.2f}s")
            elif elapsed < player_best:
                # Improved personal best
                save_placemate(PLACEMATE_FILE, player, elapsed)
                print(f"🎉 New personal best! {player} - {elapsed:.2f}s (was {player_best:.2f}s)")
            else:
                # Didn't beat personal best
                print(f"Good game! Your best is still {player_best:.2f}s")
            
            return

    # Out of tries
    print(f"Out of tries. The word was: {target.upper()}")



if __name__ == "__main__":
    main()