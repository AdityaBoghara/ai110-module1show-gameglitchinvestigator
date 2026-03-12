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
