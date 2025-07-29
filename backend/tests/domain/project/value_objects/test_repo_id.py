import pytest

from domain.project.exceptions import (
    EmptyRepositoryIdError,
    InvalidRepositoryIdFormatError,
)
from domain.project.value_objects import RepositoryId


class TestRepositoryId:
    """Test cases for RepositoryId value object."""

    @pytest.mark.parametrize(
        "valid_repo_id",
        [
            "repo",
            "my-repo",
            "repo123",
            "repo-123",
            "123repo",
            "a",
            "a-b",
            "123",
            "repo-name-123",
            "MyRepository",
            "repo.name",
            "repo_name",
            "repo-name_with.dots",
            "complex-repo_name.with123",
            "repo.git",
            "repo_123.test",
        ],
    )
    def test_valid_repository_id_creation(self, valid_repo_id: str) -> None:
        """Test creating RepositoryId with valid repository names."""
        repo_id = RepositoryId(valid_repo_id)
        assert repo_id.value == valid_repo_id.strip()
        assert str(repo_id) == valid_repo_id.strip()

    @pytest.mark.parametrize(
        "repo_id_with_whitespace, expected",
        [
            (" repo ", "repo"),
            ("\trepo\t", "repo"),
            ("\nrepo\n", "repo"),
            ("  my-repo  ", "my-repo"),
            (" repo.name ", "repo.name"),
        ],
    )
    def test_repository_id_whitespace_trimming(
        self, repo_id_with_whitespace: str, expected: str
    ) -> None:
        """Test that RepositoryId trims whitespace from input."""
        repo_id = RepositoryId(repo_id_with_whitespace)
        assert repo_id.value == expected
        assert str(repo_id) == expected

    @pytest.mark.parametrize(
        "empty_repo_id",
        [
            "",  # Empty string
            "   ",  # Only whitespace
            "\t\n",  # Only tabs and newlines
            "\r\n\t ",  # Various whitespace characters
        ],
    )
    def test_empty_repository_id_creation(self, empty_repo_id: str) -> None:
        """Test that RepositoryId raises EmptyRepositoryIdError for empty values."""
        with pytest.raises(EmptyRepositoryIdError):
            RepositoryId(empty_repo_id)

    @pytest.mark.parametrize(
        "invalid_repo_id",
        [
            "-repo",  # Starts with hyphen
            "repo-",  # Ends with hyphen
            ".repo",  # Starts with dot
            "repo.",  # Ends with dot
            "_repo",  # Starts with underscore
            "repo_",  # Ends with underscore
            "repo@name",  # Invalid character @
            "repo name",  # Space in middle
            "repo/name",  # Invalid character /
            "repo#name",  # Invalid character #
            "repo$name",  # Invalid character $
            "-",  # Single hyphen
            ".",  # Single dot
            "_",  # Single underscore
            "repo+name",  # Invalid character +
            "repo=name",  # Invalid character =
        ],
    )
    def test_invalid_repository_id_creation(self, invalid_repo_id: str) -> None:
        """Test that RepositoryId raises InvalidRepositoryIdFormatError for invalid names."""
        with pytest.raises(InvalidRepositoryIdFormatError):
            RepositoryId(invalid_repo_id)

    def test_repository_id_immutability(self) -> None:
        """Test that RepositoryId is immutable (frozen dataclass)."""
        repo_id = RepositoryId("testrepo")
        with pytest.raises(AttributeError):
            repo_id.value = "newrepo"  # type: ignore

    def test_repository_id_equality(self) -> None:
        """Test RepositoryId equality comparison."""
        repo_id1 = RepositoryId("testrepo")
        repo_id2 = RepositoryId("testrepo")
        repo_id3 = RepositoryId("differentrepo")

        assert repo_id1 == repo_id2
        assert repo_id1 != repo_id3
        assert hash(repo_id1) == hash(repo_id2)
        assert hash(repo_id1) != hash(repo_id3)

    def test_repository_id_str_representation(self) -> None:
        """Test string representation of RepositoryId."""
        repo_id = RepositoryId("myrepo")
        assert str(repo_id) == "myrepo"

    def test_repository_id_regex_edge_cases(self) -> None:
        """Test edge cases for RepositoryId regex validation."""
        # Single character
        single_char = RepositoryId("a")
        assert single_char.value == "a"

        # Alphanumeric with dots, underscores, and hyphens
        complex_name = RepositoryId("test-repo_name.git")
        assert complex_name.value == "test-repo_name.git"

        # Numbers only
        numbers_only = RepositoryId("123")
        assert numbers_only.value == "123"

        # Mixed case
        mixed_case = RepositoryId("TestRepository")
        assert mixed_case.value == "TestRepository"

    def test_repository_id_common_patterns(self) -> None:
        """Test common repository naming patterns."""
        # GitHub-style repository names
        github_style = RepositoryId("awesome-project")
        assert github_style.value == "awesome-project"

        # Package-style names with dots
        package_style = RepositoryId("com.example.package")
        assert package_style.value == "com.example.package"

        # Version-style names
        version_style = RepositoryId("project-v1.2.3")
        assert version_style.value == "project-v1.2.3"

        # Git repository names
        git_repo = RepositoryId("project.git")
        assert git_repo.value == "project.git"
