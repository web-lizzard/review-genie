import pytest

from domain.project.exceptions import InvalidUrlFormatError
from domain.project.value_objects import URL


class TestURL:
    """Test cases for URL value object."""

    @pytest.mark.parametrize(
        "valid_url",
        [
            # GitHub URLs
            "https://github.com/user/repo",
            "http://github.com/user/repo",
            "https://github.com/user/repo.git",
            "https://github.com/user/repo/",
            "https://github.com/user-name/repo-name",
            "https://github.com/user123/repo123",
            "https://github.com/a/b",
            "https://github.com/test_user/test.repo",
            "https://github.com/user/repo_with_underscores",

            # GitLab URLs
            "https://gitlab.com/user/repo",
            "http://gitlab.com/user/repo",
            "https://gitlab.com/user/repo.git",
            "https://gitlab.com/user/repo/",
            "https://gitlab.com/user-name/repo-name",
            "https://gitlab.com/user123/repo123",
            "https://gitlab.com/a/b",

            # Bitbucket URLs
            "https://bitbucket.org/user/repo",
            "http://bitbucket.org/user/repo",
            "https://bitbucket.org/user/repo.git",
            "https://bitbucket.org/user/repo/",
            "https://bitbucket.org/user-name/repo-name",
            "https://bitbucket.org/user123/repo123",
            "https://bitbucket.org/a/b",
        ],
    )
    def test_valid_url_creation(self, valid_url: str) -> None:
        """Test creating URL with valid repository URLs."""
        url = URL(valid_url)
        assert url.value == valid_url

    @pytest.mark.parametrize(
        "invalid_url",
        [
            # Empty and whitespace
            "",
            "   ",
            "\t",
            "\n",

            # Invalid domains
            "https://github.io/user/repo",
            "https://gitlab.io/user/repo",
            "https://bitbucket.com/user/repo",
            "https://example.com/user/repo",

            # Missing username or repo
            "https://github.com/user",
            "https://github.com/user/",
            "https://github.com//repo",
            "https://github.com/",
            "https://github.com",

            # Invalid characters in username
            "https://github.com/user@name/repo",
            "https://github.com/user.name/repo",
            "https://github.com/user space/repo",
            "https://github.com/user$/repo",

            # Invalid characters in repo name
            "https://github.com/user/repo space",
            "https://github.com/user/repo@name",
            "https://github.com/user/repo$",

            # Starting or ending with hyphen
            "https://github.com/-user/repo",
            "https://github.com/user-/repo",
            "https://github.com/user/-repo",
            "https://github.com/user/repo-",

            # Non-HTTP protocols
            "ftp://github.com/user/repo",
            "ssh://github.com/user/repo",
            "git@github.com:user/repo.git",

            # Malformed URLs
            "github.com/user/repo",
            "www.github.com/user/repo",
            "https://github.com/user/repo/extra/path",
            "https://github.com/user/repo?query=param",
            "https://github.com/user/repo#anchor",

            # Too many path segments
            "https://github.com/user/repo/subfolder",
            "https://gitlab.com/user/repo/another/path",
        ],
    )
    def test_invalid_url_creation(self, invalid_url: str) -> None:
        """Test that invalid URLs raise InvalidUrlFormatError."""
        with pytest.raises(InvalidUrlFormatError):
            URL(invalid_url)

    def test_url_with_whitespace_strips(self) -> None:
        """Test that URLs with leading/trailing whitespace are stripped."""
        url = URL("  https://github.com/user/repo  ")
        assert url.value == "https://github.com/user/repo"

    @pytest.mark.parametrize(
        "url_value,expected_provider",
        [
            ("https://github.com/user/repo", "github"),
            ("https://gitlab.com/user/repo", "gitlab"),
            ("https://bitbucket.org/user/repo", "bitbucket"),
            ("http://github.com/user/repo.git", "github"),
            ("https://gitlab.com/user/repo/", "gitlab"),
        ],
    )
    def test_get_provider(self, url_value: str, expected_provider: str) -> None:
        """Test extracting provider from URL."""
        url = URL(url_value)
        assert url.get_provider() == expected_provider

    @pytest.mark.parametrize(
        "url_value,expected_username,expected_project",
        [
            ("https://github.com/user/repo", "user", "repo"),
            ("https://gitlab.com/test-user/test-repo", "test-user", "test-repo"),
            ("https://bitbucket.org/user123/repo123", "user123", "repo123"),
            ("https://github.com/a/b", "a", "b"),
            ("https://github.com/user/repo.git", "user", "repo"),
            ("https://gitlab.com/user/repo/", "user", "repo"),
            ("https://github.com/user/test_repo", "user", "test_repo"),
            ("https://github.com/user/test.repo", "user", "test.repo"),
        ],
    )
    def test_get_username_and_project(
        self, url_value: str, expected_username: str, expected_project: str
    ) -> None:
        """Test extracting username and project from URL."""
        url = URL(url_value)
        username, project = url.get_username_and_project()
        assert username == expected_username
        assert project == expected_project

    def test_str_representation(self) -> None:
        """Test string representation of URL."""
        url_value = "https://github.com/user/repo"
        url = URL(url_value)
        assert str(url) == url_value

    def test_url_immutability(self) -> None:
        """Test that URL value object is immutable."""
        url = URL("https://github.com/user/repo")
        with pytest.raises(AttributeError):
            url.value = "https://github.com/other/repo"  # type: ignore

    def test_url_equality(self) -> None:
        """Test URL equality comparison."""
        url1 = URL("https://github.com/user/repo")
        url2 = URL("https://github.com/user/repo")
        url3 = URL("https://gitlab.com/user/repo")

        assert url1 == url2
        assert url1 != url3
        assert hash(url1) == hash(url2)
        assert hash(url1) != hash(url3)
