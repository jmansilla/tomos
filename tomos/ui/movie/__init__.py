from tomos.buttons_and_dials import ButtonsAndDialsSet
from pathlib import Path

here = Path(__file__).parent.resolve()
configs = ButtonsAndDialsSet('tomos', here/'tomos.toml', check_cwd=False, argv_prefix='--cfg')
