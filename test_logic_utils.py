"""
pytest suite for logic_utils.py — focused on three edge-case categories:

  Edge Case 1 — Negative numbers pass parse_guess validation and consume an attempt
  Edge Case 2 — Decimal inputs are silently truncated (3.9 → 3, not 4)
  Edge Case 3 — Score has no lower floor; repeated wrong guesses drive it negative
"""

import pytest
from logic_utils import parse_guess, check_guess, update_score


# ---------------------------------------------------------------------------
# Edge Case 1: Negative number inputs
# ---------------------------------------------------------------------------

class TestNegativeInputs:
    """Negative numbers should ideally be rejected or at least handled predictably."""

    def test_negative_integer_is_accepted(self):
        """parse_guess currently accepts "-5" as valid — documents current behaviour."""
        ok, value, err = parse_guess("-5")
        # Current behaviour: negative numbers are NOT rejected.
        # If a fix is added to reject out-of-range values, flip this assertion.
        assert ok is True
        assert value == -5
        assert err is None

    def test_negative_integer_gives_too_low_outcome(self):
        """check_guess on a negative number should always return Too Low."""
        outcome, message = check_guess(-5, 10)
        assert outcome == "Too Low"
        assert "HIGHER" in message

    def test_negative_float_truncated_to_negative_int(self):
        """'-3.9' truncates to -3, not -4 — documents truncation direction."""
        ok, value, err = parse_guess("-3.9")
        assert ok is True
        assert value == -3   # int(float('-3.9')) == -3  (truncates toward zero)

    def test_negative_zero_string(self):
        """-0 should parse to 0 and check as a win when secret is 0 (hypothetical)."""
        ok, value, err = parse_guess("-0")
        assert ok is True
        assert value == 0


# ---------------------------------------------------------------------------
# Edge Case 2: Decimal / float inputs are silently truncated
# ---------------------------------------------------------------------------

class TestDecimalTruncation:
    """Decimals are accepted but truncated without any warning to the player."""

    def test_decimal_truncates_down_not_rounds(self):
        """3.9 → 3, not 4 — int(float(...)) truncates toward zero."""
        ok, value, err = parse_guess("3.9")
        assert ok is True
        assert value == 3   # would fail if rounding were used instead

    def test_decimal_exactly_half(self):
        """5.5 truncates to 5, not 6."""
        ok, value, err = parse_guess("5.5")
        assert ok is True
        assert value == 5

    def test_decimal_very_close_to_next_int(self):
        """9.9999 truncates to 9, not 10."""
        ok, value, err = parse_guess("9.9999")
        assert ok is True
        assert value == 9

    def test_decimal_zero(self):
        """0.7 truncates to 0."""
        ok, value, err = parse_guess("0.7")
        assert ok is True
        assert value == 0

    def test_no_error_message_for_decimal(self):
        """No warning is returned when a decimal is silently truncated."""
        ok, value, err = parse_guess("7.3")
        assert ok is True
        assert err is None   # player receives no notice that truncation occurred


# ---------------------------------------------------------------------------
# Edge Case 3: Score can go unboundedly negative
# ---------------------------------------------------------------------------

class TestScoreFloor:
    """update_score floors win points at 10 but has no floor for wrong guesses."""

    def test_wrong_guess_deducts_5(self):
        """Each non-win outcome deducts exactly 5 points."""
        assert update_score(100, "Too High", 1) == 95
        assert update_score(100, "Too Low", 1) == 95

    def test_score_goes_negative_after_many_wrong_guesses(self):
        """Score has no lower floor — 5 wrong guesses on 0 score → -25."""
        score = 0
        for attempt in range(1, 6):
            score = update_score(score, "Too Low", attempt)
        assert score == -25   # documents current unbounded behaviour

    def test_score_can_reach_large_negative(self):
        """20 consecutive wrong guesses from 0 → -100 with no safety net."""
        score = 0
        for attempt in range(1, 21):
            score = update_score(score, "Too High", attempt)
        assert score == -100

    def test_win_score_floor_is_10(self):
        """Winning on attempt 10+ is floored at 10 — existing guard works."""
        # attempt 10: 100 - 10*10 = 0 → floor kicks in → 10
        assert update_score(0, "Win", 10) == 10
        # attempt 20: 100 - 200 = -100 → floor still gives 10
        assert update_score(0, "Win", 20) == 10

    def test_wrong_guess_score_has_no_floor(self):
        """
        Contrast with win floor: wrong guesses have NO equivalent floor.
        This test documents the asymmetry as a known gap.
        """
        score = update_score(-1000, "Too Low", 1)
        assert score == -1005   # no floor — keeps going negative


# ---------------------------------------------------------------------------
# Baseline / sanity checks (to confirm the happy path still works)
# ---------------------------------------------------------------------------

class TestBaseline:
    def test_parse_valid_integer(self):
        ok, value, err = parse_guess("42")
        assert ok is True and value == 42 and err is None

    def test_parse_empty_string(self):
        ok, value, err = parse_guess("")
        assert ok is False and err == "Enter a guess."

    def test_parse_non_numeric(self):
        ok, value, err = parse_guess("abc")
        assert ok is False and err == "That is not a number."

    def test_check_guess_win(self):
        outcome, _ = check_guess(7, 7)
        assert outcome == "Win"

    def test_check_guess_too_high(self):
        outcome, _ = check_guess(10, 5)
        assert outcome == "Too High"

    def test_check_guess_too_low(self):
        outcome, _ = check_guess(3, 8)
        assert outcome == "Too Low"

    def test_update_score_win_first_attempt(self):
        assert update_score(0, "Win", 1) == 90
