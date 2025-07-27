from abc import ABC, abstractmethod

from domain.project.value_objects import Policies, PullRequestPolicy, RetryLimitType


class PoliciesFactory(ABC):
    @abstractmethod
    def create_policies(self) -> Policies: ...


class DefaultPoliciesFactory(PoliciesFactory):
    def create_policies(self) -> Policies:
        return Policies(
            pull_request_policy=PullRequestPolicy.ALL,
            retry_limit_type=RetryLimitType.COUNT,
            retry_limit_value=2,
        )
