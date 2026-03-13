# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🚨 The Situation

You asked an AI to build a simple "Number Guessing Game" using Streamlit.
It wrote the code, ran away, and now the game is unplayable. 

- You can't win.
- The hints lie to you.
- The secret number seems to have commitment issues.

## 🛠️ Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Run the broken app: `python -m streamlit run app.py`

## 🕵️‍♂️ Your Mission

1. **Play the game.** Open the "Developer Debug Info" tab in the app to see the secret number. Try to win.
2. **Find the State Bug.** Why does the secret number change every time you click "Submit"? Ask ChatGPT: *"How do I keep a variable from resetting in Streamlit when I click a button?"*
3. **Fix the Logic.** The hints ("Higher/Lower") are wrong. Fix them.
4. **Refactor & Test.** - Move the logic into `logic_utils.py`.
   - Run `pytest` in your terminal.
   - Keep fixing until all tests pass!

## 📝 Document Your Experience

- [x] **Game Purpose:** This is a number guessing game built with Streamlit. The player picks a difficulty (Easy, Normal, or Hard), which sets the number range and attempt limit. Each round, a secret number is randomly chosen and the player tries to guess it. After each guess, they get a hint ("Go Higher" or "Go Lower") to help narrow it down. The goal is to guess the secret number before running out of attempts, with a score that rewards guessing it in fewer tries.

- [x] **Bugs Found:**
  - The secret number kept changing every time the Submit button was clicked, making it impossible to win.
  - The hints were backwards — "Go Higher" showed up when the guess was too high, and "Go Lower" when it was too low.
  - Invalid input (empty field or non-numbers) still counted as a used attempt.
  - The attempt counter started at 1 instead of 0, so the player was already "down an attempt" before they even guessed.
  - Switching difficulty mid-game didn't reset the secret or attempt count, letting players cheat by switching to Easy for more attempts.
  - The scoring formula had an off-by-one error — winning on the first try gave 80 points instead of the expected 90.
  - The "Too High" outcome incorrectly awarded +5 points on even attempts instead of always deducting.

- [x] **Fixes Applied:**
  - Moved the secret number into `st.session_state` so it only generates once per game and stays stable across reruns.
  - Swapped the hint logic in `check_guess()` so "Go HIGHER!" and "Go LOWER!" now point in the right direction.
  - Moved `attempts += 1` inside the valid-input branch so only real guesses count against the player.
  - Initialized `attempts` to 0 so the counter is accurate from the very first guess.
  - Added difficulty tracking in session state — switching difficulty now fully resets the game.
  - Fixed the score formula from `100 - 10 * (attempt_number + 1)` to `100 - 10 * attempt_number`.
  - Made both "Too High" and "Too Low" consistently deduct 5 points with no exceptions.

## 📸 Demo

![Winning Screenshot](Winning%20Screenshot.png)

## 🚀 Stretch Features

- [ ] [If you choose to complete Challenge 4, insert a screenshot of your Enhanced Game UI here]
