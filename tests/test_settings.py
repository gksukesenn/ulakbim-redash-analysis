import pytest

from ulakbim_analysis.infrastructure.settings import MongoDBSettings


def test_settings_loads_values_from_environment_mapping() -> None:
    settings = MongoDBSettings.from_env(
        {
            "MONGODB_URI": "mongodb://example:27017",
            "MONGODB_DATABASE": "database",
            "MONGODB_COLLECTION": "collection",
            "MONGODB_CONNECT_TIMEOUT_MS": "2500",
        }
    )

    assert settings.uri == "mongodb://example:27017"
    assert settings.database == "database"
    assert settings.collection == "collection"
    assert settings.connect_timeout_ms == 2500


def test_settings_requires_uri() -> None:
    with pytest.raises(ValueError, match="MONGODB_URI"):
        MongoDBSettings.from_env({})


@pytest.mark.parametrize("timeout", ["zero", "0", "-1"])
def test_settings_rejects_invalid_timeout(timeout: str) -> None:
    with pytest.raises(ValueError):
        MongoDBSettings.from_env(
            {
                "MONGODB_URI": "mongodb://localhost:27017",
                "MONGODB_CONNECT_TIMEOUT_MS": timeout,
            }
        )
