# coding: utf8
import os
import sys
import json
import shutil
import logging
from pathlib import Path
# from typing import Literal

from typedict_def import (
    ErrMsg,
    PrfInfo, ExtInfo, SgExtInfo, BmxInfo,
    PrfDB, ExtDB, AllExtDB, BmxDB,
)
from utils_general import (
    get_with_chained_keys,
    path_not_exist,
    get_errmsg,
)
from config import QtCore


PLAT = sys.platform
USER_PATH = os.path.expanduser("~")
DATA_PATH_MAP = {
    "win32": {
        "Chrome": Path(USER_PATH, "AppData", "Local", "Google", "Chrome", "User Data"),
        "Edge": Path(USER_PATH, "AppData", "Local", "Microsoft", "Edge", "User Data"),
        "Brave": Path(USER_PATH, "AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data"),
    },
    "darwin": {
        "Chrome": Path(USER_PATH, "Library", "Application Support", "Google", "Chrome"),
        "Edge": Path(USER_PATH, "Library", "Application Support", "Microsoft Edge"),
        "Brave": Path(USER_PATH, "Library", "Application Support", "BraveSoftware", "Brave-Browser"),
    },
}
EXEC_PATH_MAP = {
    "win32": {
        "Chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "Edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "Brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    },
    "darwin": {
        "Chrome": r"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "Edge": r"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "Brave": r"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    },
}

# EXT_SET_FILE_MARK = None  # type: Literal["pref_path", "s_pref_path"] | None


def get_exec_path(browser: str, *, errmsg: ErrMsg = None) -> str | None:
    errmsg = get_errmsg(errmsg)

    us = QtCore.QSettings()
    exec_path = us.value(f"{browser.lower()}_exec", "")  # type: str
    if not path_not_exist(exec_path):
        errmsg["err"] = False
        return exec_path

    exec_path = get_with_chained_keys(EXEC_PATH_MAP, [PLAT, browser])  # type: str | None
    if path_not_exist(exec_path):
        errmsg["msg"] = f"未找到 {browser} 浏览器的默认执行路径"
        return None

    errmsg["err"] = False
    return exec_path


def get_data_path(browser: str, *, errmsg: ErrMsg = None) -> Path | None:
    errmsg = get_errmsg(errmsg)

    us = QtCore.QSettings()
    data_path = us.value(f"{browser.lower()}_data", "")  # type: str
    if not path_not_exist(data_path):
        errmsg["err"] = False
        return Path(data_path)

    data_path = get_with_chained_keys(DATA_PATH_MAP, [PLAT, browser])  # type: Path | None
    if path_not_exist(data_path):
        errmsg["msg"] = f"未找到 {browser} 浏览器的默认用户数据路径"
        return None

    errmsg["err"] = False
    return data_path


def get_profiles_db(user_data_path: Path, *, errmsg: ErrMsg = None) -> PrfDB:
    errmsg = get_errmsg(errmsg)

    local_state_file_path = Path(user_data_path, "Local State")
    if path_not_exist(local_state_file_path):
        errmsg["msg"] = "没有找到 Local State 文件"
        return {}

    local_state_data = json.loads(local_state_file_path.read_text("utf8"))  # type: dict
    profiles_info = get_with_chained_keys(local_state_data, ["profile", "info_cache"])   # type: dict
    if profiles_info is None:
        errmsg["msg"] = "在 Local State 中没有找到 profile>info_cache"
        return {}

    profiles_db = {}  # type: PrfDB
    for profile_id in profiles_info:
        name = profiles_info[profile_id].get("name", "")  # type: str
        path = Path(user_data_path, profile_id)
        pref_path = Path(path, "Preferences")
        s_pref_path = Path(path, "Secure Preferences")
        web_data_path = Path(path, "Web Data")
        bookmarks_path = Path(path, "Bookmarks")
        ext_cookies_path = Path(path, "Extension Cookies")
        affiliation_path = Path(path, "Affiliation Database")
        extensions_path_d = Path(path, "Extensions")
        bookmarks_bak_path = Path(path, "Bookmarks.bak")
        local_ext_settings_path_d = Path(path, "Local Extension Settings")
        cache_data_path_d = Path(path, "Cache", "Cache_Data")

        prf_info = PrfInfo(
            name=name,
            path=path,

            pref_path=pref_path,
            s_pref_path=s_pref_path,

            bookmarks_path=bookmarks_path,
            bookmarks_bak_path=bookmarks_bak_path,

            ext_cookies_path=ext_cookies_path,
            extensions_path_d=extensions_path_d,
            local_ext_settings_path_d=local_ext_settings_path_d,

            web_data_path=web_data_path,
            affiliation_path=affiliation_path,

            cache_data_path_d=cache_data_path_d,
        )
        profiles_db[profile_id] = prf_info

    errmsg["err"] = False
    return profiles_db


# def get_extension_settings_data(profile_info: PrfInfo, *, errmsg: ErrMsg = None) -> dict:
#     global EXT_SET_FILE_MARK
#     errmsg = get_errmsg(errmsg)
#
#     if EXT_SET_FILE_MARK is not None:
#         e_pref_path = profile_info[EXT_SET_FILE_MARK]
#         e_pref_data = json.loads(e_pref_path.read_text("utf8"))  # type: dict
#         ext_set_data = get_with_chained_keys(e_pref_data, ["extensions", "settings"])  # type: dict
#         if ext_set_data is not None:
#             errmsg["err"] = True
#             return ext_set_data
#
#     profile_path = profile_info["path"]
#
#     s_pref_path = profile_info["s_pref_path"]
#     if not path_not_exist(s_pref_path):
#         s_pref_data = json.loads(s_pref_path.read_text("utf8"))  # type: dict
#         ext_set_data = get_with_chained_keys(s_pref_data, ["extensions", "settings"])  # type: dict
#         if ext_set_data is not None:
#             EXT_SET_FILE_MARK = "s_pref_path"
#             errmsg["err"] = True
#             return ext_set_data
#
#     pref_path = profile_info["pref_path"]
#     if path_not_exist(pref_path):
#         errmsg["msg"] = f"在 {profile_path} 中找不到 Secure Preferences 和 Preferences"
#         return {}
#     pref_data = json.loads(pref_path.read_text("utf8"))  # type: dict
#     ext_set_data = get_with_chained_keys(pref_data, ["extensions", "settings"])  # type: dict
#     if ext_set_data is None:
#         errmsg["msg"] = f"在 {profile_path} 的 Preferences 中找不到 extensions>settings"
#         return {}
#
#     EXT_SET_FILE_MARK = "pref_path"
#     errmsg["err"] = True
#     return ext_set_data


def _get_largest_icon_path(icons: dict[str, str], prefix_path: str | Path) -> str:
    if len(icons) == 0:
        return ""

    if "128" in icons:
        icon_path = icons["128"]
    else:
        icon_path = icons[str(max(map(int, icons.keys())))]  # type: str

    # 以 / 为开头会导致前面的路径被忽略
    if icon_path.startswith("/"):
        icon_path = icon_path[1:]
    icon_p = Path(prefix_path, icon_path)
    if icon_p.exists():
        return str(icon_p)

    return ""


def _read_plg_db() -> dict[str, dict]:
    us = QtCore.QSettings()
    plg_db = us.value("plg_db", "")  # type: str
    if path_not_exist(plg_db):
        logging.info("未找到 [插件预存库文件]。")
        return {}

    try:
        with open(plg_db, "r", encoding="utf8") as f:
            data = json.load(f)
    except:
        logging.warning("无法打开 [插件预存库文件]。")
        return {}
    else:
        return data


def get_extensions_db(profiles_db: PrfDB, for_all: bool, *, errmsg: ErrMsg = None) -> tuple[ExtDB, AllExtDB]:
    errmsg = get_errmsg(errmsg)
    if len(profiles_db) == 0:
        errmsg["msg"] = "profiles_db 为空"
        return {}, {}

    plg_db = _read_plg_db()

    extensions_db = {}  # type: ExtDB  # ext_id: info
    all_extensions_db = {}  # type: AllExtDB  # profile_id: [info, ...]
    for profile_id in profiles_db:
        prf_info = profiles_db[profile_id]
        profile_name = prf_info["name"]

        # 需要在这个位置，以保证 profiles_db 和 all_extensions_db 的键值对个数始终相同
        if profile_id not in all_extensions_db:
            all_extensions_db[profile_id] = []

        e_pref_path = prf_info["s_pref_path"]
        if path_not_exist(e_pref_path):
            logging.warning(f"找不到 {e_pref_path}")
            e_pref_path = prf_info["pref_path"]
            if path_not_exist(e_pref_path):
                logging.warning(f"找不到 {e_pref_path}")
                logging.warning(f"在 {e_pref_path.parent} 中无法找到插件信息")
                continue

        e_pref_data = json.loads(e_pref_path.read_text("utf8"))  # type: dict
        ext_set_data = get_with_chained_keys(e_pref_data, ["extensions", "settings"])
        if ext_set_data is None:
            logging.warning(f"在 {e_pref_path} 中找不到 extensions>settings")
            continue

        # 此处不判断是否存在，之后会有图标路径的判断
        extensions_path_d = prf_info["extensions_path_d"]

        for ext_id in ext_set_data:
            ext_data = ext_set_data[ext_id]  # type: dict

            path = ext_data.get("path", "")  # type: str
            if len(path) == 0:
                # 一些没啥信息的插件
                continue

            if path.startswith(ext_id):
                manifest = ext_data.get("manifest", {})
                name = manifest.get("name", "")
                icon = _get_largest_icon_path(manifest.get("icons", {}), Path(extensions_path_d, path))
            elif Path(path).exists():
                manifest_p = Path(path, "manifest.json")
                if path_not_exist(manifest_p):
                    name = ""
                    icon = ""
                else:
                    manifest_data = json.loads(manifest_p.read_text("utf8"))  # type: dict
                    name = manifest_data.get("name", "")
                    icon = _get_largest_icon_path(manifest_data.get("icons", {}), path)
            else:
                # 可能是不存在路径的一些内置插件
                continue

            if for_all:
                all_extensions_db[profile_id].append(SgExtInfo(id=ext_id, name=name, icon=icon))
            else:
                if ext_id in plg_db:
                    safe = plg_db[ext_id]["safe"]
                    note = plg_db[ext_id]["note"]
                else:
                    safe = None
                    note = ""
                if ext_id not in extensions_db:
                    extensions_db[ext_id] = ExtInfo(name=name, icon=icon, profiles={}, safe=safe, note=note)
                extensions_db[ext_id]["profiles"][profile_id] = profile_name

    errmsg["err"] = False
    return extensions_db, all_extensions_db


def _handle_bookmark(bmx_info: dict, bookmarks_db: BmxDB, profile_id: str, profile_name: str, position: list[str]):
    match bmx_info["type"]:
        case "url":
            url = bmx_info["url"]
            name = bmx_info["name"]
            if url not in bookmarks_db:
                bookmarks_db[url] = BmxInfo(name=name, profiles={})
            bookmarks_db[url]["profiles"][profile_id] = (profile_name, "/".join(position))
        case "folder":
            position = position.copy()
            position.append(bmx_info["name"])
            for child in bmx_info["children"]:
                _handle_bookmark(child, bookmarks_db, profile_id, profile_name, position)


def get_bookmarks_db(profiles_db: PrfDB, *, errmsg: ErrMsg = None) -> BmxDB:
    errmsg = get_errmsg(errmsg)
    if len(profiles_db) == 0:
        errmsg["msg"] = "profiles_db 为空"
        return {}

    bookmarks_db = {}  # type: BmxDB
    for profile_id in profiles_db:
        prf_info = profiles_db[profile_id]
        profile_name = prf_info["name"]
        bookmarks_path = prf_info["bookmarks_path"]

        if path_not_exist(bookmarks_path):
            logging.warning(f"找不到 {bookmarks_path}")
            continue

        bookmarks_data = json.loads(bookmarks_path.read_text("utf8"))  # type: dict
        bookmarks_roots = get_with_chained_keys(bookmarks_data, ["roots"])  # type: dict
        if bookmarks_roots is None:
            logging.warning(f"在 {bookmarks_path} 中找不到 roots")
            continue

        for bmx_pos in bookmarks_roots:
            _handle_bookmark(bookmarks_roots[bmx_pos], bookmarks_db, profile_id, profile_name, [""])

    errmsg["err"] = False
    return bookmarks_db


def delete_extensions(profile_info: PrfInfo, ext_ids: list[str]) -> tuple[int, int]:
    total = len(ext_ids)

    e_pref_path = profile_info["s_pref_path"]
    if path_not_exist(e_pref_path):
        logging.error(f"找不到 {e_pref_path}")
        e_pref_path = profile_info["pref_path"]
        if path_not_exist(e_pref_path):
            logging.error(f"找不到 {e_pref_path}")
            logging.error(f"在 {e_pref_path.parent} 中无法找到插件信息")
            return 0, total
    e_pref_data = json.loads(e_pref_path.read_text("utf8"))  # type: dict
    ext_set_data = get_with_chained_keys(e_pref_data, ["extensions", "settings"])  # type: dict
    if ext_set_data is None:
        logging.error(f"在 {e_pref_path} 中找不到 extensions>settings")
        return 0, total

    s_pref_path = profile_info["s_pref_path"]
    pref_path = profile_info["pref_path"]
    if s_pref_path == e_pref_path:
        s_pref_data = e_pref_data
        pref_data = json.loads(pref_path.read_text("utf8"))  # type: dict
    elif pref_path == e_pref_path:
        pref_data = e_pref_data
        s_pref_data = json.loads(s_pref_path.read_text("utf8"))  # type: dict
    else:
        logging.critical("不可能的错误")
        return 0, total

    macs = get_with_chained_keys(s_pref_data, ["protection", "macs", "extensions", "settings"])  # type: dict
    if macs is None:
        logging.error(f"在 {s_pref_path} 中找不到 protection>macs>extensions>settings")
        return 0, total

    success = 0
    for ids in ext_ids:
        c1 = ext_set_data.pop(ids, None)
        c2 = macs.pop(ids, None)
        if None not in (c1, c2):
            success += 1
        else:
            logging.warning(f"在 {e_pref_path} 中移除 {ids} 失败")

    pinned_ext = get_with_chained_keys(pref_data, ["extensions", "pinned_extensions"])  # type: list
    if pinned_ext is None:
        logging.warning(f"在 {pref_path} 中未找到 extensions>pinned_extensions")
    else:
        for ids in ext_ids:
            if ids in pinned_ext:
                pinned_ext.remove(ids)

    s_pref_path.write_text(json.dumps(s_pref_data, ensure_ascii=False), "utf8")
    pref_path.write_text(json.dumps(pref_data, ensure_ascii=False), "utf8")

    extensions_path_d = profile_info["extensions_path_d"]
    for ids in ext_ids:
        # 对于离线安装的插件，目录可能不在这个位置，所以就不删了
        ext_folder_path = Path(extensions_path_d, ids)
        if ext_folder_path.exists():
            shutil.rmtree(ext_folder_path, ignore_errors=True)

    return success, total


def delete_bookmarks(profile_info: PrfInfo, urls: list[str]) -> tuple[int, int]:
    total = len(urls)

    bookmarks_path = profile_info["bookmarks_path"]
    bookmarks_bak_path = profile_info["bookmarks_bak_path"]
    if not path_not_exist(bookmarks_bak_path):
        os.remove(bookmarks_bak_path)
    if path_not_exist(bookmarks_path):
        logging.error(f"未找到 {bookmarks_path}")
        return 0, total

    bookmarks_data = json.loads(bookmarks_path.read_text("utf8"))  # type: dict
    if "checksum" in bookmarks_data:
        bookmarks_data.pop("checksum")

    success = 0

    def search_and_delete(data: dict, parent: list) -> bool:
        nonlocal success

        match data["type"]:
            case "url":
                if data["url"] in urls:
                    parent.remove(data)
                    return True
                else:
                    return False
            case "folder":
                children = data["children"]
                i = 0
                while i < len(children):
                    is_deleted = search_and_delete(children[i], children)
                    if not is_deleted:
                        i += 1
                    else:
                        success += 1
            case _:
                return False

    root = bookmarks_data["roots"]
    for f in root:
        search_and_delete(root[f], [])

    bookmarks_path.write_text(json.dumps(bookmarks_data, ensure_ascii=False), "utf8")

    return success, total
