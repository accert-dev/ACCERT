"""Small SON parser fallback for ACCERT input files.

This parser supports the SON subset used by ACCERT tutorial inputs: nested
objects, optional object identifiers, keyed values, comments, strings, and
numbers. It intentionally does not replace WASP/HIVE schema validation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from pathlib import Path


class SONParseError(ValueError):
    """Raised when the fallback SON parser cannot parse an input file."""


@dataclass
class SONNode:
    name: str
    id_value: str | None = None
    value: str | None = None
    children: list["SONNode"] = field(default_factory=list)


class _Tokenizer:
    _PUNCTUATION = set("{}()[]=:,")

    def __init__(self, text: str):
        self.text = text
        self.pos = 0

    def peek(self) -> str | None:
        pos = self.pos
        token = self.next()
        self.pos = pos
        return token

    def next(self) -> str | None:
        self._skip_ws_and_comments()
        if self.pos >= len(self.text):
            return None
        char = self.text[self.pos]
        if char in self._PUNCTUATION:
            self.pos += 1
            return char
        if char in ("'", '"'):
            return self._quoted()
        return self._bare()

    def expect(self, expected: str) -> None:
        token = self.next()
        if token != expected:
            raise SONParseError(f"Expected {expected!r}, found {token!r}")

    def _skip_ws_and_comments(self) -> None:
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isspace():
                self.pos += 1
                continue
            if char == "%":
                while self.pos < len(self.text) and self.text[self.pos] not in "\r\n":
                    self.pos += 1
                continue
            break

    def _quoted(self) -> str:
        quote = self.text[self.pos]
        start = self.pos
        self.pos += 1
        escaped = False
        while self.pos < len(self.text):
            char = self.text[self.pos]
            self.pos += 1
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == quote:
                return self.text[start:self.pos]
        raise SONParseError("Unterminated quoted string")

    def _bare(self) -> str:
        start = self.pos
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isspace() or char in self._PUNCTUATION or char == "%":
                break
            self.pos += 1
        return self.text[start:self.pos]


def parse_son(text: str) -> SONNode:
    tokenizer = _Tokenizer(text)
    root = SONNode("document")
    while tokenizer.peek() is not None:
        root.children.append(_parse_statement(tokenizer))
    return root


def parse_son_file(path: str | Path) -> SONNode:
    return parse_son(Path(path).read_text(encoding="utf-8"))


def son_to_xml(path: str | Path) -> str:
    return _node_to_xml(parse_son_file(path))


def _parse_statement(tokenizer: _Tokenizer) -> SONNode:
    name = tokenizer.next()
    if name is None:
        raise SONParseError("Unexpected end of input")
    if name in _Tokenizer._PUNCTUATION:
        raise SONParseError(f"Expected a name, found {name!r}")

    id_value = None
    if tokenizer.peek() == "(":
        tokenizer.expect("(")
        id_value = tokenizer.next()
        if id_value is None:
            raise SONParseError(f"Missing identifier for {name!r}")
        tokenizer.expect(")")

    token = tokenizer.next()
    if token == "{":
        children = []
        while tokenizer.peek() != "}":
            if tokenizer.peek() is None:
                raise SONParseError(f"Unterminated object {name!r}")
            children.append(_parse_statement(tokenizer))
        tokenizer.expect("}")
        return SONNode(name=name, id_value=id_value, children=children)

    if token == "[":
        values = []
        while tokenizer.peek() != "]":
            value = tokenizer.next()
            if value is None:
                raise SONParseError(f"Unterminated array {name!r}")
            if value != ",":
                values.append(value)
        tokenizer.expect("]")
        return SONNode(name=name, id_value=id_value, value=" ".join(values))

    if token in ("=", ":"):
        value = tokenizer.next()
        if value is None:
            raise SONParseError(f"Missing value for {name!r}")
        return SONNode(name=name, id_value=id_value, value=value)

    raise SONParseError(f"Expected object, array, or assignment after {name!r}; found {token!r}")


def _node_to_xml(node: SONNode, indent: int = 0) -> str:
    space = " " * indent
    pieces = [f"{space}<{node.name}>"]
    child_indent = indent + 2
    if node.id_value is not None:
        pieces.append(f"{' ' * child_indent}<id>{escape(node.id_value)}</id>")
    if node.value is not None:
        pieces.append(f"{' ' * child_indent}<value>{escape(node.value)}</value>")
    for child in node.children:
        pieces.append(_node_to_xml(child, child_indent))
    pieces.append(f"{space}</{node.name}>")
    return "\n".join(pieces)
