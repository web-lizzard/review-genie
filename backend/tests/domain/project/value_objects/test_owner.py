import pytest

from domain.project.exceptions import InvalidOwnerFormatError
from domain.project.value_objects import Owner


class TestOwner:
    """Test cases for Owner value object."""

    @pytest.mark.parametrize(
        "valid_owner",
        [
            "user",
            "organization",
            "my-org",
            "user123",
            "org-123",
            "123user",
            "a",
            "a-b",
            "123",
            "user-name-123",
            "MyOrganization",
        ],
    )
    def test_valid_owner_creation(self, valid_owner: str) -> None:
        """Test creating Owner with valid owner names."""
        owner = Owner(valid_owner)
        assert owner.value == valid_owner.strip()
        assert str(owner) == valid_owner.strip()

    @pytest.mark.parametrize(
        "owner_with_whitespace, expected",
        [
            (" user ", "user"),
            ("\torg\t", "org"),
            ("\ntest\n", "test"),
            ("  spaced-org  ", "spaced-org"),
        ],
    )
    def test_owner_whitespace_trimming(
        self, owner_with_whitespace: str, expected: str
    ) -> None:
        """Test that Owner trims whitespace from input."""
        owner = Owner(owner_with_whitespace)
        assert owner.value == expected
        assert str(owner) == expected

    @pytest.mark.parametrize(
        "invalid_owner",
        [
            "",  # Empty string
            "   ",  # Only whitespace
            "\t\n",  # Only tabs and newlines
            "-user",  # Starts with hyphen
            "user-",  # Ends with hyphen
            "user@name",  # Invalid character @
            "user.name",  # Invalid character .
            "user_name",  # Invalid character _
            "user name",  # Space in middle
            "user/name",  # Invalid character /
            "-",  # Single hyphen
            "--",  # Multiple hyphens
        ],
    )
    def test_invalid_owner_creation(self, invalid_owner: str) -> None:
        """Test that Owner raises InvalidOwnerFormatError for invalid names."""
        with pytest.raises(InvalidOwnerFormatError):
            Owner(invalid_owner)

    def test_owner_immutability(self) -> None:
        """Test that Owner is immutable (frozen dataclass)."""
        owner = Owner("testuser")
        with pytest.raises(AttributeError):
            owner.value = "newuser"  # type: ignore

    def test_owner_equality(self) -> None:
        """Test Owner equality comparison."""
        owner1 = Owner("testuser")
        owner2 = Owner("testuser")
        owner3 = Owner("differentuser")

        assert owner1 == owner2
        assert owner1 != owner3
        assert hash(owner1) == hash(owner2)
        assert hash(owner1) != hash(owner3)

    def test_owner_str_representation(self) -> None:
        """Test string representation of Owner."""
        owner = Owner("myorg")
        assert str(owner) == "myorg"

    @pytest.mark.parametrize(
        "owner_name",
        [
            "a",
            "test-user-123",
            "TestUser",
        ],
    )
    def test_owner_regex_edge_cases(self, owner_name: str) -> None:
        """Test edge cases for Owner regex validation."""
        owner = Owner(owner_name)
        assert owner.value == owner_name
