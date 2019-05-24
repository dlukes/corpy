"""Shared utilities for the subpackage.

"""
from functools import wraps

from . import LOG


def generator_with_shared_state(gen_func):
    """Decorator for instance methods creating generators with shared state.

    When an instance method creates generators which rely on shared mutable
    resources stored as attributes on the instance, creating a new generator
    invalidates the state of those resources with respect to previously created
    generators.

    This decorator ensures that there is only one active generator created by
    the wrapped method at a time. If the method is used to create a new
    generator before the previous one is exhausted, a warning will be logged and
    the previous one will be terminated early.

    A (stupid) use case for this decorator is demonstrated in the tests, in
    test_morphodita.py. Actual use cases are in the tagger.py and tokenizer.py
    modules.

    """

    @wraps(gen_func)
    def wrapper(self, *args, **kwargs):
        if getattr(self, "_current_generator", None) is not None:
            class_ = self.__class__.__name__
            current_generator = self._current_generator
            LOG.warning(
                f"{self} was given a new text to process before having yielded "
                f"all the tokens in the previous one. The {current_generator} "
                "created for the previous text is now therefore invalid and "
                "will not yield any more tokens. If you want to process "
                f"multiple texts in parallel, please create multiple {class_} "
                "objects."
            )
        this_generator = gen_func(self, *args, **kwargs)
        self._current_generator = this_generator
        try:
            while this_generator is self._current_generator:
                yield next(this_generator)
            LOG.debug(f"{this_generator} for {self} was invalidated before exhaustion.")
        except StopIteration:
            LOG.debug(f"{this_generator} for {self} was fully exhausted.")
            self._current_generator = None

    return wrapper
