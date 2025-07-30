import re
from dataclasses import dataclass

from ..exceptions import InvalidUrlFormatError


@dataclass(frozen=True)
class URL:
    """Repository URL value object with validation for GitHub, GitLab, and Bitbucket."""

    value: str

    def __post_init__(self) -> None:
        """Validate URL value."""
        self._validate()

    def get_username_and_project(self) -> tuple[str, str]:
        """Extract username and project name from URL."""
        pattern = r"^https?://(?:github\.com|gitlab\.com|bitbucket\.org)/([a-zA-Z0-9]([a-zA-Z0-9\-_]*[a-zA-Z0-9])?)/([a-zA-Z0-9]([a-zA-Z0-9\-_.]*[a-zA-Z0-9])?)(?:\.git)?/?$"

        match = re.match(pattern, self.value)
        if match:
            username = match.group(1)
            project = match.group(3)
            # Remove .git suffix from project name if present
            if project.endswith(".git"):
                project = project[:-4]
            return username, project

        raise InvalidUrlFormatError()

    def get_provider(self) -> str:
        """Extract provider name from URL."""
        if "github.com" in self.value:
            return "github"
        elif "gitlab.com" in self.value:
            return "gitlab"
        elif "bitbucket.org" in self.value:
            return "bitbucket"
        else:
            raise InvalidUrlFormatError()

    def __str__(self) -> str:
        """Return the URL value."""
        return self.value

    def _validate(self) -> None:
        """Validate that URL is a valid GitHub, GitLab, or Bitbucket repository URL."""
        if not self.value or not self.value.strip():
            raise InvalidUrlFormatError()

        stripped_value = self.value.strip()

        # Define patterns for supported providers - allowing underscores in usernames
        patterns = [
            r"^https?://github\.com/([a-zA-Z0-9]([a-zA-Z0-9\-_]*[a-zA-Z0-9])?)/([a-zA-Z0-9]([a-zA-Z0-9\-_.]*[a-zA-Z0-9])?)(?:\.git)?/?$",
            r"^https?://gitlab\.com/([a-zA-Z0-9]([a-zA-Z0-9\-_]*[a-zA-Z0-9])?)/([a-zA-Z0-9]([a-zA-Z0-9\-_.]*[a-zA-Z0-9])?)(?:\.git)?/?$",
            r"^https?://bitbucket\.org/([a-zA-Z0-9]([a-zA-Z0-9\-_]*[a-zA-Z0-9])?)/([a-zA-Z0-9]([a-zA-Z0-9\-_.]*[a-zA-Z0-9])?)(?:\.git)?/?$",
        ]

        # Check if URL matches any of the supported patterns
        for pattern in patterns:
            if re.match(pattern, stripped_value):
                object.__setattr__(self, "value", stripped_value)
                return

        raise InvalidUrlFormatError()
