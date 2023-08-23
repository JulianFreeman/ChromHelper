# coding: utf8
from pathlib import Path
from typing import TypedDict


class ErrMsg(TypedDict):
    err: bool
    msg: str


class PrfInfo(TypedDict):
    name: str
    path: Path

    pref_path: Path
    s_pref_path: Path

    bookmarks_path: Path
    bookmarks_bak_path: Path

    ext_cookies_path: Path
    extensions_path_d: Path
    local_ext_settings_path_d: Path

    web_data_path: Path
    affiliation_path: Path


class ExtInfo(TypedDict):
    name: str
    icon: str
    safe: bool
    note: str
    profiles: dict[str, str]  # id: name


class SgExtInfo(TypedDict):
    id: str
    name: str
    icon: str


class BmxInfo(TypedDict):
    name: str
    profiles: dict[str, tuple[str, str]]  # id: (name, position)


PrfDB = dict[str, PrfInfo]
ExtDB = dict[str, ExtInfo]  # ext_id: info
AllExtDB = dict[str, list[SgExtInfo]]  # profile_id: [info, ...]
BmxDB = dict[str, BmxInfo]  # url: info
