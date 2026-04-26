import os
import ujson
from datetime import datetime
from aiogram.fsm.context import FSMContext


class ActionLogger:
    LOG_PATH = os.path.join("log", "log.json")

    @classmethod
    def _load_log(cls) -> dict:
        if not os.path.exists(cls.LOG_PATH):
            os.makedirs(os.path.dirname(cls.LOG_PATH), exist_ok=True)
            return {}
        with open(cls.LOG_PATH, "r", encoding="utf-8") as f:
            return ujson.load(f)

    @classmethod
    def _save_log(cls, data: dict):
        with open(cls.LOG_PATH, "w", encoding="utf-8") as f:
            ujson.dump(data, f, ensure_ascii=False, indent=4)

    @classmethod
    async def log_action(
            cls,
            user_id: int,
            state: FSMContext,
            action: str,
            result: str = ""
    ):
        log_data = cls._load_log()
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        current_state = await state.get_state()
        log_entry = {
            "state": current_state,
            "action": action,
            "result": result
        }

        user_logs = log_data.get(str(user_id), {})
        user_logs[now] = log_entry
        log_data[str(user_id)] = user_logs

        cls._save_log(log_data)

    @classmethod
    def log_system_event(cls, action: str, result: str = ""):
        log_data = cls._load_log()
        now = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        log_entry = {
            "state": "SYSTEM",
            "action": action,
            "result": result
        }

        user_logs = log_data.get("0", {})
        user_logs[now] = log_entry
        log_data["0"] = user_logs

        cls._save_log(log_data)
