import os
import sys
from pathlib import Path
from typing import Union, cast

from pydantic import ValidationError
from pydantic_settings import BaseSettings

path_default = Path("/var/data")
def get_user_config_dir(app_name: str) -> Path:
    if sys.platform.startswith("win"):
        # En Windows se usa APPDATA → Roaming
        return Path(cast(str, os.getenv("APPDATA"))) / app_name
    elif sys.platform == "darwin":
        # En macOS
        return Path.home() / "Library" / "Application Support" / app_name
    else:
        # En Linux / Unix
        return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / app_name


class Credentials(BaseSettings):
    username: str
    password: str

    working_dir: Path = path_default
    lab_cookies_path:Path= path_default
    vocareum_cookies_path: Path= path_default

    def model_post_init(self, __context):
        if self.working_dir== path_default:
            self.working_dir= get_user_config_dir("labcontrol")
            self.working_dir.mkdir(parents=True, exist_ok=True)

        if self.lab_cookies_path == path_default:
            self.lab_cookies_path = self.working_dir / "lab_cookies.txt"
        
        if self.vocareum_cookies_path == path_default:
            self.vocareum_cookies_path = self.working_dir / "vocareum_cookies.txt"

def get_settings(env_path: Union[Path, str] = ".env") -> Credentials:
    env_path = Path(env_path) if isinstance(env_path, str) else env_path
    try:
        if env_path.exists():
            settings = Credentials(_env_file=env_path)  # type: ignore
            return settings
        raise FileNotFoundError(f"El archivo de configuración {env_path} no existe.")
    except ValidationError as e:
        print("❌ Error en configuración:", e)
        raise