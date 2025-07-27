import pytest

from domain.project.exceptions import EmptyRuleError
from domain.project.value_objects import Rules


class TestRules:
    """Test cases for Rules value object."""

    def test_default_rules_creation(self) -> None:
        """Test creating Rules with default rules."""
        rules = Rules()

        assert len(rules) == 5
        assert "Focus on code quality, readability, and maintainability" in rules.rules
        assert "Check for potential bugs and security vulnerabilities" in rules.rules
        assert "Verify proper error handling and edge cases" in rules.rules
        assert (
            "Ensure code follows project conventions and best practices" in rules.rules
        )
        assert "Review performance implications of changes" in rules.rules

    def test_custom_rules_creation(self) -> None:
        """Test creating Rules with custom rules list."""
        custom_rules = ["Rule 1", "Rule 2", "Rule 3"]
        rules = Rules(custom_rules)

        assert len(rules) == 3
        assert rules.rules == custom_rules

    def test_empty_rules_creation(self) -> None:
        """Test creating Rules with empty rules list."""
        rules = Rules([])

        assert len(rules) == 0
        assert rules.rules == []

    @pytest.mark.parametrize(
        "new_rule",
        [
            "Check for proper documentation",
            "Verify unit test coverage",
            "Review API design consistency",
            "Ensure backward compatibility",
            "Check for memory leaks",
        ],
    )
    def test_add_rule_valid(self, new_rule: str) -> None:
        """Test adding valid rules to Rules."""
        rules = Rules([])
        new_rules = rules.add_rule(new_rule)

        assert len(new_rules) == 1
        assert new_rule in new_rules.rules
        assert new_rules.has_rule(new_rule)
        # Original rules object should remain unchanged
        assert len(rules) == 0

    @pytest.mark.parametrize(
        "rule_with_whitespace, expected",
        [
            ("  Check documentation  ", "Check documentation"),
            ("\tReview tests\t", "Review tests"),
            ("\nValidate input\n", "Validate input"),
            ("   Multiple   spaces   ", "Multiple   spaces"),
        ],
    )
    def test_add_rule_whitespace_trimming(
        self, rule_with_whitespace: str, expected: str
    ) -> None:
        """Test that add_rule trims whitespace from rules."""
        rules = Rules([])
        new_rules = rules.add_rule(rule_with_whitespace)

        assert expected in new_rules.rules
        assert new_rules.has_rule(expected)

    @pytest.mark.parametrize(
        "empty_rule",
        [
            "",  # Empty string
            "   ",  # Only whitespace
            "\t\n",  # Only tabs and newlines
            "\r\n\t ",  # Various whitespace characters
        ],
    )
    def test_add_rule_empty(self, empty_rule: str) -> None:
        """Test that adding empty rule raises EmptyRuleError."""
        rules = Rules([])

        with pytest.raises(EmptyRuleError):
            rules.add_rule(empty_rule)

    def test_add_rule_duplicate(self) -> None:
        """Test that adding duplicate rule doesn't create duplicates."""
        initial_rules = ["Existing rule", "Another rule"]
        rules = Rules(initial_rules)

        # Add existing rule
        new_rules = rules.add_rule("Existing rule")

        assert len(new_rules) == 2  # Should remain the same
        assert new_rules.rules == initial_rules

    def test_add_rule_to_default(self) -> None:
        """Test adding rule to default rules."""
        rules = Rules()  # Start with default rules
        initial_count = len(rules)

        new_rules = rules.add_rule("New custom rule")

        assert len(new_rules) == initial_count + 1
        assert "New custom rule" in new_rules.rules
        assert new_rules.has_rule("New custom rule")

    @pytest.mark.parametrize(
        "rule_to_remove",
        [
            "Focus on code quality, readability, and maintainability",
            "Check for potential bugs and security vulnerabilities",
            "Verify proper error handling and edge cases",
        ],
    )
    def test_remove_rule_existing(self, rule_to_remove: str) -> None:
        """Test removing existing rules from default Rules."""
        rules = Rules()  # Start with default rules
        initial_count = len(rules)

        new_rules = rules.remove_rule(rule_to_remove)

        assert len(new_rules) == initial_count - 1
        assert rule_to_remove not in new_rules.rules
        assert not new_rules.has_rule(rule_to_remove)
        # Original rules should remain unchanged
        assert len(rules) == initial_count

    def test_remove_rule_non_existing(self) -> None:
        """Test removing non-existing rule."""
        rules = Rules(["Rule 1", "Rule 2"])

        new_rules = rules.remove_rule("Non-existing rule")

        assert len(new_rules) == 2
        assert new_rules.rules == ["Rule 1", "Rule 2"]

    @pytest.mark.parametrize(
        "empty_rule",
        [
            "",  # Empty string
            "   ",  # Only whitespace
            "\t\n",  # Only tabs and newlines
        ],
    )
    def test_remove_rule_empty(self, empty_rule: str) -> None:
        """Test removing empty rule returns same Rules."""
        rules = Rules(["Rule 1", "Rule 2"])

        new_rules = rules.remove_rule(empty_rule)

        assert new_rules is rules  # Should return the same object
        assert len(new_rules) == 2

    def test_remove_rule_whitespace_trimming(self) -> None:
        """Test that remove_rule trims whitespace when matching."""
        rules = Rules(["Test rule", "Another rule"])

        new_rules = rules.remove_rule("  Test rule  ")

        assert len(new_rules) == 1
        assert "Test rule" not in new_rules.rules
        assert "Another rule" in new_rules.rules

    @pytest.mark.parametrize(
        "rule, should_exist",
        [
            ("Focus on code quality, readability, and maintainability", True),
            ("Check for potential bugs and security vulnerabilities", True),
            ("Non-existing rule", False),
            ("", False),
            ("   ", False),
        ],
    )
    def test_has_rule(self, rule: str, should_exist: bool) -> None:
        """Test has_rule method with various inputs."""
        rules = Rules()  # Default rules

        assert rules.has_rule(rule) == should_exist

    def test_has_rule_whitespace_trimming(self) -> None:
        """Test that has_rule trims whitespace when checking."""
        rules = Rules(["Test rule"])

        assert rules.has_rule("  Test rule  ")
        assert not rules.has_rule("  Different rule  ")

    def test_rules_immutability(self) -> None:
        """Test that Rules is immutable (frozen dataclass)."""
        rules = Rules(["Rule 1"])

        with pytest.raises(AttributeError):
            rules.rules = ["New rule"]  # type: ignore

    def test_rules_length(self) -> None:
        """Test __len__ method."""
        rules_empty = Rules([])
        rules_default = Rules()
        rules_custom = Rules(["Rule 1", "Rule 2", "Rule 3"])

        assert len(rules_empty) == 0
        assert len(rules_default) == 5  # Default rules count
        assert len(rules_custom) == 3

    def test_rules_str_representation_with_rules(self) -> None:
        """Test string representation with rules."""
        custom_rules = ["Rule 1", "Rule 2", "Rule 3"]
        rules = Rules(custom_rules)

        str_repr = str(rules)

        assert "• Rule 1" in str_repr
        assert "• Rule 2" in str_repr
        assert "• Rule 3" in str_repr
        assert str_repr.count("•") == 3

    def test_rules_str_representation_empty(self) -> None:
        """Test string representation with empty rules."""
        rules = Rules([])

        assert str(rules) == "No specific rules defined"

    def test_rules_to_text_with_rules(self) -> None:
        """Test to_text method with rules."""
        custom_rules = ["Rule 1", "Rule 2", "Rule 3"]
        rules = Rules(custom_rules)

        text_output = rules.to_text()

        assert text_output == "Rule 1\nRule 2\nRule 3"

    def test_rules_to_text_empty(self) -> None:
        """Test to_text method with empty rules."""
        rules = Rules([])

        assert rules.to_text() == ""

    def test_rules_to_text_default(self) -> None:
        """Test to_text method with default rules."""
        rules = Rules()

        text_output = rules.to_text()
        lines = text_output.split("\n")

        assert len(lines) == 5
        assert "Focus on code quality, readability, and maintainability" in lines
        assert "Check for potential bugs and security vulnerabilities" in lines

    def test_rules_equality(self) -> None:
        """Test Rules equality comparison."""
        rules1 = Rules(["Rule 1", "Rule 2"])
        rules2 = Rules(["Rule 1", "Rule 2"])
        rules3 = Rules(["Rule 1", "Rule 3"])

        assert rules1 == rules2
        assert rules1 != rules3
        # Note: Rules cannot be hashed because it contains a list

    def test_rules_workflow(self) -> None:
        """Test complete workflow of Rules operations."""
        # Start with default rules
        rules = Rules()
        initial_count = len(rules)

        # Add custom rule
        rules = rules.add_rule("Custom rule 1")
        assert len(rules) == initial_count + 1
        assert rules.has_rule("Custom rule 1")

        # Add another rule
        rules = rules.add_rule("Custom rule 2")
        assert len(rules) == initial_count + 2
        assert rules.has_rule("Custom rule 2")

        # Remove a default rule
        rules = rules.remove_rule(
            "Focus on code quality, readability, and maintainability"
        )
        assert len(rules) == initial_count + 1
        assert not rules.has_rule(
            "Focus on code quality, readability, and maintainability"
        )

        # Remove custom rule
        rules = rules.remove_rule("Custom rule 1")
        assert len(rules) == initial_count
        assert not rules.has_rule("Custom rule 1")
        assert rules.has_rule("Custom rule 2")
