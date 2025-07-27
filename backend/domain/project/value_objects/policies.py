from dataclasses import dataclass
from enum import Enum


class PullRequestPolicy(str, Enum):
    """Policy determining when to create analyses for Pull Requests."""

    ALL = "all"  # Analyze all Pull Requests
    NONE = "none"  # Do not analyze any Pull Requests
    MAIN_BRANCH_ONLY = "main_branch_only"  # Analyze only PRs to main branch


class RetryLimitType(str, Enum):
    """Type of retry limit for analysis retries."""

    COUNT = "count"  # Limit by number of attempts
    TIME = "time"  # Limit by time window (future extension)


@dataclass(frozen=True)
class Policies:
    """Analysis creation policies for a project."""

    pull_request_policy: PullRequestPolicy
    retry_limit_type: RetryLimitType
    retry_limit_value: int
