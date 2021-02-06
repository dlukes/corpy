import inspect
import textwrap
from typing import Any, Optional, Dict

from IPython.core.magic import Magics, magics_class, line_cell_magic

from .util import clean_env


# TODO: unit-test this, to ensure magic options are properly mapped to kwargs?
def _clean_env_opts2kwargs(opts: Dict[str, Any]) -> Dict[str, Any]:
    opt2kwarg = dict(
        b="blacklist",
        w="whitelist",
        r="restore_builtins",
        x="strict",
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


@magics_class
class CorpyMagics(Magics):
    @line_cell_magic
    def clean_env(self, line: str, cell: Optional[str] = None) -> Any:
        """Run a block of code in a sanitized global environment.

        Usage, in line mode:
          %clean_env [options] statement

        Usage, in cell mode:
          %%clean_env [options] [statement]
          code...
          code...

        In cell mode, the block to run is constructed by appending the
        additional code lines to the (possibly empty) statement on the first
        line.

        The original global environment is restored afterwards.

        Options:

        For boolean options, lowercase letters toggle the option on, uppercase
        letters toggle it off.

        -b <varname>
          Blacklist this variable, i.e. *always* remove it from the environment
          prior to execution, irrespective of the other options. Repeat this
          option with different arguments to blacklist multiple variables.

        -w <varname>
          Whitelist this variable, i.e. *never* remove it from the environment
          prior to execution, irrespective of the other options. Repeat this
          option with different arguments to whitelist multiple variables.

        -x to toggle on, -X to toggle off (default: on)
          Strict mode. In non-strict mode, allow global variables in the current
          scope, i.e. only start pruning within function calls. NOTE: This is
          slower because it requires tracing the function calls.

        -r to toggle on, -R to toggle off (default: on)
          Restore builtins, i.e. make sure that the conventional names for
          built-in objects point to those objects (beginners often use ``list``
          or ``sorted`` as variable names).

        -m to toggle on, -M to toggle off (default: off)
          Prune variables which refer to modules.

        -c to toggle on, -C to toggle off (default: off)
          Prune variables which refer to callables.

        -u to toggle on, -U to toggle off (default: off)
          Prune variables with all-uppercase identifiers (underscores allowed),
          which are likely to be intentional global variables (constants and the
          like).

        -d to toggle on, -D to toggle off (default: off)
          Prune variables whose name starts with a double underscore.

        -s to toggle on, -S to toggle off (default: on)
          Prune variables whose name starts with a single underscore.

        See also:

          from corpy.util import clean_env
          clean_env?

        """
        opts, code = self.parse_options(
            line, "b:w:xXrRmMcCuUdDsS", list_all=True, posix=False
        )
        kwargs = _clean_env_opts2kwargs(opts)
        kwargs = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        assert isinstance(code, str)
        if code.strip() and cell is not None:
            code += "\n" + cell
        elif cell is not None:
            code = cell
        code = f"with clean_env({kwargs}):\n" + textwrap.indent(code, " ")
        self.shell.run_cell("from corpy.util import clean_env")
        return self.shell.run_cell(code).result
