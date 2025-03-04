from buttons_and_dials import ConfigSet
from pathlib import Path

here = Path(__file__).parent.resolve()
configs = ConfigSet("tomos_ui", here / "tomos_ui.toml", check_cwd=True, argv_prefix="--cfg")
