🟩 Python Wordle Clone
A full-featured clone of the popular game Wordle, built with Python. This project offers two ways to play: a Terminal-based (CLI) version for quick play and a Graphical User Interface (GUI) version built with Tkinter.
Both versions feature a persistent Leaderboard (Placemate) that tracks the fastest solve times.
🚀 Features
•	Dual Modes: Play in your terminal or via a windowed application.
•	Speed-Run Leaderboard: Tracks the fastest completion times in placemate.json.
•	Standard Wordle Rules: 6 attempts to guess a 5-letter word.
•	Feedback System:
o	🟩 Green: Correct letter, correct spot.
o	🟨 Yellow: Correct letter, wrong spot.
o	⬜ Gray: Letter not in the word.
•	Input Validation: Checks if the word is 5 letters long and exists in the dictionary.
________________________________________
📂 Project Structure
File	Description
Wordle.py	The Command Line Interface (CLI) version of the game. Uses ANSI escape codes for colored text.
wordle_gui.py	The Graphical User Interface (GUI) version. Built using Python's native tkinter library.
words.txt	The dictionary file containing valid 5-letter words used for both guesses and targets.
placemate.json	A JSON database that stores player records (Name, Time, Date) for the leaderboard.
________________________________________
🛠️ Installation & Prerequisites
You need Python 3.x installed on your machine. This project uses standard libraries (tkinter, json, random, datetime, pathlib), so no external pip install is required.
1.	Clone this repository:
Bash
git clone https://github.com/yourusername/wordle-python.git
cd wordle-python
2.	Ensure words.txt is in the same directory as the scripts.
________________________________________
🎮 How to Play
Option 1: Terminal (CLI) Version
Run the script in your terminal. The game uses colored background text to provide feedback.
Bash
python Wordle.py
Option 2: GUI Version
Run the graphical interface. It features a start menu, a visual grid, and a real-time timer.
Bash
python wordle_gui.py
Customizing Window Size:
You can optionally pass width and height arguments to the GUI script:
Bash
# Usage: python wordle_gui.py [width] [height]
python wordle_gui.py 600 700
________________________________________
🏆 Leaderboard System (Placemate)
This game focuses on speed. Both versions of the game read from and write to placemate.json.
•	New Players: If you are new, your name and time are added to the file.
•	Returning Players: The system checks your previous records. It only updates your entry if you achieve a New Personal Best (faster time).
•	View Leaderboard:
o	CLI: The top 10 times are printed at the start of the script.
o	GUI: Click the "Leaderboard" button in the main menu.
________________________________________
📝 Notes on words.txt
The game relies on words.txt for valid guesses.
•	The file should contain one 5-letter word per line.
•	The current list is a sample. You can expand it by adding more 5-letter words to the text file to increase difficulty.
🤝 Contributing
Feel free to fork this repository and submit pull requests. Suggestions for improvements:
•	Adding a "Hard Mode" (must use revealed hints).
•	Expanding the words.txt dictionary.
•	Adding sound effects to the GUI.


