import pytest

from app.links.utils import generate_slug


@pytest.mark.unit
def test_generate_slug_length():
    slug = generate_slug()
    assert len(slug) == 6
    slug = generate_slug(20)
    assert len(slug) == 20


@pytest.mark.unit
def test_generate_slug_uniqness():
    slug1 = generate_slug()
    slug2 = generate_slug()
    assert slug1 != slug2


@pytest.mark.unit
def test_generate_slug_alnum():
    slug = generate_slug()
    assert slug.isalnum()
