import sys
import inspect
from contextlib import contextmanager

from IPython.core.magic import Magics, magics_class, line_cell_magic

from .util import clean_env


# TODO: unit-test this, to ensure magic options are properly mapped to kwargs
# (it's basically the only complicated logic here, everything else is in
# util.py; other than this, just test whether the magic actually works in both
# strict and non-strict modes)
def _clean_env_opts2kwargs(opts):
    opt2kwarg = dict(
        b="blacklist",
        w="whitelist",
        r="restore_builtins",
        a="strict",
        m="modules",
        c="callables",
        u="upper",
        d="dunder",
        s="sunder",
    )
    kwargs = {k: v.default for k, v in inspect.signature(clean_env).parameters.items()}
    for opt, val in opts.items():
        kwarg = opt2kwarg[opt.lower()]
        if kwarg.endswith("list"):
            kwargs[kwarg] = val
        else:
            kwargs[kwarg] = opt.islower()
    return kwargs


@contextmanager
def _tracing_managed_via_ipython_events(ip, global_trace):
    # yield
    settrace = lambda: sys.settrace(global_trace)
    unsettrace = lambda: sys.settrace(None)
    ip.events.register("pre_execute", settrace)
    ip.events.register("post_execute", unsettrace)
    yield
    ip.events.unregister("pre_execute", settrace)
    ip.events.unregister("post_execute", unsettrace)


@magics_class
class CorpyMagics(Magics):
    @line_cell_magic
    def clean_env(self, line, cell=None):
        """TODO

        Take inspiration from
        https://github.com/ipython/ipython/blob/6a7c488093026577db0d5c5f21d2aea129e5b6c9/IPython/core/magics/execution.py#L184

        Mnemonics for toggle options: lowercase letters toggle on, uppercase
        toggle off. You can think of `-a` for `strict` as standing for "(prune)
        all".

        """
        opts, code = self.parse_options(
            line, "b:w:rRaAmMcCuUdDsS", list_all=True, posix=False
        )
        kwargs = _clean_env_opts2kwargs(opts)
        kwargs["env"] = self.shell.user_ns
        # the comment on the first line is there mostly to make line numbers
        # match between the code the user wrote and the code that runs
        code = f"{code}  # Running code in a sanitized environment...".strip()
        if cell is not None:
            code += "\n" + cell

        # kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        # code = f"with clean_env({kwargs}):\n" + textwrap.indent(code, " ")
        # self.shell.run_cell("from corpy.util import clean_env")

        # TODO: the non-strict version is currently broken in IPython (it nukes
        # global scopes it shouldn't) -> figure out why
        with clean_env(**kwargs) as global_trace:
            if global_trace is None:
                return self.shell.run_cell(code).result
            else:
                with _tracing_managed_via_ipython_events(self.shell, global_trace):
                    return self.shell.run_cell(code).result
