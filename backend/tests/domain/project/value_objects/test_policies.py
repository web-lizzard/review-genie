import pytest

from domain.project.value_objects import Policies, PullRequestPolicy, RetryLimitType


class TestPullRequestPolicy:
    """Test cases for PullRequestPolicy enum."""

    def test_pull_request_policy_values(self) -> None:
        """Test that PullRequestPolicy has expected values."""
        assert PullRequestPolicy.ALL == "all"
        assert PullRequestPolicy.NONE == "none"
        assert PullRequestPolicy.MAIN_BRANCH_ONLY == "main_branch_only"

    def test_pull_request_policy_membership(self) -> None:
        """Test membership checks for PullRequestPolicy."""
        assert "all" in PullRequestPolicy
        assert "none" in PullRequestPolicy
        assert "main_branch_only" in PullRequestPolicy
        assert "unknown" not in PullRequestPolicy

    @pytest.mark.parametrize(
        "policy_value",
        [
            PullRequestPolicy.ALL,
            PullRequestPolicy.NONE,
            PullRequestPolicy.MAIN_BRANCH_ONLY,
        ],
    )
    def test_pull_request_policy_iteration(
        self, policy_value: PullRequestPolicy
    ) -> None:
        """Test that all PullRequestPolicy values are accessible."""
        assert policy_value in PullRequestPolicy
        assert isinstance(policy_value.value, str)

    def test_pull_request_policy_as_string_enum(self) -> None:
        """Test that PullRequestPolicy works as string enum."""
        assert PullRequestPolicy.ALL == "all"
        assert PullRequestPolicy.NONE.value == "none"
        assert PullRequestPolicy.MAIN_BRANCH_ONLY.value == "main_branch_only"


class TestRetryLimitType:
    """Test cases for RetryLimitType enum."""

    def test_retry_limit_type_values(self) -> None:
        """Test that RetryLimitType has expected values."""
        assert RetryLimitType.COUNT == "count"
        assert RetryLimitType.TIME == "time"

    def test_retry_limit_type_membership(self) -> None:
        """Test membership checks for RetryLimitType."""
        assert "count" in RetryLimitType
        assert "time" in RetryLimitType
        assert "unknown" not in RetryLimitType

    @pytest.mark.parametrize(
        "limit_type",
        [
            RetryLimitType.COUNT,
            RetryLimitType.TIME,
        ],
    )
    def test_retry_limit_type_iteration(self, limit_type: RetryLimitType) -> None:
        """Test that all RetryLimitType values are accessible."""
        assert limit_type in RetryLimitType
        assert isinstance(limit_type.value, str)

    def test_retry_limit_type_as_string_enum(self) -> None:
        """Test that RetryLimitType works as string enum."""
        assert RetryLimitType.COUNT == "count"
        assert RetryLimitType.TIME.value == "time"
        assert RetryLimitType.COUNT.value == "count"


class TestPolicies:
    """Test cases for Policies value object."""

    @pytest.mark.parametrize(
        "pr_policy, retry_type, retry_value",
        [
            (PullRequestPolicy.ALL, RetryLimitType.COUNT, 3),
            (PullRequestPolicy.NONE, RetryLimitType.COUNT, 5),
            (PullRequestPolicy.MAIN_BRANCH_ONLY, RetryLimitType.TIME, 10),
            (PullRequestPolicy.ALL, RetryLimitType.TIME, 1),
            (PullRequestPolicy.NONE, RetryLimitType.COUNT, 0),
        ],
    )
    def test_valid_policies_creation(
        self, pr_policy: PullRequestPolicy, retry_type: RetryLimitType, retry_value: int
    ) -> None:
        """Test creating Policies with valid combinations."""
        policies = Policies(
            pull_request_policy=pr_policy,
            retry_limit_type=retry_type,
            retry_limit_value=retry_value,
        )

        assert policies.pull_request_policy == pr_policy
        assert policies.retry_limit_type == retry_type
        assert policies.retry_limit_value == retry_value

    def test_policies_immutability(self) -> None:
        """Test that Policies is immutable (frozen dataclass)."""
        policies = Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=3,
        )

        with pytest.raises(AttributeError):
            policies.pull_request_policy = PullRequestPolicy.NONE  # type: ignore

        with pytest.raises(AttributeError):
            policies.retry_limit_type = RetryLimitType.TIME  # type: ignore

        with pytest.raises(AttributeError):
            policies.retry_limit_value = 5  # type: ignore

    def test_policies_equality(self) -> None:
        """Test Policies equality comparison."""
        policies1 = Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=3,
        )

        policies2 = Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=3,
        )

        policies3 = Policies(
            pull_request_policy=PullRequestPolicy.NONE,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=3,
        )

        assert policies1 == policies2
        assert policies1 != policies3
        assert hash(policies1) == hash(policies2)
        assert hash(policies1) != hash(policies3)

    @pytest.mark.parametrize(
        "retry_value",
        [0, 1, 5, 10, 100, 1000],
    )
    def test_policies_with_different_retry_values(self, retry_value: int) -> None:
        """Test Policies creation with different retry limit values."""
        policies = Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=retry_value,
        )

        assert policies.retry_limit_value == retry_value

    def test_policies_all_pull_request_combinations(self) -> None:
        """Test Policies with all PullRequestPolicy combinations."""
        for pr_policy in PullRequestPolicy:
            for retry_type in RetryLimitType:
                policies = Policies(
                    pull_request_policy=pr_policy,
                    retry_limit_type=retry_type,
                    retry_limit_value=5,
                )

                assert policies.pull_request_policy == pr_policy
                assert policies.retry_limit_type == retry_type
                assert policies.retry_limit_value == 5

    def test_policies_default_configuration(self) -> None:
        """Test common default configuration for Policies."""
        default_policies = Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=3,
        )

        assert default_policies.pull_request_policy == PullRequestPolicy.ALL
        assert default_policies.retry_limit_type == RetryLimitType.COUNT
        assert default_policies.retry_limit_value == 3

    def test_policies_restrictive_configuration(self) -> None:
        """Test restrictive configuration for Policies."""
        restrictive_policies = Policies(
            pull_request_policy=PullRequestPolicy.NONE,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=0,
        )

        assert restrictive_policies.pull_request_policy == PullRequestPolicy.NONE
        assert restrictive_policies.retry_limit_type == RetryLimitType.COUNT
        assert restrictive_policies.retry_limit_value == 0

    def test_policies_main_branch_only_configuration(self) -> None:
        """Test main branch only configuration for Policies."""
        main_branch_policies = Policies(
            pull_request_policy=PullRequestPolicy.MAIN_BRANCH_ONLY,
            retry_limit_type=RetryLimitType.TIME,
            retry_limit_value=60,  # 60 minutes, for example
        )

        assert (
            main_branch_policies.pull_request_policy
            == PullRequestPolicy.MAIN_BRANCH_ONLY
        )
        assert main_branch_policies.retry_limit_type == RetryLimitType.TIME
        assert main_branch_policies.retry_limit_value == 60

    def test_policies_attribute_access(self) -> None:
        """Test that all Policies attributes are accessible."""
        policies = Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=5,
        )

        # Test that all attributes exist and are accessible
        assert hasattr(policies, "pull_request_policy")
        assert hasattr(policies, "retry_limit_type")
        assert hasattr(policies, "retry_limit_value")

        # Test attribute types
        assert isinstance(policies.pull_request_policy, PullRequestPolicy)
        assert isinstance(policies.retry_limit_type, RetryLimitType)
        assert isinstance(policies.retry_limit_value, int)

    def test_policies_edge_case_values(self) -> None:
        """Test Policies with edge case values."""
        # Test with maximum typical values
        max_policies = Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=999999,
        )
        assert max_policies.retry_limit_value == 999999

        # Test with zero retry value
        zero_retry_policies = Policies(
            pull_request_policy=PullRequestPolicy.NONE,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=0,
        )
        assert zero_retry_policies.retry_limit_value == 0
