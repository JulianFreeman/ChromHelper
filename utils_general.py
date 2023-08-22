# coding: utf8
import os
import sys
from pathlib import Path

from typedict_def import ErrMsg


def get_errmsg(errmsg: ErrMsg = None) -> ErrMsg:
    if errmsg is None:
        errmsg = ErrMsg(err=True, msg="")
    else:
        # 重置上一次的残留信息
        errmsg["err"] = True
        errmsg["msg"] = ""

    return errmsg


def get_with_chained_keys(dic: dict, keys: list):
    k = keys[0]
    if k not in dic:
        return None
    if len(keys) == 1:
        return dic[k]
    return get_with_chained_keys(dic[k], keys[1:])


def sort_profiles_id_func(profile_id: str) -> int:
    if profile_id == "Default":
        return 0
    else:
        seq = profile_id.split(" ", 1)[-1]
        try:
            return int(seq)
        except ValueError:
            # if the id is weird
            return 999


def path_not_exist(path: str | Path) -> bool:
    if isinstance(path, str):
        return len(path) == 0 or not Path(path).exists()
    elif isinstance(path, Path):
        return not path.exists()
    else:
        return True


def get_log_dir(org_name: str, app_name: str, *, errmsg: ErrMsg = None) -> Path | None:
    errmsg = get_errmsg(errmsg)

    match sys.platform:
        case "win32":
            log_dir = os.path.expandvars("%appdata%")
        case "darwin":
            log_dir = os.path.expanduser("~") + "/Library/Application Support"
        case _:
            errmsg["msg"] = "不支持的操作系统"
            return None
    if path_not_exist(log_dir):
        errmsg["msg"] = f"未找到日志路径 {log_dir}"
        return None

    app_log_dir = Path(log_dir, org_name, app_name)
    if path_not_exist(app_log_dir):
        app_log_dir.mkdir(parents=True, exist_ok=True)

    errmsg["err"] = False
    return app_log_dir


def args_match(args: tuple, count: int, a_types: tuple) -> bool:
    if len(args) != count:
        return False

    for ori, exp in zip(args, a_types):
        if not isinstance(ori, exp):
            return False

    return True
