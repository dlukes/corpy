================
corpy.vis
================

Overview
========

Wrappers for quick visualizations of linguistic data.

.. code:: python

    >>> from corpy.vis import wordcloud
    >>> import os
    >>> wc = wordcloud(os.__doc__)
    >>> wc.to_image().show()

In Jupyter, just inspect the ``wc`` variable to display the
wordcloud.

For further details, see the docstring of the ``wordcloud()``
function.
