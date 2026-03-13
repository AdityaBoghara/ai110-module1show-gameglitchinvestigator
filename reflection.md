# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

When I first ran the game, it appeared to work on the surface but had several bugs that made it unfair or broken. Here is every issue I found, with expected vs. actual behavior:

Bug 1: Hard difficulty range is easier than Normal
Expected: Hard should have a larger range than Normal. Normal goes from 1–50 and Hard goes from 1–100.
Actually happened: Normal was 1–100 and Hard was 1–50, making Hard easier than Normal.

Bug 2: Attempts counter started at 1 instead of 0
Expected: A new game starts with 0 attempts used.
Actually happened: attempts was initialized to 1, so the player had already "used" an attempt before making any guess.

Bug 3: Info banner always said "1 to 100" regardless of difficulty
Expected: The prompt should reflect the actual range for the selected difficulty.
Actually happened: The message was hardcoded to "Guess a number between 1 and 100" on every difficulty.

Bug 4: New Game button ignored the difficulty setting
Expected: New Game generates a secret within the correct range for the current difficulty.
Actually happened: The reset always called random.randint(1, 100), silently ignoring Easy and Hard ranges.

Bug 5: Inconsistent attempts reset on New Game
Expected: New Game resets state the same way the game initializes on first load.
Actually happened: First load set attempts = 1, but New Game set it to 0, creating different behavior between the first and subsequent games.

Bug 6: "Too High" and "Too Low" hints were swapped
Expected: Guessing too high means told to go lower. Guessing too low means told to go higher.
Actually happened: The logic was reversed — too high showed "📈 Go HIGHER!" and too low showed "📉 Go LOWER!", sending the player in the wrong direction every time.

Bug 7: Secret was converted to a string on even-numbered attempts
Expected: The secret stays an integer so comparisons always work correctly.
Actually happened: On every even attempt, the secret was cast to a string. This caused broken comparisons like "9" > "10" evaluating as True, producing wrong hints and false wins.

Bug 8: Score rewarded "Too High" guesses on even attempts
Expected: Wrong guesses (too high or too low) should both be penalized.
Actually happened: update_score added +5 points for "Too High" on even-numbered attempts, rewarding the player for being wrong.

Bug 9: Invalid guesses still consumed an attempt
Expected: Submitting an empty field or non-number should not count as an attempt.
Actually happened: attempts += 1 ran before input was validated, so bad input cost the player an attempt.

Bug 10: Invalid input was recorded in the guess history
Expected: Only valid numeric guesses appear in history.
Actually happened: When parsing failed, the raw invalid string (e.g. "" or "abc") was still appended to history.

Bug 11: Unchecking "Show hint" made the game unplayable
Expected: The hint is optional; the game still provides some feedback either way.
Actually happened: With show_hint = False, zero feedback was shown — no way to know if a guess was too high or too low, making the game impossible to win through logic.

Bug 12: New Game button does not reset game status (Critical)
Expected: Clicking New Game resets all game state so the player can play a full new round.
Actually happened: st.session_state.status was never reset in the New Game block. After winning or losing, clicking New Game generates a new secret and resets attempts, but status remains "won" or "lost". The early-stop check at line 85 immediately halts the game, so the player can never actually play again without refreshing the browser.

Bug 13: New Game button does not reset guess history
Expected: Starting a new game clears the previous round's guess history.
Actually happened: st.session_state.history is never cleared in the New Game block, so guesses from previous rounds accumulate indefinitely in the history list shown in the debug panel.

Bug 14: Win score formula is off by one
Expected: Winning on attempt 1 should award the maximum possible points (e.g., 90).
Actually happened: The formula uses 100 - 10 * (attempt_number + 1), so winning on attempt 1 awards 80 points instead of 90, penalizing the player one full tier as if they had used two attempts. The regression test was also written to match the broken formula, so the bug was never caught by the test suite.

Bug 15: Secret type alternation still present in app.py (partially unresolved)
Expected: The secret should always be passed as an integer to check_guess.
Actually happened: app.py lines 103–106 still cast the secret to a string on every even-numbered attempt. The check_guess function was patched to normalize both values to int first, which masks the problem, but the root cause — the type alternation — was never removed from the code.


---

## 2. How did you use AI as a teammate?

I used Claude as my AI tool throughout this project.

For Bug 1, I fixed the logic by swapping the ranges for Normal and Hard. Claude's suggestion was correct in the logic_utils file and I verified it by running the test suite.

For Bugs 6 and 7, Claude identified that the hints in check_guess were swapped — "Too High" was paired with "Go HIGHER!" when it should say "Go LOWER!", and vice versa. I verified this by reading the logic: if guess > secret, the player needs to guess lower, so the hint was clearly backwards. The fix was confirmed correct by the passing pytest tests (test_hints_not_swapped, test_guess_too_high, test_guess_too_low). That said, Claude's first refactor of check_guess still had a bug — it used int() conversion in the except TypeError block, but didn't handle the case where 42 == "42" (int vs string) would fail the initial == check and fall through incorrectly returning "Too Low" instead of "Win". The tests exposed this: test_mixed_type_win failed with assert 'Too Low' == 'Win'. The AI's suggested fix only partially solved the type-mismatch problem and had to be revised a second time to normalize both values to int upfront.

For Bug 8, Claude correctly identified that the update_score bug was in the "Too High" branch awarding +5 points on even attempts instead of deducting. It suggested collapsing both wrong-guess outcomes into a single if outcome in ("Too High", "Too Low") check. I verified this by writing the regression test test_update_score_too_high_always_deducts, which calls the function with even and odd attempt numbers and asserts all return current_score - 5.

For Bug 2, Claude correctly identified that attempts was initialized to 1 instead of 0, causing the player to start every game having already "used" an attempt. It pointed out that the "Attempts left" display subtracted st.session_state.attempts from attempt_limit, so starting at 1 immediately showed one fewer attempt available even before the first guess. The fix was a one-line change: st.session_state.attempts = 0. I verified it visually by running the app and confirming the sidebar showed the full attempt count on a fresh load, and confirmed the new_game button already reset to 0 — meaning the first load was the only place with the wrong value.

For Bug 3, Claude correctly identified that the info banner in app.py was hardcoded to "Guess a number between 1 and 100", ignoring the difficulty setting entirely. It pointed out that low and high were already being computed from get_range_for_difficulty(difficulty) on line 45, so the fix was simply replacing the hardcoded values with those variables. I verified it by switching between Easy, Normal, and Hard in the app and confirming the banner updated to reflect the correct range for each difficulty.

For Bug 4, Claude correctly identified that the New Game button called random.randint(1, 100) instead of using the low and high variables already derived from the selected difficulty. The fix was a one-line change: replacing the hardcoded values with random.randint(low, high). I verified it by selecting Easy difficulty, clicking New Game repeatedly, and confirming via the Developer Debug Info expander that the secret number stayed within the Easy range (1–20) every time.

For Bug 15, Claude correctly identified that app.py lines 103–106 were alternating the type of secret — casting it to a str on even-numbered attempts and leaving it as an int on odd ones. This caused check_guess() to always fail on even attempts because comparing an int guess to a str secret never evaluates as equal in Python. The fix was to remove the type-switching block entirely and always pass st.session_state.secret directly as an int. I verified it by playing the game and confirming a correct guess on an even-numbered attempt now correctly registers as a win.

For Bug 9, Claude correctly identified that st.session_state.attempts += 1 was placed before the parse_guess call, so any invalid input — an empty field or a non-numeric string — still consumed an attempt even though no real guess was made. It also caught that the increment was written as a broken two-line expression (st.session_state.attempts on one line, = 1 on the next), which was syntactically invalid. The fix was to remove the misplaced increment entirely and add a correct attempts += 1 inside the else branch, so only successfully parsed guesses count. I verified it by entering an empty field and typing "abc", confirming the error message appeared but the attempts-left counter did not decrease.

For Bug 10, Claude correctly identified that history.append(raw_guess) was placed inside the if not ok branch, meaning invalid inputs like "" or "abc" were being recorded in the guess history even when parse_guess() failed. The fix was simply removing that one line — history.append(guess_int) in the else branch already handles the valid case correctly, so only successfully parsed integers get recorded. I verified it by submitting invalid input and checking the Developer Debug Info expander to confirm the history list stayed unchanged.

For Bug 11, Claude correctly identified that the entire st.warning(message) call was wrapped inside if show_hint:, which meant unchecking the checkbox suppressed all feedback — not just the directional hint. With show_hint = False, submitting any guess produced no visible output at all, making it impossible to play logically. The fix was to move the show_hint check inside a guard for non-win outcomes, and add an else branch showing a neutral "Guess recorded." message. I verified it by unchecking the checkbox, submitting a wrong guess, and confirming the info message appeared without revealing the hint direction.

For Bug 12, Claude correctly identified that st.session_state.status was never reset in the New Game block. After winning or losing, the status remained "won" or "lost", so the early-stop guard at line 89 immediately called st.stop() on the very next rerun — even after clicking New Game. The fix was a one-line addition: st.session_state.status = "playing" inside the new_game block. I verified it by winning a game, clicking New Game, submitting a guess, and confirming the game accepted the input and decremented the attempts counter normally. However, Claude's first explanation of the bug described it as a "missing reset" without flagging that st.rerun() at the end of the new_game block actually triggers the status check on the very next script execution — meaning the guard fires before any guess is submitted, not on guess submission. I initially thought the bug would only surface when clicking Submit after New Game, but it actually blocks the game immediately after the rerun. Running the app manually made this clear: the "You already won." banner appeared right after clicking New Game, before I could type anything at all.

For Bug 13, Claude correctly identified that st.session_state.history was never cleared in the New Game block. After each game, clicking New Game reset the secret and attempts but left the history list intact, so guesses from all previous rounds kept accumulating in the Developer Debug Info panel. The fix was a one-line addition — st.session_state.history = [] — placed alongside the other reset lines inside the new_game block. I verified it by playing a round, clicking New Game, and confirming the history list in the debug expander was empty before any new guesses were submitted.

For Bug 14, Claude correctly identified that the win score formula in update_score used 100 - 10 * (attempt_number + 1), which applied an extra penalty tier — a player winning on their first attempt received 80 points instead of the expected 90. It also caught that the regression test test_update_score_win_first_attempt was written to assert == 80, matching the broken formula rather than the intended behavior, so the bug had never been detected by the test suite. The fix was removing the spurious + 1 from the formula and updating the test assertion from 80 to 90. I verified it by running pytest and confirming test_update_score_win_first_attempt passed with the corrected expected value. On the other hand, Claude's first pass flagged only the formula in logic_utils.py and did not initially mention that the test itself was wrong. I had to re-read the test file and notice that the comment still said "100 - 10*(1+1) = 80 points" — matching the old broken formula. The AI only caught the test issue when prompted to check whether any tests reflected the old behavior. This was a good reminder that when a formula changes, every test asserting its output must be reviewed at the same time.


---

## 3. Debugging and testing your fixes

For Bug 1, I confirmed the fix was real by asking Claude to generate a targeted pytest test — test_hard_range_larger_than_normal — and then running the suite to watch it pass. The test worked by asserting hard_high > normal_high rather than checking exact numbers, so it would catch the bug regardless of what the specific range values were:

def test_hard_range_larger_than_normal():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high

Running pytest confirmed that Hard's range (1–100) is now wider than Normal's (1–50). Before the fix, the assertion would have failed outright — which proved the test was actually catching the bug rather than just passing blindly. Claude pointed out that testing the relationship between difficulty levels, rather than hardcoding expected values, made the test resilient to future range changes while still enforcing correct ordering.

For Bugs 6 and 7, a bug wasn't considered fixed until the corresponding pytest test passed. Reading the code alone wasn't enough — the 42 == "42" issue looked plausible in the first fix but the test exposed it right away. I ran test_mixed_type_str_comparison_not_lexicographic, which called check_guess(9, "10") and asserted the outcome was "Too Low". This mattered because Python evaluates "9" > "10" as True under lexicographic comparison, which would have wrongly returned "Too High". The test passing confirmed the fix was doing numeric comparison via int() instead. Claude also flagged that check_guess("abc", "xyz") wouldn't raise a TypeError at all — strings are always comparable in Python — which is why a separate test_invalid_input_returns_invalid test was needed. Even so, the AI's initial fix still failed two of its own suggested tests, which was a good reminder that tests exist to verify AI-generated code, not just trust it.

For Bug 8, I considered the fix done only when test_update_score_too_high_always_deducts passed across even and odd attempt numbers. The original buggy code looked intentional at first glance, so reading the fix wasn't enough — I needed a test that called the function three times (attempt 0, 1, 2) and asserted == 95 each time. I also ran test_update_score_high_and_low_equal_penalty, which called update_score(100, "Too High", 3) and update_score(100, "Too Low", 3) and asserted both results were equal. That test verified the symmetry between the two wrong-guess outcomes, which is exactly what the bug had broken. Claude designed all six update_score tests and explained the reasoning behind each one, including test_update_score_unknown_outcome_unchanged as a guard against future outcomes being accidentally penalized — a good reminder that tests should pin down broken behavior, not just verify the happy path.

For Bug 2, I ran the app manually and watched the "Attempts left" display on a fresh load. Before the fix it showed one fewer attempt than allowed (e.g., 7 instead of 8 on Normal). After changing the initialization to 0, it matched the expected attempt_limit exactly, and I confirmed the New Game button reset already used 0 — meaning first load was the only place with the wrong value. Claude pointed out that this bug couldn't be caught by a unit test since it lived in Streamlit session state initialization, not a pure function. It suggested a manual checklist instead: load fresh, check the count, submit one guess, confirm it decrements from the full limit. That was a useful reminder that not every bug needs pytest — sometimes a structured manual check is the right tool.

For Bug 3, I ran the app and selected each difficulty in turn. On Easy the banner showed "Guess a number between 1 and 20", on Normal "1 and 50", and on Hard "1 and 100". Before the fix all three showed "1 and 100", so watching the banner change with each difficulty selection confirmed the fix was working. Claude noted that since the bug was a hardcoded string in Streamlit UI code, a unit test wasn't the right approach — a manual walkthrough was. That reinforced the same lesson from Bug 2: knowing which verification tool fits the situation is part of debugging well.

For Bug 4, I set difficulty to Easy, clicked New Game five times, and read the "Secret:" value from the Developer Debug Info expander each time. Before the fix, the secret frequently landed outside the Easy range (e.g., 73 or 91). After the fix every reset produced a number between 1 and 20. Claude pointed out that since the bug was in the New Game button handler — not a pure function — the debug expander was the right verification tool, giving immediate and reliable feedback without needing to guess.

For Bug 9, I tested with an empty field and the string "abc" and confirmed the attempts-left counter didn't drop after either rejection. Before the fix, typing "abc" and clicking Submit would decrement the counter even though an error appeared. After moving attempts += 1 inside the else branch, the same input showed the error and left the counter unchanged. Claude suggested the two-case manual check specifically because the bug lived in the Streamlit submit handler, making a pytest test impractical.

For Bug 15, I used the Developer Debug Info expander to find the secret, then deliberately submitted that exact value as my second guess — an even-numbered attempt. Before the fix, a correct guess on attempt 2, 4, or 6 would never register as a win; the game just showed a hint and kept going. After removing the type-switching logic, submitting the correct number on an even attempt immediately triggered the win screen and the balloons, confirming int-to-int comparison was now happening on every attempt. Claude recommended this manual approach since the bug was in app.py's submit handler rather than a testable pure function.

For Bug 10, I typed "abc" and clicked Submit, then checked the Developer Debug Info expander. Before the fix, the history list showed "abc" appended even though an error was displayed. After removing the history.append(raw_guess) line from the if not ok branch, the same input left the history list completely unchanged. Claude noted the fix was a single line removal and the debug expander was the right way to verify it — since history.append(guess_int) in the else branch already handled the valid case, all that was needed was confirming the invalid branch no longer touched history.

For Bug 11, I unchecked "Show hint", typed a guess I knew was wrong, and clicked Submit. Before the fix the page just refreshed with no output at all, making the game unplayable without hints. After the fix "Guess recorded." appeared as a neutral info message. Re-checking the box immediately restored the directional hint, confirming the checkbox now controlled only the hint detail and not all feedback. Claude identified the root cause: the entire st.warning(message) call was inside if show_hint:, suppressing all output when the checkbox was off. Its fix — wrapping only the non-win outcomes in the show_hint check and adding an else branch — was verified manually since the bug was in Streamlit UI code.

For Bug 12, I reproduced the full failure path: won a game, clicked New Game, then immediately tried to submit a guess. Before the fix, the "You already won." banner appeared right after the rerun — before I even typed anything — because st.rerun() at the end of the new_game block re-executed the whole script and hit the status guard at line 89 immediately. After adding st.session_state.status = "playing" to the new_game block, the game fully reset and accepted new guesses normally. I repeated the same test after a loss to confirm the "lost" status was cleared too. Claude's explanation of st.rerun() behavior was what helped me understand why the game broke right after clicking New Game rather than only on the next Submit click.

For Bug 13, I played a round, submitted three guesses, then clicked New Game. Before the fix, the history list in the debug expander still showed all three guesses from the previous round. After adding st.session_state.history = [] to the new_game block, the same sequence produced an empty list right after the reset. Claude pointed out that since the bug was in the New Game handler — not a pure function — the debug expander was the right tool, consistent with the same approach used for Bugs 3, 4, and 12.

For Bug 14, I knew the fix was real when test_update_score_win_first_attempt passed with the corrected assertion (== 90). Crucially, the test itself had to be fixed first — it was asserting == 80, which matched the broken formula, and that's exactly why the bug had gone undetected for so long. I ran pytest on update_score(0, "Win", 1) and confirmed it now returned 90 after removing the spurious + 1. I also updated test_update_score_win_minimum_points to use attempt_number=10, confirming the floor of 10 still applied correctly. Claude caught that the test comment ("100 - 10*(1+1) = 80") still matched the old broken formula, which reinforced a key lesson: when a formula changes, every test asserting its output needs to be reviewed at the same time, not just the production code.


---

## 4. What did you learn about Streamlit and state?

The biggest thing I learned is that Streamlit reruns your entire Python script from top to bottom every single time the user interacts with anything a button click, a slider change, anything. In the original code, `random.randint(low, high)` was just sitting at the top level with no guard around it, so every rerun rolled a completely new secret number. The player never had a real chance because the target kept moving with every click.

If I were explaining this to a friend, I'd put it this way: every button click is basically a full page refresh that reexecutes all your code from scratch. Normal variables get wiped between those refreshes. The way you hold onto something across reruns is by storing it in `st.session_state`, which is like a small notepad that Streamlit keeps alive for the duration of the session. Whatever you write to it sticks around until you explicitly clear it.

Wrapping the secret generation in an `if "secret" not in st.session_state:` check was all it took to fix it. That one guard means the number gets picked exactly once on the very first load, and every rerun after that just reads the value that's already there. Once that was in place the game was actually playable for the first time.

---

## 5. Looking ahead: your developer habits

The habit I'm taking away from this project is running the full test suite after every single fix, not just at the end when everything is supposedly done. A few times I patched one bug and quietly introduced a problem somewhere else, and I only caught it because a previously passing test suddenly started failing. That tight feedback loop fix something, run everything, see what shifted saved me from pushing broken code more than once. I don't want to go back to skipping that step.

If I could do one thing differently, it would be treating AI suggestions the same way I'd treat a pull request from a teammate not just reading through the explanation and nodding along, but actually running the code and checking the results. A couple of times I accepted a fix that sounded completely reasonable, moved on, and then had the tests catch something the AI missed. The fix was right in spirit but wrong in a small but important detail. Going forward: read it, understand it, test it in that order, every time.

What this project actually changed for me is how I think about AI confidence. I came in expecting AI to either nail it or obviously fail, but the tricky case is the one in between code that looks correct, reads cleanly, and still breaks on one specific edge case. That's the one that's actually dangerous because it's easy to miss. AI is a strong collaborator and a fast starting point, but it's not a replacement for running the code yourself and seeing what actually happens.
