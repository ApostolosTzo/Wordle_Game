# 🟩 Python Wordle Clone

A full-featured clone of the popular game **Wordle**, built with Python. This project offers two ways to play: a **Terminal-based (CLI) version** for quick play and a **Graphical User Interface (GUI)** version built with Tkinter.

Both versions feature a persistent **Leaderboard (Placemate)** that tracks the fastest solve times.

## 🚀 Features

* **Dual Modes:** Play in your terminal or via a windowed application.
* **Speed-Run Leaderboard:** Tracks the fastest completion times in `placemate.json`.
* **Standard Wordle Rules:** 6 attempts to guess a 5-letter word.
* **Feedback System:**
    * 🟩 **Green:** Correct letter, correct spot.
    * 🟨 **Yellow:** Correct letter, wrong spot.
    * ⬜ **Gray:** Letter not in the word.
* **Input Validation:** Checks if the word is 5 letters long and exists in the dictionary.

---

## 📂 Project Structure

| File | Description |
| :--- | :--- |
| `Wordle.py` | The **Command Line Interface** (CLI) version of the game. Uses ANSI escape codes for colored text. |
| `wordle_gui.py` | The **Graphical User Interface** (GUI) version. Built using Python's native `tkinter` library. |
| `words.txt` | The dictionary file containing valid 5-letter words used for both guesses and targets. |
| `placemate.json` | A JSON database that stores player records (Name, Time, Date) for the leaderboard. |

---

## 🛠️ Installation

You need **Python 3.x** installed on your machine. This project uses standard libraries (`tkinter`, `json`, `random`, `datetime`, `pathlib`), so no external `pip install` is required.

1.  Clone this repository:
    ```bash
    git clone [https://github.com/yourusername/wordle-python.git](https://github.com/yourusername/wordle-python.git)
    cd wordle-python
    ```
2.  Ensure `words.txt` is in the same directory as the scripts.

---

## 🎮 How to Play

### Option 1: Terminal (CLI) Version
Run the script in your terminal. The game uses colored background text to provide feedback.

```bash
python Wordle.py
```

---

##🏆 Leaderboard System (Placemate)
This game focuses on speed. Both versions of the game read from and write to `placemate.json`
### Option 2: Run the graphical interface. It features a start menu, a visual grid, and a real-time timer.
```bash
python wordle_gui.py
```

## Customizing Window Size:
You can optionally pass width and height arguments to the GUI script:
```bash
# Usage: python wordle_gui.py [width] [height]
python wordly_gui.py600 700
```
