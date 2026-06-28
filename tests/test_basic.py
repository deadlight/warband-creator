from django.conf import settings


def test_django_settings_configured():
    assert settings.configured is True


def test_true():
    assert True
