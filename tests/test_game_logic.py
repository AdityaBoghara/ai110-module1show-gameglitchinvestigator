from logic_utils import check_guess, get_range_for_difficulty


def test_hard_range_larger_than_normal():
    # Bug fix: Hard difficulty was 1-50, Normal was 1-100 (Hard was easier)
    # Hard should have a wider range than Normal to be more difficult
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high, "Hard difficulty should have a larger range than Normal"


def test_winning_guess():
    outcome, message = check_guess(50, 50)
    assert outcome == "Win"
    assert message == "🎉 Correct!"

def test_guess_too_high():
    outcome, message = check_guess(60, 50)
    assert outcome == "Too High"
    assert "LOWER" in message  # hint must say go lower, not higher

def test_guess_too_low():
    outcome, message = check_guess(40, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message  # hint must say go higher, not lower

def test_hints_not_swapped():
    # Regression: original bug had hints backwards
    high_outcome, high_msg = check_guess(99, 1)
    low_outcome, low_msg = check_guess(1, 99)
    assert high_outcome == "Too High" and "LOWER" in high_msg
    assert low_outcome == "Too Low" and "HIGHER" in low_msg

def test_mixed_type_int_guess_str_secret():
    # App passes secret as str on even attempts
    outcome, message = check_guess(5, "10")
    assert outcome == "Too Low"
    assert "HIGHER" in message

def test_mixed_type_str_comparison_not_lexicographic():
    # Regression: "9" > "10" is True lexicographically — must use numeric comparison
    outcome, _ = check_guess(9, "10")
    assert outcome == "Too Low", "9 < 10 numerically; must not use lexicographic string comparison"

def test_mixed_type_win():
    outcome, message = check_guess(42, "42")
    assert outcome == "Win"
    assert message == "🎉 Correct!"

def test_invalid_input_returns_invalid():
    outcome, _ = check_guess("abc", "xyz")
    assert outcome == "Invalid"
