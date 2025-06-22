from rich_argparse import RichHelpFormatter, _lazy_rich as rr
from typing import ClassVar

class CustomRichHelpFormatter(RichHelpFormatter):
    """A custom RichHelpFormatter with modified styles."""

    def __init__(self, prog, epilog=None, width=None, max_help_position=24, indent_increment=2):
        super().__init__(prog)
        if epilog is not None:
            self.epilog = epilog
        if width is not None:
            self.width = width
        self._max_help_position = max_help_position
        self._indent_increment = indent_increment
        
    styles: ClassVar[dict[str, rr.StyleType]] = {
        "argparse.args": "bold #FFFF00",  # Changed from cyan
        "argparse.groups": "#AA55FF",   # Changed from dark_orange
        "argparse.help": "bold #00FFFF",    # Changed from default
        "argparse.metavar": "bold #FF00FF", # Changed from dark_cyan
        "argparse.syntax": "underline", # Changed from bold
        "argparse.text": "white",   # Changed from default
        "argparse.prog": "bold #00AAFF italic",     # Changed from grey50
        "argparse.default": "bold", # Changed from italic
    }
    
    def _fill_text(self, text, width, indent):
        # Pastikan baris baru tetap dipertahankan
        return ''.join([indent + line + '\n' for line in text.splitlines()])

