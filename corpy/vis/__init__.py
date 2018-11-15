from collections.abc import Mapping, Iterable

from wordcloud import WordCloud

CM_PER_IN = 2.54


def size_in_pixels(width, height, unit="in", ppi=300):
    """Convert size in inches/cm to pixels.

    width, height: dimensions, as measured by unit
    unit: "in" for inches, "cm" for centimeters
    ppi: pixels per inch

    Sample values for ppi:

    - for displays: you can detect your monitor's DPI using the
      following website:
      <https://www.infobyip.com/detectmonitordpi.php>; a typical
      value is 96 (of course, double that for HiDPI)
    - for print output: 300 at least, 600 is high quality

    """
    allowed_units = ("in", "cm")
    if unit not in allowed_units:
        raise ValueError(f"`unit` must be one of {allowed_units}.")
    if unit == "cm":
        width *= CM_PER_IN
        height *= CM_PER_IN
    return width * ppi, height * ppi


def wordcloud(data, size=(400, 400), *, fast=True, shape=None, **kwargs):
    """Generate a wordcloud.

    data: input data -- either one long string of text, or an
        iterable of tokens, or a mapping of word types to their
        frequencies; use the third option if you want full control
        over the input data
    size: size in pixels, as a tuple of integers, (width, height);
        if you want to specify the size in inches or cm, use the
        `size_in_pixels()` function to generate this tuple
    fast: when True, optimizes large wordclouds for speed of
        generation rather than precision of word placement
    kwargs: remaining keyword arguments are passed on to the
        `wordcloud.WordCloud` initializer

    """
    # TODO: implement shapes (circle, ellipse)
    if shape is not None:
        raise NotImplementedError("Specifying shapes has not been implemented yet.")
    width, height = size
    fast_limit = 800
    # NOTE: Reasonable numbers for width and height are in the hundreds
    # to low thousands of pixels. If the requested size is large, for
    # faster results, we shrink the canvas during wordcloud
    # computation, and only scale it back up during rendering.
    if fast and width * height > fast_limit ** 2:
        scale = max(size) / fast_limit
        width = round(width / scale)
        height = round(height / scale)
    else:
        scale = 1
    # tweak defaults
    kwargs.setdefault("background_color", "white")
    # if Jupyter gets better at rendering transparent images, then
    # maybe these would be better defaults:
    # kwargs.setdefault("mode", "RGBA")
    # kwargs.setdefault("background_color", None)

    wc = WordCloud(width=width, height=height, scale=scale, **kwargs)
    # raw text
    if isinstance(data, str):
        return wc.generate_from_text(data)
    # frequency counts
    elif isinstance(data, Mapping):
        return wc.generate_from_frequencies(data)
    # tokenized text
    # NOTE: the second condition is there because of nltk.text, which
    # behaves like an Iterable / Collection / Sequence for all
    # practical intents and purposes, but the corresponding abstract
    # base classes don't pick up on it (maybe because it only has a
    # __getitem__ magic method?)
    elif isinstance(data, Iterable) or hasattr(data, "__getitem__"):
        return wc.generate_from_text(" ".join(data))
    else:
        raise ValueError(
            "`data` must be a string, a mapping from words to frequencies, or an iterable of words."
        )


def _wordcloud_png(wc):
    from IPython.display import display

    return display(wc.to_image())


try:
    from IPython import get_ipython

    ip = get_ipython()
    if ip is not None:
        png_formatter = ip.display_formatter.formatters["image/png"]
        png_formatter.for_type(WordCloud, _wordcloud_png)
except ImportError:
    pass
