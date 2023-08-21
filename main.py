# coding: utf8
import logging
from pathlib import Path
from datetime import datetime

from config import version, ORG_NAME, APP_NAME
from utils_general import get_log_dir, get_errmsg

from mw_chrom_helper import launch


def init_logging() -> tuple[bool, str]:
    errmsg = get_errmsg()
    app_log_dir = get_log_dir(ORG_NAME, APP_NAME, errmsg=errmsg)
    if errmsg["err"]:
        return False, errmsg["msg"]

    now_s = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ver_s = f"v{version[0]}.{version[1]}.{version[2]}"
    log_file = Path(app_log_dir, f"{APP_NAME}_{ver_s}_{now_s}.log")

    logging.basicConfig(filename=log_file, encoding="utf8", level=logging.INFO,
                        format="[%(asctime)s][%(funcName)s][%(levelname)s] %(message)s")
    return True, ""


def main():
    has_log, log_err = init_logging()
    launch(ORG_NAME, APP_NAME, has_log, log_err, version)


if __name__ == '__main__':
    main()
