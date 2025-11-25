import tkinter as tk 
from tkinter import messagebox, simpledialog
import json
import random
import time
from datetime import datetime
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent

WORDS_EASY_FILE = SCRIPT_DIR / "words_easy_mode.txt"
WORDS_MEDIUM_FILE = SCRIPT_DIR / "words_medium_mode.txt"
ALL_WORDS_FILE = SCRIPT_DIR / "All_the_Words.txt"
PLACEMATE_FILE = SCRIPT_DIR / "placemate.json"

# Window size
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 750

# Colors for feedback
COLOR_GREEN = "#6aaa64"
COLOR_YELLOW = "#c9b458"
COLOR_GRAY = "#787c7e"
COLOR_DEFAULT = "#d3d6da"

def load_words(path):
    if not path.exists():
        messagebox.showerror("Error", f"words file not found: {path}")
        return []
    words = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            w = line.strip().lower()
            if len(w) == 5 and w.isalpha():
                words.append(w)
    if not words:
        messagebox.showerror("Error", f"No valid 5-letter words found in {path.name}")
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

def save_placemate(path, name, seconds, mode):
    leaderboard = load_placemate(path)
    player_index = None
    
    # Check for player entry specifically for this mode
    for i, entry in enumerate(leaderboard):
        entry_mode = entry.get("mode", "Easy") # Default to Easy if missing
        if entry.get("name") == name and entry_mode == mode:
            player_index = i
            break
            
    new_entry = {
        "name": name,
        "time": float(seconds),
        "date": datetime.utcnow().isoformat() + "Z",
        "mode": mode
    }
    
    if player_index is not None:
        if seconds < leaderboard[player_index].get("time", float("inf")):
            leaderboard[player_index] = new_entry
    else:
        leaderboard.append(new_entry)
        
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(leaderboard, f, indent=2)
    except Exception:
        print("Warning: could not save placemate record.")
 
class WordleGUI(tk.Tk):         # Main application class
    def __init__(self):
        super().__init__()
        self.title("Wordle Game")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        
        # Load two word lists
        self.target_words = load_words(WORDS_EASY_FILE)
        self.valid_words = load_words(ALL_WORDS_FILE)
        self.player_name = ""
        self.target = ""
        self.start_time = 0.0
        self.attempt = 1
        
        # Game Settings
        self.selected_difficulty = tk.StringVar(value="Easy") # Default to Easy
        self.max_attempts = 6 # Default 6
        
        self.guess_rows = []
        self.details_label = None
        self.keyboard_buttons = {}
        self.letter_status = {}
        
        self._build_main_screen()
    
    def _clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()
    
    def _build_main_screen(self):       # Main menu
        self._clear_screen()
        title = tk.Label(self, text="WORDLE", font=("Arial", 32, "bold"))
        title.pack(pady=40)
        
        # Difficulty Selection
        diff_frame = tk.Frame(self)
        diff_frame.pack(pady=10)
        tk.Label(diff_frame, text="Select Difficulty:", font=("Arial", 14)).pack(anchor="w")
        
        tk.Radiobutton(diff_frame, text="Easy (6 Attempts)", variable=self.selected_difficulty, 
                      value="Easy", font=("Arial", 12)).pack(anchor="w")
        tk.Radiobutton(diff_frame, text="Medium (4 Attempts)", variable=self.selected_difficulty, 
                      value="Medium", font=("Arial", 12)).pack(anchor="w")

        start_btn = tk.Button(self, text="Start", font=("Arial", 18), width=16, command=self._prompt_name)
        start_btn.pack(pady=18)
        
        leaderboard_btn = tk.Button(self, text="Leaderboard", font=("Arial", 18), width=16, command=self._show_leaderboard_screen)
        leaderboard_btn.pack(pady=18)
        
        exit_btn = tk.Button(self, text="Exit", font=("Arial", 18), width=16, command=self.quit)
        exit_btn.pack(pady=18)
    
    def _prompt_name(self):            # Prompt for player name
        self._clear_screen()
        lbl = tk.Label(self, text="Enter your name:", font=("Arial", 20))
        lbl.pack(pady=50)
        name_var = tk.StringVar()
        name_entry = tk.Entry(self, textvariable=name_var, font=("Arial", 16), justify="center")
        name_entry.pack(pady=16) 
        name_entry.focus_set()
        
        # Set attempts based on selection
        mode = self.selected_difficulty.get()
        if mode == "Medium":
            self.max_attempts = 4
        else:
            self.max_attempts = 6

        name_entry.bind("<Return>", lambda e: self._start_game(name_var.get()))
        join_btn = tk.Button(self, text=f"Play ({mode})", font=("Arial", 18), width=12, command=lambda: self._start_game(name_var.get()))
        join_btn.pack(pady=24)
        back_btn = tk.Button(self, text="Back", font=("Arial", 15), command=self._build_main_screen)
        back_btn.pack(pady=8)

    def _start_game(self, player_name):     # Start the game
        player_name = player_name.strip()
        if not player_name:
            player_name = "Anonymous"
        self.player_name = player_name
        
        # Load the correct word list based on difficulty
        mode = self.selected_difficulty.get()
        if mode == "Medium":
            self.target_words = load_words(WORDS_MEDIUM_FILE)
        else:  # Easy
            self.target_words = load_words(WORDS_EASY_FILE)
        
        # Load all valid words for guess validation
        self.valid_words = load_words(ALL_WORDS_FILE)
        
        if not self.target_words:
            messagebox.showerror("Error", "No target words available. Cannot start game.")
            self._build_main_screen()
            return
        
        self.target = random.choice(self.target_words)
        self.start_time = time.perf_counter()
        self.attempt = 1
        self.letter_status = {}
        self._build_game_screen()
    
    def _build_game_screen(self):                # Build the game screen
        self._clear_screen()
        top = tk.Frame(self)
        top.pack(anchor="center", pady=8)
        
        mode = self.selected_difficulty.get()
        details = f"Player: {self.player_name} ({mode})  Attempts: {self.attempt}/{self.max_attempts}"
        self.details_label = tk.Label(top, text=details, font=("Arial", 14))
        self.details_label.pack()
        
        self._update_timer()

        game_frame = tk.Frame(self)
        game_frame.pack(pady=16)
        self.guess_rows = []
        
        # Create dynamic number of rows based on max_attempts
        for i in range(self.max_attempts):
            row = []
            f = tk.Frame(game_frame)
            f.pack(pady=2)
            for j in range(5):
                lbl = tk.Label(f, text=" ", font=("Consolas", 18, "bold"), width=3, height=1, relief="ridge", bd=2, bg="white")
                lbl.pack(side="left", padx=2)
                row.append(lbl)
            self.guess_rows.append(row)

        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=12)
        self.guess_var = tk.StringVar()
        guess_entry = tk.Entry(entry_frame, textvariable=self.guess_var, font=("Arial", 16), justify="center", width=8)
        guess_entry.grid(row=0, column=0)
        guess_entry.focus_set()
        guess_entry.bind("<Return>", lambda e: self._handle_guess())
        guess_btn = tk.Button(entry_frame, text="Guess", font=("Arial", 16), width=8, command=self._handle_guess)
        guess_btn.grid(row=0, column=1, padx=6)
        
        self.feedback_label = tk.Label(self, text="", font=("Arial", 13), fg="red")
        self.feedback_label.pack(pady=2)
        
        self._build_keyboard()
        
        back_btn = tk.Button(self, text="Main Menu", font=("Arial", 12), command=self._build_main_screen)
        back_btn.pack(side="bottom", pady=8)
    
    def _build_keyboard(self):
        keyboard_frame = tk.Frame(self)
        keyboard_frame.pack(pady=8)
        
        rows = [
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L'],
            ['Z', 'X', 'C', 'V', 'B', 'N', 'M']
        ]
        
        for row in rows:
            row_frame = tk.Frame(keyboard_frame)   
            row_frame.pack(pady=2) 
            for letter in row:
                btn = tk.Button(
                    row_frame,
                    text=letter,
                    font=("Arial", 10, "bold"),
                    width=4,
                    height=2,
                    bg=COLOR_DEFAULT,
                    fg="black",
                    relief="raised",
                    bd=1
                )
                btn.pack(side="left", padx=1)
                self.keyboard_buttons[letter] = btn
    
    def _update_keyboard_colors(self, guess, feedback_colors):  
        for i, letter in enumerate(guess):
            letter_upper = letter.upper()
            color = feedback_colors[i]
            
            if letter_upper in self.letter_status:
                current = self.letter_status[letter_upper]
                if color == COLOR_GREEN:
                    self.letter_status[letter_upper] = COLOR_GREEN
                elif color == COLOR_YELLOW and current != COLOR_GREEN:
                    self.letter_status[letter_upper] = COLOR_YELLOW
                elif color == COLOR_GRAY and current == COLOR_DEFAULT:
                    self.letter_status[letter_upper] = COLOR_GRAY
            else:
                self.letter_status[letter_upper] = color
            
            if letter_upper in self.keyboard_buttons:
                btn = self.keyboard_buttons[letter_upper]
                btn.config(bg=self.letter_status[letter_upper], fg="white")
    
    def _update_timer(self):
        if self.start_time > 0:
            elapsed = time.perf_counter() - self.start_time
            # Keep calling recursively if we are still in game screen
            # (simple check: if details_label exists)
            if self.details_label and self.details_label.winfo_exists():
                self.after(100, self._update_timer)
    
    def _handle_guess(self):
        guess = self.guess_var.get().strip().lower()
        if len(guess) != 5 or not guess.isalpha():
            self.feedback_label.config(text="Please enter exactly 5 letters.")
            return
        
        if guess not in self.valid_words:
            self.feedback_label.config(text="Word doesn't exist in the database.")
            return

        row_widgets = self.guess_rows[self.attempt - 1]
        feedback, colorings = self._format_feedback(guess, self.target)
        for i in range(5):
            row_widgets[i].config(text=guess[i].upper(),            
                                   bg=colorings[i],     
                                   fg="white" if colorings[i] != "white" else "black")
        
        self._update_keyboard_colors(guess, colorings)
        
        self.feedback_label.config(text="")
        self.guess_var.set("")

        if guess == self.target:
            elapsed = time.perf_counter() - self.start_time     
            self._record_result(elapsed)            
            return
        self.attempt += 1

        if self.attempt > self.max_attempts:
            messagebox.showinfo("Wordle", f"Out of tries.\nThe word was: {self.target.upper()}")
            self._build_main_screen()
        else:
            mode = self.selected_difficulty.get()
            details = f"Player: {self.player_name} ({mode})  Attempts: {self.attempt}/{self.max_attempts}"
            self.details_label.config(text=details)

    def _format_feedback(self, guess, target):
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

    def _record_result(self, elapsed):
        mode = self.selected_difficulty.get()
        leaderboard = load_placemate(PLACEMATE_FILE)
        
        # Check PB for this mode
        player_best = None
        for entry in leaderboard:
            entry_mode = entry.get("mode", "Easy")
            if entry.get("name") == self.player_name and entry_mode == mode:
                player_best = entry.get("time")
                break
                
        save_placemate(PLACEMATE_FILE, self.player_name, elapsed, mode)
        
        msg = ""
        if player_best is None:
            msg = f"New {mode} record!\nSaved {self.player_name} - {elapsed:.2f}s"
        elif elapsed < player_best:
            msg = f"New {mode} PB!\n{self.player_name} - {elapsed:.2f}s (was {player_best:.2f}s)"
        else:
            msg = f"Good game!\nYour {mode} best is still {player_best:.2f}s"
            
        messagebox.showinfo("Wordle", f"Correct! You found the word.\nYour time: {elapsed:.2f} seconds\n{msg}")
        self._build_main_screen()

    def _show_leaderboard_screen(self, default_mode="Easy"):
        self._clear_screen()
        leaderboard = load_placemate(PLACEMATE_FILE)
        
        title = tk.Label(self, text="Leaderboard", font=("Arial", 25, "bold"))
        title.pack(pady=10)
        
        # Mode switch buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=5)
        
        # Helper to refresh the list part only
        def refresh_list(mode):
            # Clear previous list
            for widget in list_frame.winfo_children():
                widget.destroy()
                
            # Filter and sort
            filtered = [e for e in leaderboard if e.get("mode", "Easy") == mode]
            filtered.sort(key=lambda x: x.get("time", float("inf")))
            
            header = tk.Label(list_frame, text=f"{mode.upper()} MODE", font=("Arial", 12, "bold"), fg="#555")
            header.pack(pady=5)

            if not filtered:
                lbl = tk.Label(list_frame, text=f"No {mode} records yet.", font=("Arial", 14))
                lbl.pack(pady=20)
            else:
                head_str = f"{'Rank':<5}{'Name':<14}{'Time(s)':<10}{'Date'}"
                tk.Label(list_frame, text=head_str, font=("Consolas", 12, "bold")).pack()
                
                for i, entry in enumerate(filtered[:10], 1):
                    name = entry.get("name", "Unknown")
                    time_sec = entry.get("time", 0)
                    date = entry.get("date", "")
                    s = f"{i:>2}    {name:<14}{time_sec:7.2f}   {date[:10]}"
                    lbl = tk.Label(list_frame, text=s, font=("Consolas", 12))
                    lbl.pack(anchor="w", padx=20)

        # Buttons
        b1 = tk.Button(btn_frame, text="Easy (6)", command=lambda: refresh_list("Easy"))
        b1.pack(side="left", padx=10)
        b2 = tk.Button(btn_frame, text="Medium (4)", command=lambda: refresh_list("Medium"))
        b2.pack(side="left", padx=10)

        list_frame = tk.Frame(self)
        list_frame.pack(pady=10, fill="both", expand=True)

        # Show default
        refresh_list(default_mode)

        back_btn = tk.Button(self, text="Back", font=("Arial", 13), command=self._build_main_screen)
        back_btn.pack(pady=16, side="bottom")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) >= 3:
        try:
            WINDOW_WIDTH = int(sys.argv[1])
            WINDOW_HEIGHT = int(sys.argv[2])
        except ValueError:
            print("Invalid arguments. Usage: python wordle_gui.py [width] [height]")
    
    app = WordleGUI()
    app.mainloop()