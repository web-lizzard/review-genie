from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, composite, mapped_column

from domain.project import value_objects as vo


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""

    pass


class ProjectIdORM(vo.ProjectId):
    """ORM representation of ProjectId value object."""

    @classmethod
    def from_composite(cls, value: str) -> "ProjectIdORM":
        """Create ORM instance from composite value."""
        return cls(value)

    def __composite_values__(self) -> tuple[str]:
        """Return composite values for SQLAlchemy."""
        return (self.value,)


class RepositoryIdORM(vo.RepositoryId):
    """ORM representation of RepositoryId value object."""

    @classmethod
    def from_composite(cls, value: str) -> "RepositoryIdORM":
        """Create ORM instance from composite value."""
        return cls(value)

    def __composite_values__(self) -> tuple[str]:
        """Return composite values for SQLAlchemy."""
        return (self.value,)


class ProviderORM(vo.Provider):
    """ORM representation of Provider value object."""

    @classmethod
    def from_composite(cls, value: str) -> "ProviderORM":
        """Create ORM instance from composite value."""
        provider_type = vo.ProviderType(value)
        return cls(provider_type)

    def __composite_values__(self) -> tuple[str]:
        """Return composite values for SQLAlchemy."""
        return (str(self.value),)


class PoliciesORM(vo.Policies):
    """ORM representation of Policies value object."""

    @classmethod
    def from_composite(
        cls, pull_request_policy: str, retry_limit_type: str, retry_limit_value: int
    ) -> "PoliciesORM":
        """Create ORM instance from composite values."""
        pr_policy = vo.PullRequestPolicy(pull_request_policy)
        retry_type = vo.RetryLimitType(retry_limit_type)
        return cls(
            pull_request_policy=pr_policy,
            retry_limit_type=retry_type,
            retry_limit_value=retry_limit_value,
        )

    def __composite_values__(self) -> tuple[str, str, int]:
        """Return composite values for SQLAlchemy."""
        return (
            self.pull_request_policy.value,
            self.retry_limit_type.value,
            self.retry_limit_value,
        )


class OwnerORM(vo.Owner):
    """ORM representation of Owner value object."""

    @classmethod
    def from_composite(cls, value: str) -> "OwnerORM":
        """Create ORM instance from composite value."""
        return cls(value)

    def __composite_values__(self) -> tuple[str]:
        """Return composite values for SQLAlchemy."""
        return (self.value,)


class RulesORM(vo.Rules):
    """ORM representation of Rules value object."""

    @classmethod
    def from_composite(cls, rules_text: str) -> "RulesORM":
        """Create ORM instance from composite value."""
        if not rules_text.strip():
            return cls()
        rules_list = [rule.strip() for rule in rules_text.split("\n") if rule.strip()]
        return cls(rules_list)

    def __composite_values__(self) -> tuple[str]:
        """Return composite values for SQLAlchemy."""
        return (self.to_text(),)


class URLORM(vo.URL):
    """ORM representation of URL value object."""

    @classmethod
    def from_composite(cls, value: str) -> "URLORM":
        """Create ORM instance from composite value."""
        return cls(value)

    def __composite_values__(self) -> tuple[str]:
        """Return composite values for SQLAlchemy."""
        return (self.value,)


class ProjectModel(Base):
    """SQLAlchemy model for Project aggregate."""

    __tablename__ = "projects"

    # Private primitive fields with proper typing
    _project_id_value: Mapped[str] = mapped_column(
        "project_id", String(255), primary_key=True
    )
    _repo_id_value: Mapped[str] = mapped_column("repo_id", String(255), nullable=False)
    _provider_value: Mapped[str] = mapped_column("provider", String(50), nullable=False)
    _pull_request_policy: Mapped[str] = mapped_column(
        "pull_request_policy", String(50), nullable=False
    )
    _retry_limit_type: Mapped[str] = mapped_column(
        "retry_limit_type", String(50), nullable=False
    )
    _retry_limit_value: Mapped[int] = mapped_column(
        "retry_limit_value", Integer, nullable=False
    )
    _owner_value: Mapped[str] = mapped_column("owner", String(255), nullable=False)
    _url_value: Mapped[str] = mapped_column("url", String(500), nullable=False)
    _rules_text: Mapped[str] = mapped_column(
        "rules_text", Text, nullable=False, default=""
    )
    created_at: Mapped[datetime] = mapped_column("created_at", DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column("updated_at", DateTime, nullable=False)

    # Public composite fields
    project_id: Mapped[vo.ProjectId] = composite(
        ProjectIdORM,
        _project_id_value,
    )

    repo_id: Mapped[vo.RepositoryId] = composite(
        RepositoryIdORM,
        _repo_id_value,
    )

    provider: Mapped[vo.Provider] = composite(
        ProviderORM,
        _provider_value,
    )

    policies: Mapped[vo.Policies] = composite(
        PoliciesORM,
        _pull_request_policy,
        _retry_limit_type,
        _retry_limit_value,
    )

    owner: Mapped[vo.Owner] = composite(
        OwnerORM,
        _owner_value,
    )

    rules: Mapped[vo.Rules] = composite(
        RulesORM,
        _rules_text,
    )

    url: Mapped[vo.URL] = composite(
        URLORM,
        _url_value,
    )
