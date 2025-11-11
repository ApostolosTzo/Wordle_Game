import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import random
import time
from datetime import datetime
from pathlib import Path

WORDS_FILE = Path("words.txt")
PLACEMATE_FILE = Path("placemate.json")
ATTEMPTS = 6

# Window size (modify these to change the window dimensions)
WINDOW_WIDTH = 500   # Width in pixels
WINDOW_HEIGHT = 600  # Height in pixels

# Colors for feedback
COLOR_GREEN = "#6aaa64"
COLOR_YELLOW = "#c9b458"
COLOR_GRAY = "#787c7e"

def load_words(path):
    if not path.exists():                   # back up if the file is missing
        messagebox.showerror("Error", f"words file not found: {path}")
        return []
    words = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if len(w) == 5 and w.isalpha():
                words.append(w)
    if not words:
        messagebox.showerror("Error", "No valid 5-letter words found in words.txt")
    return words

def load_placemate(path):
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

def save_placemate(path, name, seconds):
    leaderboard = load_placemate(path)
    player_index = None
    for i, entry in enumerate(leaderboard):
        if entry.get("name") == name:
            player_index = i
            break
    new_entry = {
        "name": name,
        "time": float(seconds),
        "date": datetime.utcnow().isoformat() + "Z",
    }
    if player_index is not None:
        if seconds < leaderboard[player_index].get("time", float("inf")):
            leaderboard[player_index] = new_entry
    else:
        leaderboard.append(new_entry)
    leaderboard.sort(key=lambda x: x.get("time", float("inf")))
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=2)
    except Exception:
        print("Warning: could not save placemate record.")
 
class WordleGUI(tk.Tk):         # Main application class
    def __init__(self):
        super().__init__()
        self.title("Wordle Game")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")            # Set window size
        self.resizable(False, False)
        
        self.words = load_words(WORDS_FILE)
        self.player_name = ""
        self.leaderboard = []
        self.target = ""
        self.start_time = 0.0
        self.attempt = 1
        self.guess_rows = []  # For game screen
        
        self._build_main_screen()
    
    def _clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def _build_main_screen(self):       # Main menu
        self._clear_screen()
        title = tk.Label(self, text="WORDLE", font=("Arial", 32, "bold"))
        title.pack(pady=48)
        
        start_btn = tk.Button(self, text="Start", font=("Arial", 18), width=16, command=self._prompt_name)
        start_btn.pack(pady=18)
        
        leaderboard_btn = tk.Button(self, text="Leaderboard", font=("Arial", 18), width=16, command=self._show_leaderboard)
        leaderboard_btn.pack(pady=18)
        
        exit_btn = tk.Button(self, text="Exit", font=("Arial", 18), width=16, command=self.quit)
        exit_btn.pack(pady=18)
    
    def _prompt_name(self):            # Prompt for player name
        self._clear_screen()
        lbl = tk.Label(self, text="Enter your name:", font=("Arial", 20))
        lbl.pack(pady=50)
        name_var = tk.StringVar()       # Variable to hold name
        name_entry = tk.Entry(self, textvariable=name_var, font=("Arial", 16), justify="center")    # Entry field
        name_entry.pack(pady=16) 
        name_entry.focus_set()
        name_entry.bind("<Return>", lambda e: self._start_game(name_var.get()))  # Bind Enter key to start game
        join_btn = tk.Button(self, text="Join", font=("Arial", 18), width=12, command=lambda: self._start_game(name_var.get()))  # Join button
        join_btn.pack(pady=24)
        back_btn = tk.Button(self, text="Back", font=("Arial", 15), command=self._build_main_screen)
        back_btn.pack(pady=8)

    def _start_game(self, player_name):     # Start the game
        player_name = player_name.strip()
        if not player_name:
            player_name = "Anonymous"
        self.player_name = player_name
        self.target = random.choice(self.words)  # Choose target word
        self.start_time = time.perf_counter()    # Start timer
        self.attempt = 1
        self._build_game_screen()
    
    def _build_game_screen(self):                # Build the game screen
        self._clear_screen()
        top = tk.Frame(self)                     # Top frame for player info   
        top.pack(anchor="center", pady=8)
        details = f"Player: {self.player_name}   Attempts: {self.attempt}/{ATTEMPTS}"
        ttk = tk.Label(top, text=details, font=("Arial", 14))
        ttk.pack()
        
        self.time_label = tk.Label(top, text="Time: 0s", font=("Arial", 14))
        self.time_label.pack()
        self._update_timer()  # Start the timer

        game_frame = tk.Frame(self)         # Frame for guesses
        game_frame.pack(pady=16)
        self.guess_rows = []
        for i in range(ATTEMPTS):           # create 6 rows for guesses
            row = []
            f = tk.Frame(game_frame)
            f.pack(pady=2)
            for j in range(5):              # 5 letters per guess
                lbl = tk.Label(f, text=" ", font=("Consolas", 18, "bold"), width=3, height=1, relief="ridge", bd=2, bg="white")
                lbl.pack(side="left", padx=2)
                row.append(lbl)
            self.guess_rows.append(row)     # store row widgets

        entry_frame = tk.Frame(self)        # Frame for guess entry
        entry_frame.pack(pady=18)
        self.guess_var = tk.StringVar()     # Variable for guess entry
        guess_entry = tk.Entry(entry_frame, textvariable=self.guess_var, font=("Arial", 16), justify="center", width=8) # Entry field
        guess_entry.grid(row=0, column=0)
        guess_entry.focus_set()             # focus on entry
        guess_entry.bind("<Return>", lambda e: self._handle_guess())            # Bind Enter key to submit guess
        guess_btn = tk.Button(entry_frame, text="Guess", font=("Arial", 16), width=8, command=self._handle_guess)
        guess_btn.grid(row=0, column=1, padx=6)
        self.feedback_label = tk.Label(self, text="", font=("Arial", 13), fg="red") # Feedback label
        self.feedback_label.pack(pady=2)
        back_btn = tk.Button(self, text="Back", font=("Arial", 12), command=self._build_main_screen)
        back_btn.pack(side="bottom", pady=8)
    
    def _update_timer(self):                # Update the timer
        if self.start_time > 0:
            elapsed = time.perf_counter() - self.start_time
            self.time_label.config(text=f"Time: {elapsed:.1f}s")
            self.after(100, self._update_timer)  # Update every 100ms
    def _handle_guess(self):                # Handle a guess submission
        guess = self.guess_var.get().strip().lower()
        if len(guess) != 5 or not guess.isalpha():          # check input validity
            self.feedback_label.config(text="Please enter exactly 5 letters.")
            return
       # if guess not in self.words:
            self.feedback_label.config(text="Word not in list.")
            return

        # Show the guess in the appropriate row
        row_widgets = self.guess_rows[self.attempt - 1]
        feedback, colorings = self._format_feedback(guess, self.target)  # get feedback and colors
        for i in range(5):                                               # update each letter label
            row_widgets[i].config(text=guess[i].upper(),            
                                   bg=colorings[i],     
                                   fg="white" if colorings[i] != "white" else "black")              
        self.feedback_label.config(text="")
        self.guess_var.set("")  # Clear the entry field

        if guess == self.target:                # correct guess
            elapsed = time.perf_counter() - self.start_time     
            self._record_result(elapsed)            
            return
        self.attempt += 1                       # increment attempt

        if self.attempt > ATTEMPTS:             # out of tries
            messagebox.showinfo("Wordle", f"Out of tries.\nThe word was: {self.target.upper()}")        # show correct word
            self._build_main_screen()
        else:
            details = f"Player: {self.player_name}   Attempts: {self.attempt}/{ATTEMPTS}"               # update attempts display
            for widget in self.winfo_children():                                                        # update top label
                if isinstance(widget, tk.Frame):            
                    # Find relevant label
                    for child in widget.winfo_children():                                               # iterate children
                        if isinstance(child, tk.Label) and "Attempts" in child.cget("text"):            # find label
                            child.config(text=details)

    def _format_feedback(self, guess, target):                                                          # Format feedback for a guess
        feedback = [""] * 5
        colors = ["white"] * 5
        target_chars = list(target)
        used = [False] * 5

        # Greens
        for i, ch in enumerate(guess):
            if ch == target[i]:
                feedback[i] = ch.upper()
                colors[i] = COLOR_GREEN
                used[i] = True
                target_chars[i] = None

        # Yellows and grays
        for i, ch in enumerate(guess):
            if feedback[i]:
                continue
            if ch in target_chars:
                j = target_chars.index(ch)
                target_chars[j] = None
                feedback[i] = ch.upper()
                colors[i] = COLOR_YELLOW
            else:
                feedback[i] = ch.upper()
                colors[i] = COLOR_GRAY
        return feedback, colors

    def _record_result(self, elapsed):                      # Record the result and update leaderboard
        leaderboard = load_placemate(PLACEMATE_FILE)
        player_best = None
        for entry in leaderboard:
            if entry.get("name") == self.player_name:
                player_best = entry.get("time")
                break
        save_placemate(PLACEMATE_FILE, self.player_name, elapsed)
        msg = ""
        if player_best is None:
            msg = f"New player record!\nSaved {self.player_name} - {elapsed:.2f}s"
        elif elapsed < player_best:
            msg = f"New personal best!\n{self.player_name} - {elapsed:.2f}s (was {player_best:.2f}s)"
        else:
            msg = f"Good game!\nYour best is still {player_best:.2f}s"
        messagebox.showinfo("Wordle", f"Correct! You found the word.\nYour time: {elapsed:.2f} seconds\n{msg}")
        self._build_main_screen()

    def _show_leaderboard(self):
        self._clear_screen()
        leaderboard = load_placemate(PLACEMATE_FILE)
        title = tk.Label(self, text="Leaderboard", font=("Arial", 25, "bold"))
        title.pack(pady=20)
        frame = tk.Frame(self)
        frame.pack()

        if not leaderboard:
            lbl = tk.Label(frame, text="No placemate record yet.", font=("Arial", 17))
            lbl.pack(pady=30)
        else:
            header = tk.Label(frame, text=f"{'Rank':<5}{'Name':<16}{'Time(s)':<10}{'Date'}", font=("Consolas", 14, "bold"))
            header.pack()
            for i, entry in enumerate(leaderboard[:10], 1):
                name = entry.get("name", "Unknown")
                time_sec = entry.get("time", 0)
                date = entry.get("date", "")
                s = f"{i:>2}    {name:<16}{time_sec:7.2f}   {date[:19]}"
                lbl = tk.Label(frame, text=s, font=("Consolas", 13))
                lbl.pack(anchor="w")

        back_btn = tk.Button(self, text="Back", font=("Arial", 13), command=self._build_main_screen)
        back_btn.pack(pady=16, side="bottom")

if __name__ == "__main__":
    import sys
    
    # Parse command-line arguments for window size
    # Usage: python wordle_gui.py [width] [height]
    # Example: python wordle_gui.py 500 600
    if len(sys.argv) >= 3:
        try:
            WINDOW_WIDTH = int(sys.argv[1])
            WINDOW_HEIGHT = int(sys.argv[2])
        except ValueError:
            print("Invalid arguments. Usage: python wordle_gui.py [width] [height]")
            print(f"Using default size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    
    app = WordleGUI()
    app.mainloop()