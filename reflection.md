# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").

  When I first ran the game, it appeared to work on the surface but had several bugs that made it unfair or broken. Here is every issue found, with expected vs. actual behavior:

  Bug 1: Hard difficulty range is easier than Normal
  Expected: Hard should have a larger range than the normal range. The normal range goes from 1-50 and the harder range goes from 1-100
  Actually happened: Normal range goes from 1-100 and harder goes from 1-50. making the harder more easier than the normal

  Bug 2: Attempts counter started at 1 instead of 0
  Expected: A new game starts with 0 attempts used.
  Actually happened: attempts was initialized to 1, so the player had already "used" an attempt before making any guess.

  Bug 3: Info banner always said "1 to 100" regardless of difficulty
  Expected: The prompt should reflect the actual range for the selected difficulty.
  Actually happened: The message was hardcoded to "Guess a number between 1 and 100" on every difficulty.

  Bug 4 — New Game button ignored the difficulty setting
  Expected: New Game generates a secret within the correct range for the current difficulty.
  Actually happened: The reset always called random.randint(1, 100), silently ignoring Easy and Hard ranges.

  Bug 5 — Inconsistent attempts reset on New Game
  Expected: New Game resets state the same way the game initializes on first load.
  Actually happened: First load set attempts = 1, but New Game set it to 0, creating different behavior between the first and subsequent games.

  Bug 6 — "Too High" and "Too Low" hints were swapped
  Expected: Guessing too high → told to go lower. Guessing too low → told to go higher.
  Actually happened: The logic was reversed — too high showed "📈 Go HIGHER!" and too low showed "📉 Go LOWER!", sending the player in the wrong direction every time.

  Bug 7 — Secret was converted to a string on even-numbered attempts
  Expected: The secret stays an integer so comparisons always work correctly.
  Actually happened: On every even attempt, the secret was cast to a string. This caused broken comparisons like "9" > "10" evaluating as True, producing wrong hints and false wins.

  Bug 8 — Score rewarded "Too High" guesses on even attempts
  Expected: Wrong guesses (too high or too low) should both be penalized.
  Actually happened: update_score added +5 points for "Too High" on even-numbered attempts, rewarding the player for being wrong.

  Bug 9 — Invalid guesses still consumed an attempt
  Expected: Submitting an empty field or non-number should not count as an attempt.
  Actually happened: attempts += 1 ran before input was validated, so bad input cost the player an attempt.

  Bug 10 — Invalid input was recorded in the guess history
  Expected: Only valid numeric guesses appear in history.
  Actually happened: When parsing failed, the raw invalid string (e.g. "" or "abc") was still appended to history.

  Bug 11 — Unchecking "Show hint" made the game unplayable
  Expected: The hint is optional; the game still provides some feedback either way.
  Actually happened: With show_hint = False, zero feedback was shown — no way to know if a guess was too high or too low, making the game impossible to win through logic.

  Bug 12 — New Game button does not reset game status (Critical)
  Expected: Clicking New Game resets all game state so the player can play a full new round.
  Actually happened: st.session_state.status was never reset in the New Game block. After winning or losing, clicking New Game generates a new secret and resets attempts, but status remains "won" or "lost". The early-stop check at line 85 immediately halts the game, so the player can never actually play again without refreshing the browser.

  Bug 13 — New Game button does not reset guess history
  Expected: Starting a new game clears the previous round's guess history.
  Actually happened: st.session_state.history is never cleared in the New Game block, so guesses from previous rounds accumulate indefinitely in the history list shown in the debug panel.

  Bug 14 — Win score formula is off by one
  Expected: Winning on attempt 1 should award the maximum possible points (e.g., 90).
  Actually happened: The formula uses 100 - 10 * (attempt_number + 1), so winning on attempt 1 awards 80 points instead of 90 — penalizing the player one full tier as if they had used two attempts. The regression test was also written to match the broken formula, so the bug was never caught by the test suite.

  Bug 15 — Secret type alternation still present in app.py (partially unresolved)
  Expected: The secret should always be passed as an integer to check_guess.
  Actually happened: app.py lines 103–106 still cast the secret to a string on every even-numbered attempt. The check_guess function was patched to normalize both values to int first, which masks the problem, but the root cause — the type alternation — was never removed from the code.





---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

AI tool: Claude

Bug 1 Fix:
Fixed the logic by swapping the range of normal and hard by swapping the values. 
The AI suggestion was correct in the logic_utils file and i verified it by running the test file

Bug 6 and 7 fix: 
Claude identified that the hints in check_guess were swapped — "Too High" was paired with "Go HIGHER!" when it should say "Go LOWER!", and vice versa. I verified this by reading the logic: if guess > secret, the player needs to guess lower, so the hint was clearly backwards. The fix was confirmed correct by the passing pytest tests (test_hints_not_swapped, test_guess_too_high, test_guess_too_low).

Example of an incorrect or misleading AI suggestion:
Claude's first refactor of check_guess still had a bug — it used int() conversion in the except TypeError block, but didn't handle the case where 42 == "42" (int vs string) would fail the initial == check and fall through incorrectly returning "Too Low" instead of "Win". The tests exposed this: test_mixed_type_win failed with assert 'Too Low' == 'Win'. The AI's suggested fix only partially solved the type-mismatch problem and had to be revised a second time to normalize both values to int upfront.

Bug 8:
Claude correctly identified that the update_score bug was in the "Too High" branch awarding +5 points on even attempts instead of deducting. It suggested collapsing both wrong-guess outcomes into a single if outcome in ("Too High", "Too Low") check. I verified this by writing the regression test test_update_score_too_high_always_deducts, which calls the function with even and odd attempt numbers and asserts all return current_score - 5.

Bug 2:
Claude correctly identified that attempts was initialized to 1 instead of 0, causing the player to start every game having already "used" an attempt. It pointed out that the "Attempts left" display subtracted st.session_state.attempts from attempt_limit, so starting at 1 immediately showed one fewer attempt available even before the first guess. The fix was a one-line change: st.session_state.attempts = 0. I verified it visually by running the app and confirming the sidebar showed the full attempt count on a fresh load, and confirmed the new_game button already reset to 0 — meaning the first load was the only place with the wrong value.

Bug 3:
Claude correctly identified that the info banner in app.py was hardcoded to "Guess a number between 1 and 100", ignoring the difficulty setting entirely. It pointed out that low and high were already being computed from get_range_for_difficulty(difficulty) on line 45, so the fix was simply replacing the hardcoded values with those variables. I verified it by switching between Easy, Normal, and Hard in the app and confirming the banner updated to reflect the correct range for each difficulty.

Bug 4:
Claude correctly identified that the New Game button called random.randint(1, 100) instead of using the low and high variables already derived from the selected difficulty. The fix was a one-line change: replacing the hardcoded values with random.randint(low, high). I verified it by selecting Easy difficulty, clicking New Game repeatedly, and confirming via the Developer Debug Info expander that the secret number stayed within the Easy range (1–20) every time.

Bug 15:
Claude correctly identified that app.py lines 103–106 were alternating the type of secret — casting it to a str on even-numbered attempts and leaving it as an int on odd ones. This caused check_guess() to always fail on even attempts because comparing an int guess to a str secret never evaluates as equal in Python. The fix was to remove the type-switching block entirely and always pass st.session_state.secret directly as an int. I verified it by playing the game and confirming a correct guess on an even-numbered attempt now correctly registers as a win.

Bug 9:
Claude correctly identified that st.session_state.attempts += 1 was placed before the parse_guess call, so any invalid input — an empty field or a non-numeric string — still consumed an attempt even though no real guess was made. It also caught that the increment was written as a broken two-line expression (st.session_state.attempts on one line, = 1 on the next), which was syntactically invalid. The fix was to remove the misplaced increment entirely and add a correct attempts += 1 inside the else branch, so only successfully parsed guesses count. I verified it by entering an empty field and typing "abc", confirming the error message appeared but the attempts-left counter did not decrease.

Bug 10:
Claude correctly identified that history.append(raw_guess) was placed inside the if not ok branch, meaning invalid inputs like "" or "abc" were being recorded in the guess history even when parse_guess() failed. The fix was simply removing that one line — history.append(guess_int) in the else branch already handles the valid case correctly, so only successfully parsed integers get recorded. I verified it by submitting invalid input and checking the Developer Debug Info expander to confirm the history list stayed unchanged.

Bug 11:
Claude correctly identified that the entire st.warning(message) call was wrapped inside if show_hint:, which meant unchecking the checkbox suppressed all feedback — not just the directional hint. With show_hint = False, submitting any guess produced no visible output at all, making it impossible to play logically. The fix was to move the show_hint check inside a guard for non-win outcomes, and add an else branch showing a neutral "Guess recorded." message. I verified it by unchecking the checkbox, submitting a wrong guess, and confirming the info message appeared without revealing the hint direction.

Bug 12:
Claude correctly identified that st.session_state.status was never reset in the New Game block. After winning or losing, the status remained "won" or "lost", so the early-stop guard at line 89 immediately called st.stop() on the very next rerun — even after clicking New Game. The fix was a one-line addition: st.session_state.status = "playing" inside the new_game block. I verified it by winning a game, clicking New Game, submitting a guess, and confirming the game accepted the input and decremented the attempts counter normally.

Example of an incorrect or misleading AI suggestion for Bug 12:
Claude's first explanation of the bug described it as a "missing reset" without flagging that st.rerun() at the end of the new_game block actually triggers the status check on the very next script execution — meaning the guard fires before any guess is submitted, not on guess submission. I initially thought the bug would only surface when clicking Submit after New Game, but it actually blocks the game immediately after the rerun. Running the app manually made this clear: the "You already won." banner appeared right after clicking New Game, before I could type anything at all.

Bug 13:
Claude correctly identified that st.session_state.history was never cleared in the New Game block. After each game, clicking New Game reset the secret and attempts but left the history list intact, so guesses from all previous rounds kept accumulating in the Developer Debug Info panel. The fix was a one-line addition — st.session_state.history = [] — placed alongside the other reset lines inside the new_game block. I verified it by playing a round, clicking New Game, and confirming the history list in the debug expander was empty before any new guesses were submitted.

Bug 14:
Claude correctly identified that the win score formula in update_score used 100 - 10 * (attempt_number + 1), which applied an extra penalty tier — a player winning on their first attempt received 80 points instead of the expected 90. It also caught that the regression test test_update_score_win_first_attempt was written to assert == 80, matching the broken formula rather than the intended behavior, so the bug had never been detected by the test suite. The fix was removing the spurious + 1 from the formula and updating the test assertion from 80 to 90. I verified it by running pytest and confirming test_update_score_win_first_attempt passed with the corrected expected value.

Example of an incorrect or misleading AI suggestion for Bug 14:
Claude's first pass flagged only the formula in logic_utils.py and did not initially mention that the test itself was wrong. I had to re-read the test file and notice that the comment still said "100 - 10*(1+1) = 80 points" — matching the old broken formula. The AI only caught the test issue when prompted to check whether any tests reflected the old behavior. This was a good reminder that when a formula changes, every test asserting its output must be reviewed at the same time.


---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

Bug 1 fix: 
I tested the bug fix by asking claude to generate a test case: test_hard_range_larger_than_normal
 confirmed the fix by writing a targeted pytest test and running the test suite.

Test I ran:
def test_hard_range_larger_than_normal():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high
Running pytest showed this test passed, which confirmed that Hard's range (1–100) is now wider than Normal's (1–50). Before the fix, Hard was 1–50 and Normal was 1–100, so the assertion would have failed — proving the test actually catches the bug rather than just passing blindly.

Did AI help you design or understand any tests?

Yes. I asked Claude (AI) to generate a pytest case specifically targeting the bug. It identified that the right thing to test wasn't just the raw values, but the relationship between difficulty levels — asserting hard_high > normal_high rather than hardcoding expected numbers. This made the test resilient to future range changes while still enforcing the correct difficulty ordering.

Bug 6 & 7:
How did you decide whether a bug was really fixed?
A bug was considered fixed only when the corresponding pytest test passed. Reading the code alone wasn't enough — the 42 == "42" bug looked plausible in the first fix but the test exposed it immediately. Running the full test suite after each change ensured no regression was introduced.

Describe at least one test you ran and what it showed:
test_mixed_type_str_comparison_not_lexicographic called check_guess(9, "10") and asserted the outcome was "Too Low". This was critical because Python evaluates "9" > "10" as True (lexicographic order), which would wrongly return "Too High". The test passing confirmed the fix was using numeric comparison via int() rather than raw string comparison.

Did AI help you design or understand any tests? How?
Yes — Claude Code suggested the test cases and explained the reasoning behind each one. For example, it pointed out that the TypeError fallback in the original code used string comparison, and proposed check_guess(9, "10") specifically to expose that edge case. It also identified that check_guess("abc", "xyz") wouldn't raise a TypeError at all (strings are always comparable in Python), which is why a separate test_invalid_input_returns_invalid test was needed. However, the AI's initial fix still failed two of its own tests, which showed that tests are necessary to verify AI-generated code — not just trust it.

Bug 8: 

How did you decide whether a bug was really fixed?

I considered the bug fixed only when the regression test test_update_score_too_high_always_deducts passed with even and odd attempt numbers. Reading the fixed code alone wasn't sufficient — the original buggy code also looked intentional at first glance, so a test that explicitly calls the function three times (attempt 0, 1, 2) and asserts == 95 each time was the only reliable confirmation.

Describe at least one test you ran:

test_update_score_high_and_low_equal_penalty called update_score(100, "Too High", 3) and update_score(100, "Too Low", 3) and asserted both results were equal. This was useful because it didn't just check the fixed outcome — it verified the symmetry between the two wrong-guess cases, which is what the bug had broken in the first place.

Did AI help you design or understand any tests?

Yes — Claude designed all six update_score tests and explained the reasoning. It specifically added test_update_score_too_high_always_deducts as a regression test targeting the original bug, and test_update_score_unknown_outcome_unchanged to guard against future outcomes being accidentally penalized. This showed me that good tests don't just verify the happy path — they also pin down the exact behavior that was broken.

Bug 2:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by running the app manually and verifying the "Attempts left" display showed the correct full count on a fresh load. Because this bug lived in app.py session state (not a pure function), there was no pytest test to run — I had to visually confirm the counter started at the right number before the first guess was submitted.

Describe at least one test you ran:
I ran the app and checked the sidebar caption "Attempts left: N" on first load. Before the fix it showed one fewer attempt than allowed (e.g., 7 instead of 8 on Normal). After changing the initialization to 0, the display matched the expected attempt_limit exactly. I also compared the first-load behavior against the New Game button reset, which already used 0 — confirming the two code paths were now consistent.

Did AI help you design or understand any tests? How?
Claude pointed out that this bug couldn't be caught by a unit test because it involved Streamlit session state initialization, not a pure function. Instead, it suggested a manual verification checklist: load the app fresh, check the attempts-left count, submit one guess, and confirm the count decrements correctly from the full limit. This was a useful reminder that not every bug needs a pytest test — sometimes a structured manual check is the right tool.

Bug 3:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by manually running the app and switching between Easy, Normal, and Hard difficulties, confirming the info banner updated to the correct range each time. Because the bug was in a hardcoded string in app.py rather than a pure function, there was no pytest test to write — visual verification was the right approach.

Describe at least one test you ran:
I ran the app and selected each difficulty in turn. On Easy the banner showed "Guess a number between 1 and 20", on Normal "1 and 50", and on Hard "1 and 100". Before the fix, all three showed "1 and 100", so seeing the banner change with difficulty confirmed the fix was working correctly.

Did AI help you design or understand any tests? How?
Claude pointed out that since the bug was a hardcoded string in Streamlit UI code, a pytest unit test wasn't applicable — the right verification was a manual walkthrough switching difficulties and reading the banner. This reinforced the same lesson from Bug 2: not every fix requires an automated test, and knowing which tool fits the situation is part of good debugging practice.

Bug 4:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by manually running the app, selecting Easy difficulty, and clicking New Game several times. Because the bug was in Streamlit UI code (not a pure function), there was no pytest test to write — I used the Developer Debug Info expander to read the secret value directly after each reset and confirm it stayed within the correct range.

Describe at least one test you ran:
I set difficulty to Easy, clicked New Game five times, and read the "Secret:" value from the Developer Debug Info expander each time. Before the fix, the secret was frequently outside the Easy range (e.g., 73 or 91). After the fix, every reset produced a value between 1 and 20, confirming the correct range was being used.

Did AI help you design or understand any tests? How?
Claude pointed out that since the bug lived in the New Game button handler in app.py — not a pure function — a unit test wasn't the right tool. It suggested using the built-in debug expander to observe the secret directly, which gave immediate, reliable feedback without needing to guess whether the fix was working. This was the same lesson as Bugs 2 and 3: match the verification method to where the bug actually lives.

Bug 9:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by manually testing with invalid inputs — an empty field and the string "abc" — and confirming that the attempts-left counter did not decrease after each rejected submission. Because the bug was in app.py's submit handler rather than a pure function, manual verification was the right approach.

Describe at least one test you ran:
I typed "abc" into the guess field and clicked Submit. Before the fix, the attempts-left count dropped by one even though an error was shown. After moving attempts += 1 inside the else branch, the same input showed the error but left the counter unchanged. I also tested an empty submission and confirmed the same behavior, ruling out any edge case between the two invalid input types.

Did AI help you design or understand any tests? How?
Claude pointed out that since the bug lived in the Streamlit submit handler — not a pure function — a pytest unit test wasn't appropriate here. It suggested a two-case manual check: one empty submission and one non-numeric string, both confirming the attempts counter stays the same while the error message still appears. This targeted approach made the fix immediately verifiable without needing to write extra test infrastructure.

Bug 15:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by manually playing the game and submitting a correct guess on an even-numbered attempt. Before the fix, a correct guess on attempt 2, 4, or 6 would never register as a win — the game would just show a hint and keep going. After removing the type-switching logic, a correct guess on any attempt immediately triggered the win screen.

Describe at least one test you ran:
I ran the app, used the Developer Debug Info expander to read the secret number, then deliberately submitted that exact number as my second guess (an even attempt). Before the fix the game responded with a "Too Low" or "Too High" hint instead of winning. After the fix it correctly showed the win screen and balloons, confirming int-to-int comparison was now happening on every attempt.

Did AI help you design or understand any tests? How?
Claude pointed out that because this bug lived in app.py's submit handler — not a pure function — a pytest unit test wasn't the right tool. It suggested a targeted manual check: read the secret from the debug expander, then submit it on an even attempt to expose the failure directly. This made the bug immediately reproducible and the fix immediately verifiable without needing to guess or write extra test code.

Bug 10:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by manually submitting invalid input and checking the Developer Debug Info expander to confirm the history list did not change. Because the bug was in app.py's submit handler — not a pure function — manual verification using the debug panel was the right approach.

Describe at least one test you ran:
I typed "abc" into the guess field and clicked Submit. Before the fix, the history list in the debug expander showed "abc" appended even though an error was displayed. After removing the history.append(raw_guess) line from the if not ok branch, the same input showed the error but left the history list unchanged, confirming only valid integers are now recorded.

Did AI help you design or understand any tests? How?
Claude pointed out that the fix was a single line removal and suggested verifying it directly through the debug expander rather than writing a unit test, since the bug lived in Streamlit UI code. It noted that history.append(guess_int) in the else branch already covered the valid case, so the only thing needed was confirming the invalid branch no longer touched history at all.

Bug 11:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by unchecking "Show hint" and submitting a guess, then confirming that some feedback still appeared. Before the fix, unchecking the checkbox produced complete silence — no message at all after submitting — making it impossible to know whether the guess was too high or too low. After the fix, a neutral "Guess recorded." message appeared instead, confirming the guess was accepted without leaking the directional hint.

Describe at least one test you ran:
I unchecked "Show hint", typed a guess I knew was wrong, and clicked Submit. Before the fix, the page just refreshed with no feedback. After the fix, "Guess recorded." appeared as an info message. I also verified that re-checking the box immediately restored the directional hint ("Go LOWER!" / "Go HIGHER!"), confirming the checkbox now correctly controls only the hint detail rather than all feedback.

Did AI help you design or understand any tests? How?
Claude identified the root cause: the entire st.warning(message) call was inside if show_hint:, meaning disabling the hint suppressed all output from check_guess() — including feedback the player needs to keep playing. It suggested wrapping only the non-win outcomes in the show_hint check and adding an else branch with a neutral acknowledgment, so the game remains playable regardless of the checkbox state. The fix was verified manually since the bug lived in Streamlit UI code rather than a pure function.

Bug 12:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by manually reproducing the full failure path: win a game, click New Game, then immediately try to submit a guess. Before the fix, clicking New Game appeared to work — the "New game started." banner showed and the secret reset — but the game was still blocked because st.rerun() triggered the status guard before any guess could be made, showing "You already won." and halting the script. After adding st.session_state.status = "playing" to the New Game block, the game fully reset and accepted new guesses as expected.

Describe at least one test you ran:
I played a game to a win, clicked New Game, then typed a guess and clicked Submit. Before the fix, the "You already won." error banner appeared immediately after the rerun — before I even submitted a guess — because st.stop() was called at the status check on line 89. After the fix, the guess went through, the attempts counter decremented correctly, and a hint appeared. I repeated the same test after losing a game to confirm the "lost" status was also cleared.

Did AI help you design or understand any tests? How?
Claude pointed out that the bug was invisible during normal play and only surfaced after reaching a terminal state. It suggested the exact reproduction steps — play to completion, click New Game, submit a guess — and explained that st.rerun() makes Streamlit re-execute the entire script from the top, so the status guard fires immediately on the rerun rather than waiting for the next Submit click. This helped me understand why the game appeared broken right after clicking New Game rather than only when guessing, which made the fix and verification straightforward.

Bug 13:

How did you decide whether a bug was really fixed?
I decided the bug was fixed by manually clicking New Game and checking the Developer Debug Info expander to confirm the history list was empty before any new guesses were submitted. Because the bug was in app.py's New Game handler — not a pure function — manual verification using the debug panel was the right approach.

Describe at least one test you ran:
I played a round, submitted three guesses, then clicked New Game. Before the fix, the history list in the debug expander still showed all three guesses from the previous round. After adding st.session_state.history = [] to the new_game block, the same sequence produced an empty history list immediately after the reset, confirming previous guesses are now cleared on every new game.

Did AI help you design or understand any tests? How?
Claude pointed out that since the bug lived in the New Game button handler in app.py — not a pure function — a unit test wasn't appropriate. It suggested using the Developer Debug Info expander to observe the history list directly before and after clicking New Game, which gave immediate, reliable feedback. This was consistent with the same verification approach used for Bugs 3, 4, and 12 — matching the tool to where the bug actually lives.

Bug 14:

How did you decide whether a bug was really fixed?
I decided the bug was fixed when the pytest test test_update_score_win_first_attempt passed with the corrected assertion (== 90). Because update_score is a pure function, a unit test was the right tool — and crucially, the test itself had to be fixed first since it was asserting the broken behavior (== 80), which is why the bug had gone undetected.

Describe at least one test you ran:
I ran pytest on test_update_score_win_first_attempt, which calls update_score(0, "Win", 1) and asserts the result equals 90. Before fixing the formula, the function returned 80 because of the spurious + 1. After removing it, the function returned 90 and the test passed. I also checked test_update_score_win_minimum_points, which I updated to use attempt_number=10 (the actual boundary where the corrected formula reaches 0 before clamping), confirming the floor of 10 still applies correctly.

Did AI help you design or understand any tests? How?
Claude identified that the test comment ("100 - 10*(1+1) = 80") matched the broken formula rather than the intended behavior, which is what caused the bug to go undetected. This reinforced an important lesson: a test that was written against buggy code will pass the bug and fail the fix — so when changing a formula, every test asserting its output must be reviewed at the same time, not just the production code.


---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
- What change did you make that finally gave the game a stable secret number?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
