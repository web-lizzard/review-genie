from dataclasses import dataclass, field

from ..exceptions import EmptyRuleError

_DEFAULT_RULES = [
    "Focus on code quality, readability, and maintainability",
    "Check for potential bugs and security vulnerabilities",
    "Verify proper error handling and edge cases",
    "Ensure code follows project conventions and best practices",
    "Review performance implications of changes",
]


@dataclass(frozen=True)
class Rules:
    """Code review rules and conventions for a project."""

    rules: list[str] = field(default_factory=lambda: _DEFAULT_RULES)

    def add_rule(self, rule: str) -> "Rules":
        """Add a new rule to the existing rules.

        Args:
            rule: New rule to add

        Returns:
            New Rules instance with the added rule
        """
        if not rule or not rule.strip():
            raise EmptyRuleError()

        new_rules = self.rules.copy()
        rule = rule.strip()

        if rule not in new_rules:
            new_rules.append(rule)

        return Rules(new_rules)

    def remove_rule(self, rule: str) -> "Rules":
        """Remove a rule from the existing rules.

        Args:
            rule: Rule to remove

        Returns:
            New Rules instance with the rule removed
        """
        if not rule or not rule.strip():
            return self

        new_rules = [r for r in self.rules if r != rule.strip()]
        return Rules(new_rules)

    def has_rule(self, rule: str) -> bool:
        """Check if a specific rule exists.

        Args:
            rule: Rule to check for

        Returns:
            True if rule exists
        """
        return rule.strip() in self.rules

    def __len__(self) -> int:
        """Return number of rules."""
        return len(self.rules)

    def __str__(self) -> str:
        """Return rules as formatted string."""
        if not self.rules:
            return "No specific rules defined"

        return "\n".join(f"• {rule}" for rule in self.rules)

    def to_text(self) -> str:
        """Convert rules to plain text format suitable for AI processing.

        Returns:
            Rules as newline-separated text
        """
        return "\n".join(self.rules)
