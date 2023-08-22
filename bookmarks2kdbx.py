# coding: utf8
from __future__ import annotations
from html import escape
from urllib.parse import urlparse

from typedict_def import BmxDB
from utils_general import args_match


class Entry(object):
    def __init__(self, title: str, url: str):
        self.title = title
        self.url = url

    def to_dict(self) -> dict:
        return {
            "Title": self.title,
            "URL": self.url
        }

    def to_xml(self) -> str:
        return f"""<Entry>
            <String>
                <Key>Title</Key>
                <Value>{self.title}</Value>
            </String>
            <String>
                <Key>URL</Key>
                <Value>{self.url}</Value>
            </String>
        </Entry>"""


class Group(object):
    def __init__(self, name: str):
        self.name = name
        self.entries = []
        self.groups = []

    def add_entry(self, *args) -> Entry:
        if args_match(args, 1, (Entry, )):
            e = args[0]
            self.entries.append(e)
        elif args_match(args, 2, (str, str)):
            title, url = args
            e = Entry(title, url)
            self.entries.append(e)
        else:
            raise TypeError
        return e

    def add_group(self, *args) -> Group:
        if args_match(args, 1, (Group, )):
            g = args[0]
            self.groups.append(g)
        elif args_match(args, 1, (str, )):
            name = args[0]
            g = Group(name)
            self.groups.append(g)
        else:
            raise TypeError
        return g

    def get_group(self, name: str) -> Group:
        for g in self.groups:
            if g.name == name:
                return g
        else:
            g = self.add_group(name)
            return g

    def to_xml(self) -> str:
        head = f"""<Group>
            <Name>{self.name}</Name>
            {{entries}}
            {{groups}}
        </Group>"""
        entries = "\n".join([e.to_xml() for e in self.entries])
        groups = "\n".join([g.to_xml() for g in self.groups])
        return head.format(entries=entries, groups=groups)

    def to_dict(self) -> dict:
        return {
            "Name": self.name,
            "Entry": [
                e.to_dict() for e in self.entries
            ],
            "Group": [
                g.to_dict() for g in self.groups
            ]
        }


def make_xml(group: Group, filepath: str):
    with open(filepath, "w", encoding="utf8") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<KeePassFile>
    <Root>
        {group.to_xml()}
    </Root>
</KeePassFile>""")


def is_google_drive_url(url: str) -> bool:
    return urlparse(url).netloc in ("docs.google.com", "drive.google.com")


def bm2xml(xml_filepath: str, google_only: bool, bmx_db: BmxDB):
    root = Group("Bookmarks")
    for url in bmx_db:
        if google_only and not is_google_drive_url(url):
            continue

        info = bmx_db[url]
        bookmark = info["name"]
        profiles = info["profiles"]
        one_profile_id = list(profiles.keys())[0]
        _, position = profiles[one_profile_id]

        sub_g = root.get_group(one_profile_id)
        d_addr = position.split("/")
        ln_d_addr = len(d_addr)

        i = 1
        ss_g = sub_g
        while i < ln_d_addr:
            ss_g = ss_g.get_group(d_addr[i])
            i += 1
        ss_g.add_entry(escape(bookmark), escape(url))

    make_xml(root, xml_filepath)
