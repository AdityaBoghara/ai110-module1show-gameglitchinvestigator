def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    # FIXME: Logic breaks here
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50
    if difficulty == "Hard":
        return 1, 100
    return 1, 100
    #FIX: Refactored logic into logic_utils.py using Copilot Agent mode




def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    raise NotImplementedError("Refactor this function from app.py into logic_utils.py")


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    # FIXME: Hints were swapped ("Go HIGHER!" on too-high, "Go LOWER!" on too-low),
    # the TypeError fallback used lexicographic string comparison (e.g. "9" > "10" == True),
    # and int == str (e.g. 42 == "42") was never caught as a win
    # FIX: Normalise both values to int first, then compare
    try:
        g, s = int(guess), int(secret)
    except (ValueError, TypeError):
        return "Invalid", "❓ Invalid input"

    if g == s:
        return "Win", "🎉 Correct!"
    if g > s:
        return "Too High", "📉 Go LOWER!"
    return "Too Low", "📈 Go HIGHER!"


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    # FIXME: "Too High" awarded +5 points on even attempts instead of always deducting,
    # causing inconsistent scoring and an exploitable loophole
    # FIX: Both "Too High" and "Too Low" now consistently deduct 5 points
    if outcome == "Win":
        points = 100 - 10 * (attempt_number + 1)
        if points < 10:
            points = 10
        return current_score + points

    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
