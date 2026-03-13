import random
import streamlit as st
from logic_utils import get_range_for_difficulty, check_guess, update_score, parse_guess


st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

# FIXME: attempts was initialized to 1, consuming one attempt before the player
# made any guess and causing the attempts-left display to be off by one from the start
# FIX: Initialize attempts to 0 so the counter is accurate from the first guess
if "attempts" not in st.session_state:
    st.session_state.attempts = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

st.subheader("Make a guess")

# FIXME: Info banner was hardcoded to "1 and 100" regardless of the selected difficulty,
# so players always saw the wrong range on Easy and Hard modes.
# FIX: Replace hardcoded values with the `low` and `high` variables from get_range_for_difficulty()
st.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with st.expander("Developer Debug Info"):
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

raw_guess = st.text_input("Enter your guess:", key=f"guess_input_{difficulty}")

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

# FIXME: New Game button always called random.randint(1, 100), silently ignoring
# the selected difficulty and always resetting to the Normal range.
# FIX: Replace hardcoded (1, 100) with `low` and `high` from get_range_for_difficulty()
if new_game:
    st.session_state.attempts = 0
    st.session_state.secret = random.randint(low, high)
    # FIXME: status was never reset here, so after winning or losing the early-stop
    # check at line 85 would immediately halt the new game.
    # FIX: Reset status to "playing" so the player can actually play again.
    st.session_state.status = "playing"
    st.success("New game started.")
    st.rerun()

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    st.stop()

if submit:
    ok, guess_int, err = parse_guess(raw_guess)

    # FIXME: Invalid input (e.g. "" or "abc") was appended to history even when
    # parse_guess() failed, recording raw invalid strings instead of valid integers.
    # FIX: Removed the history.append(raw_guess) call from the invalid branch so
    # only successfully parsed guesses are recorded in history.
    if not ok:
        st.error(err)
    else:
        # FIXME: attempts += 1 ran before input validation, so invalid guesses
        # (empty field or non-number) still consumed an attempt.
        # FIX: Move the increment inside the valid-input branch so only
        # successful parses count against the player's attempts.
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIXME: secret was alternately cast to str on even attempts and kept as int
        # on odd attempts, causing check_guess() to always fail on even attempts
        # because comparing an int guess to a str secret never matches.
        # FIX: Remove the type-switching logic and always pass secret as int
        outcome, message = check_guess(guess_int, st.session_state.secret)

        # FIXME: show_hint = False suppressed all feedback, making the game unplayable
        # FIX: Always show directional feedback; show_hint only controls the hint wording
        if outcome != "Win":
            if show_hint:
                st.warning(message)
            else:
                st.info("Guess recorded.")

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
