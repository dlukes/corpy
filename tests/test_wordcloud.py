import pytest
import numpy as np

from corpy import vis


def test_size_in_pixels():
    assert vis.size_in_pixels(5, 6) == (1500, 1800)
    assert vis.size_in_pixels(5, 6, ppi=96) == (480, 576)
    assert vis.size_in_pixels(5, 6, unit="cm") == (3810, 4572)
    assert vis.size_in_pixels(4, 10, unit="cm", ppi=96) == (975, 2438)
    with pytest.raises(ValueError) as exc_info:
        vis.size_in_pixels(5, 5, unit="foo")
    assert exc_info.match(r"`unit` must be one of \('in', 'cm'\)\.")


def test_optimize_dimensions():
    # canvas gets shrunk for computation with scale factor for output
    # when fast == True...
    assert vis._optimize_dimensions((10000, 10000), True, 800) == (800, 800, 12.5)
    assert vis._optimize_dimensions((1000, 10000), True, 800) == (80, 800, 12.5)

    # ... but is kept untouched when fast == False...
    assert vis._optimize_dimensions((10000, 10000), False, 800) == (10000, 10000, 1)

    # ... or when the size is at or below fast_limit**2
    assert vis._optimize_dimensions((800, 800), True, 800) == (800, 800, 1)
    assert vis._optimize_dimensions((640, 1000), True, 800) == (640, 1000, 1)
    assert vis._optimize_dimensions((500, 500), True, 800) == (500, 500, 1)


def test_elliptical_mask():
    assert np.all(
        vis._elliptical_mask(5, 5)
        == np.array(
            [
                [255, 255, 255, 255, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 255, 255, 255, 255],
            ]
        )
    )
    assert np.all(
        vis._elliptical_mask(10, 5)
        == np.array(
            [
                [255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
                [255, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [255, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [255, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [255, 255, 255, 255, 255, 255, 255, 255, 255, 255],
            ]
        )
    )
    assert np.all(
        vis._elliptical_mask(5, 10)
        == np.array(
            [
                [255, 255, 255, 255, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
                [255, 0, 0, 0, 255],
            ]
        )
    )


def test_wordcloud():
    import os
    from collections import Counter

    # smaller than fast_limit**2
    im = vis.wordcloud(os.__doc__).to_image()
    assert (im.width, im.height) == (400, 400)
    im = vis.wordcloud(os.__doc__, (400, 800)).to_image()
    assert (im.width, im.height) == (400, 800)
    im = vis.wordcloud(os.__doc__, (800, 400)).to_image()
    assert (im.width, im.height) == (800, 400)

    # larger than fast_limit**2
    im = vis.wordcloud(os.__doc__, (813, 845)).to_image()
    assert (im.width, im.height) == (813, 844)
    im = vis.wordcloud(os.__doc__, (813, 845), fast=False).to_image()
    assert (im.width, im.height) == (813, 845)

    # smaller than custom fast_limit
    im = vis.wordcloud(os.__doc__, (813, 845), fast_limit=829).to_image()
    assert (im.width, im.height) == (813, 845)

    # different types of input
    assert vis.wordcloud(os.__doc__.split())
    assert vis.wordcloud(w for w in os.__doc__.split())
    assert vis.wordcloud(Counter(os.__doc__.split()))

    # using an elliptical mask doesn't affect output size
    im = vis.wordcloud(os.__doc__, (313, 345), rounded=True).to_image()
    assert (im.width, im.height) == (313, 345)

    # exceptions
    with pytest.raises(ValueError) as exc_info:
        vis.wordcloud(None)
    assert (
        str(exc_info.value)
        == "`data` must be a string, a mapping from words to frequencies, or an iterable of words."
    )
    with pytest.raises(ValueError) as exc_info:
        vis.wordcloud(os.__doc__, rounded=True, mask=1)
    assert str(exc_info.value) == "Can't specify `rounded` and `mask` at the same time."
