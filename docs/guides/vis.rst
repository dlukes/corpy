===========================
Easily generate word clouds
===========================

The `wordcloud package <https://amueller.github.io/word_cloud/>`__ is great but
I find the API a bit ceremonious, especially for beginners. Hence this wrapper
to make using it easier.

.. code:: python

    >>> from corpy.vis import wordcloud
    >>> import os
    >>> wc = wordcloud(os.__doc__)
    >>> wc.to_image().show()

In a Jupyter notebook, just inspect the ``wc`` variable to display the
wordcloud.

For further details, see the docstring of the :func:`~corpy.vis.wordcloud`
function.
