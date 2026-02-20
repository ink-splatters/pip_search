from typing import Final

try:
    from ._version import __version__ as __version__
except ImportError:
    __version__: Final[str] = "dev"
