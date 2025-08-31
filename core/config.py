# --------------------------------------
# file: meeting_assistant/core/config.py
# --------------------------------------
from dataclasses import dataclass, asdict
import os
from pathlib import Path
from typing import Optional
from core.logger import logger

try:
    from dotenv import load_dotenv
    _HAS_DOTENV = True
except Exception:
    _HAS_DOTENV = False


ENV_KEYS = [
    "MYSQL_HOST", "MYSQL_USER", "MYSQL_PASSWORD", "MYSQL_DB",
    "BASE_DIR", "OPENAI_API_KEY", "GPT_MODEL", "ASR_MODEL", "AUTOSAVE_SEC"
]


@dataclass
class AppConfig:
    mysql_host: str = "localhost"
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "meeting_db"
    base_dir: str = "./records"
    openai_api_key: str = ""
    gpt_model: str = "gpt-4o-mini"
    asr_model: str = "medium"
    autosave_sec: int = 2

    @classmethod
    def from_env(cls) -> "AppConfig":
        if _HAS_DOTENV:
            # Tải .env nếu có
            load_dotenv(override=False)
        def _get(name, default):
            return os.getenv(name, default)

        cfg = cls(
            mysql_host=_get("MYSQL_HOST", "localhost"),
            mysql_user=_get("MYSQL_USER", "root"),
            mysql_password=_get("MYSQL_PASSWORD", ""),
            mysql_db=_get("MYSQL_DB", "meeting_db"),
            base_dir=_get("BASE_DIR", "./records"),
            openai_api_key=_get("OPENAI_API_KEY", ""),
            gpt_model=_get("GPT_MODEL", "gpt-4o-mini"),
            asr_model=_get("ASR_MODEL", "medium"),
            autosave_sec=int(_get("AUTOSAVE_SEC", "2") or 2),
        )
        return cfg


# Singleton cấu hình đang chạy
CONFIG: AppConfig = AppConfig.from_env()
logger.info(
    "Loaded CONFIG: host=%s db=%s base_dir=%s gpt_model=%s asr_model=%s autosave=%ss",
    CONFIG.mysql_host, CONFIG.mysql_db, CONFIG.base_dir, CONFIG.gpt_model, CONFIG.asr_model, CONFIG.autosave_sec
)


def _project_root() -> Path:
    # ../.. từ file này (core/ -> project root)
    return Path(__file__).resolve().parents[1]


def save_config(new_cfg: AppConfig, env_path: Optional[Path] = None) -> Path:
    """
    Ghi cấu hình vào file .env (ghi đè hoặc tạo mới).
    Trả về đường dẫn .env thực tế.
    """
    env_path = env_path or (_project_root() / ".env")
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"MYSQL_HOST={new_cfg.mysql_host}",
        f"MYSQL_USER={new_cfg.mysql_user}",
        f"MYSQL_PASSWORD={new_cfg.mysql_password}",
        f"MYSQL_DB={new_cfg.mysql_db}",
        f"BASE_DIR={new_cfg.base_dir}",
        f"OPENAI_API_KEY={new_cfg.openai_api_key}",
        f"GPT_MODEL={new_cfg.gpt_model}",
        f"ASR_MODEL={new_cfg.asr_model}",
        f"AUTOSAVE_SEC={new_cfg.autosave_sec}",
        "",
    ]
    env_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Saved .env to %s", env_path)
    return env_path


def set_config(new_cfg: AppConfig):
    """
    Cập nhật CONFIG đang chạy (in-memory).
    """
    global CONFIG
    CONFIG = new_cfg
    logger.info(
        "CONFIG updated: host=%s db=%s base_dir=%s gpt_model=%s asr_model=%s autosave=%ss",
        CONFIG.mysql_host, CONFIG.mysql_db, CONFIG.base_dir, CONFIG.gpt_model, CONFIG.asr_model, CONFIG.autosave_sec
    )


def config_as_dict() -> dict:
    return asdict(CONFIG)
