import pytest

from domain.project.value_objects import Provider, ProviderType


class TestProviderType:
    """Test cases for ProviderType enum."""

    def test_provider_type_values(self) -> None:
        """Test that ProviderType has expected values."""
        assert ProviderType.GITHUB == "github"
        assert ProviderType.GITLAB == "gitlab"
        assert ProviderType.BITBUCKET == "bitbucket"

    def test_provider_type_membership(self) -> None:
        """Test membership checks for ProviderType."""
        assert "github" in ProviderType
        assert "gitlab" in ProviderType
        assert "bitbucket" in ProviderType
        assert "unknown" not in ProviderType

    @pytest.mark.parametrize(
        "provider_value",
        [
            ProviderType.GITHUB,
            ProviderType.GITLAB,
            ProviderType.BITBUCKET,
        ],
    )
    def test_provider_type_iteration(self, provider_value: ProviderType) -> None:
        """Test that all ProviderType values are accessible."""
        assert provider_value in ProviderType
        assert isinstance(provider_value.value, str)


class TestProvider:
    """Test cases for Provider value object."""

    @pytest.mark.parametrize(
        "provider_type",
        [
            ProviderType.GITHUB,
            ProviderType.GITLAB,
            ProviderType.BITBUCKET,
        ],
    )
    def test_valid_provider_creation(self, provider_type: ProviderType) -> None:
        """Test creating Provider with valid ProviderType values."""
        provider = Provider(provider_type)
        assert provider.value == provider_type
        assert str(provider) == provider_type.value

    def test_provider_immutability(self) -> None:
        """Test that Provider is immutable (frozen dataclass)."""
        provider = Provider(ProviderType.GITHUB)
        with pytest.raises(AttributeError):
            provider.value = ProviderType.GITLAB  # type: ignore

    def test_provider_equality(self) -> None:
        """Test Provider equality comparison."""
        provider1 = Provider(ProviderType.GITHUB)
        provider2 = Provider(ProviderType.GITHUB)
        provider3 = Provider(ProviderType.GITLAB)

        assert provider1 == provider2
        assert provider1 != provider3
        assert hash(provider1) == hash(provider2)
        assert hash(provider1) != hash(provider3)

    @pytest.mark.parametrize(
        "provider_type, expected_str",
        [
            (ProviderType.GITHUB, "github"),
            (ProviderType.GITLAB, "gitlab"),
            (ProviderType.BITBUCKET, "bitbucket"),
        ],
    )
    def test_provider_str_representation(
        self, provider_type: ProviderType, expected_str: str
    ) -> None:
        """Test string representation of Provider."""
        provider = Provider(provider_type)
        assert str(provider) == expected_str

    def test_provider_validation(self) -> None:
        """Test Provider validation with valid ProviderType."""
        # This test verifies that validation passes for valid providers
        for provider_type in ProviderType:
            provider = Provider(provider_type)
            assert provider.value == provider_type

    def test_provider_type_as_string_enum(self) -> None:
        """Test that ProviderType works as string enum."""
        # Test that ProviderType values can be compared with strings
        assert ProviderType.GITHUB == "github"
        assert ProviderType.GITLAB.value == "gitlab"
        assert ProviderType.BITBUCKET.value == "bitbucket"
