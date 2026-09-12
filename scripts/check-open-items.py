#!/usr/bin/env python3
"""Check the `open_items` frontmatter of every context file against one written form.

Run from the container root:

    python3 scripts/check-open-items.py

With no path argument the script reads the list at `scripts/open-items-files.txt`.
A path argument checks something else, which is what the tests use. A directory
argument checks every `*.md` file below it. An entry below it that the filesystem
cannot describe, such as a broken symlink, is a failure naming the path, exactly
as a path argument that does not resolve is, and a directory the process cannot
list is a failure naming the path and the error type. A subdirectory reached
through a symlink is never followed, and is a question naming the path:

    python3 scripts/check-open-items.py AGENTS.md central-context/AGENTS.md
    python3 scripts/check-open-items.py /path/to/a/fixture/root

The `open_items` schema in `central-context/AGENTS.md`, under `Open items
schema`, is the authority on the format. This script reads the one form that
section's example states, and refuses every other form by name:

    ---
    open_items:
      - id: kebab-case-slug
        opened: 2026-09-11
        checked: 2026-09-11
        triggers: [short phrase, another short phrase]
        asks: One sentence, or "" when no decision is owed.
        item: >
          One paragraph, on continuation lines indented six spaces.
    ---

`open_items:` sits at column 0 inside frontmatter with nothing after the colon.
Two rules find a line that means to be that key, and both refuse it by name
rather than reading it as the content of some other block and dropping every item
under it. At column 0 a line is the key when a space, a tab, a colon or the end of
the line follows the name, whatever comes after that, because a frontmatter line
at column 0 is a key and prose only reaches this scan indented. The rule names
what ends the name instead of listing what may not follow it, because a plain YAML
key may carry almost any printable character: any other suffix, `open_items-log:`
and `open_items.log:` among them, is a different key and is never reported.
Indented, a line is the key when the name is followed by a colon or by the end of
the line, which leaves a folded paragraph free to open a wrapped line with the
word.
An item opens at exactly two spaces with `- id:`. The five other keys each sit
on their own line at exactly four spaces, in the order above. `item: >` takes
continuation lines at exactly six spaces. A blank line inside the block is
ignored. A key at column 0 ends the block, and every other top-level key is
ignored. A file with frontmatter and no `open_items` key reports nothing.

Nothing wider is read. YAML permits more, and the specification pins no column:
https://yaml.org/spec/1.2.2/ section 6.1 states that "in general, indentation is
defined as a zero or more space characters at the start of a line", and that the
`-` that opens a block collection entry is handled "on a case-by-case basis by
the relevant productions". So one form is declared here rather than inferred,
and a refused form that names itself beats one silently dropped.

Refused, each on one line naming the path, the line number, the shape found and
the edit that fixes it. A refused item is dropped whole, so no file is ever
half-read while appearing read:

- The file: a byte order mark, CRLF line endings, frontmatter with no closing
  `---`, a fenced code block in the body that never closes, a tab anywhere in
  the block. A file with no frontmatter at all and no `open_items:` anywhere
  reports nothing, because it carries no item and the schema asks for
  frontmatter only where an item lives.
- The block: `open_items:` carrying a value, the key at any indent but column 0,
  a tab before the key, the key written with no colon, a space or a tab between
  the name and its colon, the name at column 0 followed by text and no colon, a
  line inside the block that matches none of the accepted patterns.
- The entry: a `-` at any column but two, a `-` alone on its line, a flow
  mapping, a quoted key, an unknown key, a first key other than `id`, a
  repeated key, a missing key, the six keys out of order.
- The values: an `id` that is not lowercase letters, digits and single hyphens,
  an `id` used twice in one file, a date that is not `YYYY-MM-DD` or not a real
  calendar date, a `checked` date before `opened`, a date after the run date,
  `triggers` that is not a bracketed list on its own line, an empty `triggers`,
  an `asks` that runs past its own line or is a block scalar or empty, an
  unquoted ` #` in an inline value, a quote round part of an inline value and
  not the whole of it, an `item` header other than `>`, `item`
  text on the key's own line, and an `item` paragraph that is absent or at any
  indent but six.

Three output classes:

- A failure. A refused shape, an unreadable path, or a file that declares
  `open_items:` and yields no item. Reading nothing is never a pass.
- A question. Zero files declaring `open_items:` across the whole run, which
  means the paths are wrong, an `open_items:` at column 0 outside
  frontmatter and outside a fenced code block, which is unread and may be an
  example, and a subdirectory reached through a symlink, which the walk refuses
  to follow and so never read. A question blocks and asserts nothing about the
  file being wrong.
  A line inside a fenced block is skipped instead, because a fenced example is
  documentation and never was a declaration. `fenced()` says which fence forms
  are read and which are not.
- A due item. Its `checked` date is older than the cutoff, which the script
  computes from the run date. It is a reading pass for `wiki-verify` and never
  affects the exit code.

Every run prints how many files were read, how many declare `open_items:`, and
how many items were parsed, so a reader can see that the script read something.

The exit code is the failures plus the questions, capped at 125, so this works
as a pre-commit hook with no wrapper. Every path that cannot be read is a
failure naming the path. The script never raises on a tree shape.

Standard library only.
"""

import argparse
import datetime
import re
import stat
import sys
from pathlib import Path

FILE_LIST = "scripts/open-items-files.txt"
STALE_DAYS = 14

# The schema's field list, in the schema's order. The order is checked, because
# reading the keys in any order is what let a shape check compare one item's
# date against another item's.
KEYS = ("id", "opened", "checked", "triggers", "asks", "item")
KEY_LIST = ", ".join(KEYS)

DASH_INDENT = 2
KEY_INDENT = 4
ITEM_INDENT = 6

# The schema's "lowercase, hyphens".
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# A line that means to be a key, so a bad indent is reported as a bad indent
# rather than as an unrecognized line.
KEY_LINE_RE = re.compile(r"^[A-Za-z_\"'][^:]*:")
# An indented frontmatter line that means to be the `open_items` key: the name,
# then a colon or the end of the line. That catches an indented key, a
# tab-indented key and a key with the colon left off, each of which used to be
# read as block content and dropped every item in the file in silence. It stops
# at the colon so that a folded prose value under another key may open a wrapped
# line with the word and pass, which this tree's own item paragraphs do.
OPEN_ITEMS_RE = re.compile(r"^open_items[ \t]*(:|$)")
# The same name at column 0, recognised by what ends the name rather than by what
# may not follow it: a space, a tab, a colon, or the end of the line. A top-level
# frontmatter line is a key by definition, because a folded paragraph's wrapped
# line always carries indentation, so `open_items` followed by text with no colon
# is a broken key there and never prose. The rule is inverted because a plain YAML
# key may legally carry almost any printable character, a hyphen and a dot among
# them, so no list of excluded characters can be complete and every name this one
# does not terminate is a different key, which criterion 8 says is never reported.
# Settled by the owner on 2026-09-12: "Invert the rule: it is our key only when a
# space, tab, colon or line end follows."
TOP_LEVEL_OPEN_ITEMS_RE = re.compile(r"^open_items(?=[ \t:]|$)")
# A fenced code block in CommonMark's form, narrowed to the markers this tree
# writes: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
FENCE_RE = re.compile(r"^(`{3,}|~{3,})")
BOM = "﻿"
QUOTE_CHARS = "\"'"
QUOTES = tuple(QUOTE_CHARS)


def shown(path, root):
    """The path as findings print it: relative to the root where it can be."""
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return str(path)


def leading(line):
    """The number of leading spaces. A tab is never indentation here."""
    return len(line) - len(line.lstrip(" "))


def trailing_text(line):
    """What follows `open_items` on a column-0 line, with spaces and tabs off.

    A leading `:` survives, so the caller can tell a key carrying a value from a
    line that never was a key. `""` when nothing follows the name.
    """
    return line.rstrip()[len("open_items"):].lstrip(" \t")


def refuse(failures, rel, lineno, message):
    """Append one refusal and return None, so a caller can `return refuse(...)`."""
    failures.append(f"{rel}:{lineno}: {message}")
    return None


def inline_value(value):
    """(text, problem) for an inline scalar. Quotes come off, ` #` is refused.

    YAML reads a `#` preceded by a space as the start of a comment, so an
    unquoted value carrying one ends early and the rest of the line is lost. A
    quoted value keeps its `#`, which is the fix the message names.
    """
    if len(value) > 1 and value[0] in QUOTES and value[-1] == value[0]:
        return value[1:-1], None
    if value[0] in QUOTES or value[-1] in QUOTES:
        return None, "carries an unbalanced quote. Quote the whole value, or none of it"
    if " #" in value:
        return None, (
            "carries an unquoted ` #`, which YAML reads as the start of a comment, so the "
            "value ends there. Wrap the whole value in double quotes"
        )
    return value, None


def frontmatter_span(lines):
    """(first, last) line indices of the frontmatter content, or None.

    Frontmatter starts at a first line that is exactly `---` and ends at the
    next line that is exactly `---`. Nothing else counts, so an `open_items:` in
    the body is not read.
    """
    if not lines or lines[0] != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i] == "---":
            return 1, i
    return None


def fenced(lines, start):
    """(the indices inside a fenced code block, the fence a line left open).

    A fenced example is documentation, not a declaration, so an `open_items:`
    inside one is neither read nor reported. Only the marker forms this tree
    writes are read: a run of three or more backticks or tildes at column 0,
    with an info string such as `yaml` on the opening line. Not read as a
    fence: a marker indented by one or more spaces, and any other marker. That
    boundary errs toward a question, which blocks, and never toward a silent
    drop.

    A line closes a fence only when it repeats the same character, is at least
    as long, and carries nothing else. The length test is what lets a fence
    hold a shorter fence: without it the outer closing line reads as a second
    opening and every line below it falls inside a fence that never ends.

    `opened` is (the index, the marker) of a fence with no closing line, or None.
    Everything below it is inside a fence forever, so a real `open_items:` there
    would vanish. The caller reports that, because silence is the one outcome
    this script exists to prevent. The marker travels with the index because the
    refusal names the fence characters found: a reader looking for the closing
    line needs to know which characters, and how many, would close it.

    The scan starts below the frontmatter, so it can never move the `---` lines
    the frontmatter span is read from. Frontmatter is YAML and carries no fence.
    """
    inside, marker, opened = set(), None, None
    for i in range(start, len(lines)):
        found = FENCE_RE.match(lines[i])
        if marker is None:
            if found:
                marker, opened = found.group(1), (i, found.group(1))
        elif (found and found.group(1)[0] == marker[0]
                and len(found.group(1)) >= len(marker)
                and not lines[i][found.end():].strip()):
            marker, opened = None, None
        else:
            inside.add(i)
    return inside, opened


def in_block(line):
    """True while a line belongs to the block a top-level key opened.

    A tab-led line counts as inside, so the tab check sees it rather than the
    block ending one line early and the tab going unreported. A `-` at column 0
    counts as inside for the same reason: it is a refused entry, and the block
    ending there would report nothing but a block that yielded no item.
    """
    return not line.strip() or line.startswith((" ", "\t")) or line.strip().startswith("-")


def block_end(lines, start, last):
    """The index where the open_items block stops: a key at column 0, or the end."""
    for i in range(start, last):
        if not in_block(lines[i]):
            return i
    return last


def read_item(rel, chunk, today, failures):
    """One item from the lines of one entry, or None after saying why not.

    `chunk` is [(lineno, text)], opening with the `  - id:` line. The first
    refusal returns, so a refused item is never half-read and nothing
    downstream sees a field the entry's shape did not support.
    """
    n, first = chunk[0]
    indent = leading(first)
    stripped = first.strip()
    if indent != DASH_INDENT:
        return refuse(failures, rel, n, f"`-` at column {indent}. An item opens at exactly two spaces, `  - id: slug`.")
    rest = stripped[1:]
    if not rest.strip():
        return refuse(failures, rel, n, "`-` alone on its line. Write the first key beside it, `  - id: slug`.")
    if not rest.startswith(" "):
        return refuse(failures, rel, n, "`-` with no space after it. Write `  - id: slug`.")
    rest = rest.strip()
    if rest.startswith("{"):
        return refuse(failures, rel, n, "a flow mapping entry. Write one key per line, opening `  - id: slug`.")

    # The id sits beside the dash, so its row is read as a key row. Blank lines
    # drop here: one does not end an item, and dropping them makes the next row
    # the next row.
    rows = [(n, KEY_INDENT, rest)]
    rows += [(m, leading(text), text.strip()) for m, text in chunk[1:] if text.strip()]

    fields, order, key_line = {}, [], {}
    para, item_line, in_item = [], n, False
    for k, (m, ind, text) in enumerate(rows):
        if in_item and ind > KEY_INDENT:
            if ind != ITEM_INDENT:
                return refuse(failures, rel, m, f"an `item: >` continuation line at indent {ind}. The paragraph sits at exactly six spaces.")
            para.append(text)
            continue
        in_item = False  # four or fewer leading spaces ends the paragraph
        if ind != KEY_INDENT:
            if KEY_LINE_RE.match(text):
                return refuse(failures, rel, m, f"an item key at indent {ind}. An item key sits at exactly four spaces.")
            return refuse(failures, rel, m, f"an unrecognized line, {text!r}. The block holds `  - id:`, a key at four spaces, and an `item: >` paragraph at six.")

        key, sep, value = text.partition(":")
        if not sep:
            return refuse(failures, rel, m, f"an unrecognized line, {text!r}. The block holds `  - id:`, a key at four spaces, and an `item: >` paragraph at six.")
        if key[:1] in QUOTES:
            return refuse(failures, rel, m, f"a quoted key, {key}. Write the key bare, `{key.strip(QUOTE_CHARS)}: value`.")
        if value and not value.startswith(" "):
            return refuse(failures, rel, m, f"key '{key}' with no space after the colon. Write `{key}: value`.")
        value = value.strip()

        if not order and key != "id":
            return refuse(failures, rel, m, f"an entry opening with key '{key}'. The first key is `id`.")
        if key not in KEYS:
            return refuse(failures, rel, m, f"an unknown key '{key}'. The keys are {KEY_LIST}.")
        if key in fields:
            return refuse(failures, rel, m, f"key '{key}' twice in one item. Write each key once.")
        expected = KEYS[len(order)]
        if key != expected:
            # Out of order and missing look the same at this line. Read ahead to
            # tell them apart, so the message names the one that is wrong.
            later = any(ind2 == KEY_INDENT and text2.startswith(f"{expected}:") for _, ind2, text2 in rows[k + 1:])
            if later:
                return refuse(failures, rel, m, f"key '{key}' before '{expected}'. The order is {KEY_LIST}.")
            return refuse(failures, rel, m, f"no `{expected}:` line in this item. The keys are {KEY_LIST}.")
        nxt = rows[k + 1] if k + 1 < len(rows) else None
        # A deeper line below an inline value continues it, unless it means to
        # be a key, in which case its own indent is what is wrong with it.
        runs_on = nxt is not None and nxt[1] > KEY_INDENT and not KEY_LINE_RE.match(nxt[2])

        if key == "id":
            if not ID_RE.match(value):
                return refuse(failures, rel, m, f"id '{value}' is not lowercase letters, digits and single hyphens.")
            fields[key] = value
        elif key in ("opened", "checked"):
            if not DATE_RE.match(value):
                return refuse(failures, rel, m, f"{key} '{value}' is not a date. Write it as YYYY-MM-DD, unquoted.")
            try:
                fields[key] = datetime.date(*(int(part) for part in value.split("-")))
            except ValueError:
                return refuse(failures, rel, m, f"{key} '{value}' is not a real calendar date.")
        elif key == "triggers":
            if not value:
                if runs_on and nxt[2].startswith("-"):
                    return refuse(failures, rel, m, "triggers: as a block list. Write it on one line, `triggers: [first phrase, second phrase]`.")
                return refuse(failures, rel, m, "triggers: with nothing after it. Write at least one phrase, `triggers: [first phrase]`. An item with no trigger never surfaces.")
            if not value.startswith("["):
                return refuse(failures, rel, m, "triggers: is not a bracketed list. Write it on one line, `triggers: [first phrase, second phrase]`.")
            if not value.endswith("]"):
                return refuse(failures, rel, m, "triggers: runs past its own line. Write the whole list on one line, `triggers: [first phrase, second phrase]`.")
            if runs_on:
                return refuse(failures, rel, nxt[0], "a line continuing triggers:. Write the whole list on one line, `triggers: [first phrase, second phrase]`.")
            inner = value[1:-1].strip()
            if not inner:
                return refuse(failures, rel, m, "triggers: is an empty list. Write at least one phrase, `triggers: [first phrase]`. An item with no trigger never surfaces.")
            entries = []
            for part in inner.split(","):
                part = part.strip()
                if not part:
                    return refuse(failures, rel, m, "an empty entry in triggers:. Write one phrase between each comma.")
                entry, problem = inline_value(part)
                if problem:
                    return refuse(failures, rel, m, f"a triggers: entry that {problem}.")
                entries.append(entry)
            fields[key] = entries
        elif key == "asks":
            if runs_on:
                return refuse(failures, rel, nxt[0], "a line continuing asks:. Write the question on the key's own line, or `asks: \"\"` when no decision is owed.")
            if value[:1] in (">", "|"):
                return refuse(failures, rel, m, f"asks: as a block scalar, '{value}'. Write the question on the key's own line, or `asks: \"\"` when no decision is owed.")
            if not value:
                return refuse(failures, rel, m, "asks: with nothing after it. Write the question, or `asks: \"\"` when no decision is owed.")
            asks, problem = inline_value(value)
            if problem:
                return refuse(failures, rel, m, f"an asks: value that {problem}.")
            fields[key] = asks
        elif key == "item":
            if not value:
                return refuse(failures, rel, m, "item: with no header. Write `item: >` and the paragraph at six spaces below it.")
            if value != ">":
                if value[0] in (">", "|"):
                    return refuse(failures, rel, m, f"item: header '{value}'. Write `item: >` and nothing else.")
                return refuse(failures, rel, m, "item: with text on the key's own line. Write `item: >` and the paragraph at six spaces below it.")
            fields[key] = ">"
            item_line, in_item = m, True
        order.append(key)
        key_line[key] = m

    if len(order) < len(KEYS):
        return refuse(failures, rel, n, f"no `{KEYS[len(order)]}:` line in this item. The keys are {KEY_LIST}.")
    if not para:
        return refuse(failures, rel, item_line, "item: > with no continuation line. Write the paragraph at six spaces below it.")
    if fields["checked"] < fields["opened"]:
        return refuse(failures, rel, key_line["checked"], f"checked {fields['checked']} before opened {fields['opened']}. Nothing is verified before it is written.")
    for key in ("opened", "checked"):
        if fields[key] > today:
            return refuse(failures, rel, key_line[key], f"{key} {fields[key]} after the run date {today}. A date in the future never goes old.")
    # The paragraph is read to prove that it is there, and never printed: a
    # listing carrying six paragraphs is not a listing.
    fields["paragraph"] = " ".join(para)
    fields["line"] = n
    return fields


def read_block(rel, lines, start, last, today, failures):
    """Every item in one block. Returns (items, the index where the block ends)."""
    end = block_end(lines, start, last)
    items = []
    for i in range(start, end):
        if "\t" in lines[i]:
            refuse(failures, rel, i + 1, "a tab character. YAML forbids a tab in indentation, so nothing in this block is read. Use spaces.")
            return items, end

    # An entry opens at four or fewer leading spaces. A `-` deeper than that is
    # paragraph text, which an `item: >` block is free to carry.
    chunks, chunk = [], None
    for i in range(start, end):
        line = lines[i]
        if line.strip().startswith("-") and leading(line) <= KEY_INDENT:
            chunk = [(i + 1, line)]
            chunks.append(chunk)
        elif chunk is not None:
            chunk.append((i + 1, line))
        elif line.strip():
            refuse(failures, rel, i + 1, f"a line before the first item, {line.strip()!r}. An item opens at two spaces, `  - id: slug`.")
    for chunk in chunks:
        item = read_item(rel, chunk, today, failures)
        if item is not None:
            items.append(item)
    return items, end


def check_file(path, rel, today, failures, questions):
    """Read one file. Returns (declares, items).

    `declares` is True when the frontmatter carries a line that means to be the
    `open_items` key, whatever shape the key and the block turned out to be. The
    caller needs that to report a file that declares a block and yields no item,
    and a key at the wrong indent has to set it for the same reason: the file
    holds items, and reporting nothing about it is the defect.
    """
    try:
        # newline="" turns off universal newlines. Without it Python translates
        # \r\n to \n on the way in and the CRLF check below can never fire.
        with path.open(encoding="utf-8", newline="") as handle:
            text = handle.read()
    except UnicodeDecodeError:
        failures.append(f"{rel}: is not UTF-8 text")
        return False, []
    except OSError as exc:
        failures.append(f"{rel}: cannot be read, {type(exc).__name__}")
        return False, []
    if text.startswith(BOM):
        failures.append(f"{rel}: starts with a byte order mark, so --- is not the first thing in it. Save it as UTF-8 with no BOM.")
        return False, []
    if "\r" in text:
        failures.append(f"{rel}: uses CRLF line endings, so no line is exactly ---. Save it with LF endings.")
        return False, []

    lines = text.split("\n")
    span = frontmatter_span(lines)
    if span is None and lines and lines[0] == "---":
        # It opened frontmatter and never closed it, so it means to carry items.
        # That one message covers the file; the stray scan below would add a
        # second line for the same defect.
        failures.append(f"{rel}:1: frontmatter with no closing ---, so nothing in it is read")
        return False, []
    # A fenced example is documentation. An unclosed fence hides every line
    # below it, so it is a failure naming the line it opened on.
    in_fence, unclosed = fenced(lines, span[1] + 1 if span else 0)
    if unclosed is not None:
        at, marker = unclosed
        failures.append(
            # The marker prints bare. Wrapping a run of backticks in backticks
            # reads as one longer run and hides the very thing being named.
            f"{rel}:{at + 1}: a fenced code block opens here with {marker} and never closes, "
            f"so no `open_items:` below it is read. Close it with a line of {marker} at column 0."
        )
    # An occurrence at column 0 outside frontmatter is not read. It blocks as a
    # question, because it is as likely a documented example as a real block
    # written in the wrong place, and the script cannot tell which. Inside a
    # fence it is documentation, so it is skipped rather than asked about.
    stray = [
        i for i, line in enumerate(lines)
        if line.startswith("open_items:") and i not in in_fence
        and not (span and span[0] <= i < span[1])
    ]
    for i in stray:
        questions.append(
            f"{rel}:{i + 1}: open_items: at column 0 outside frontmatter, so nothing under it is "
            "read. Indent it if it is an example, or move it into frontmatter if it is real."
        )
    if span is None:
        # A file with no frontmatter and no `open_items:` anywhere carries no
        # item, which is a legitimate state: the schema asks for frontmatter
        # only where an item lives. Where the file does carry an `open_items:`
        # outside
        # frontmatter, the question above is the finding and nothing here adds
        # to it.
        return False, []

    first, last = span
    declares, items, seen = False, [], set()
    i = first
    while i < last:
        line = lines[i]
        if not (OPEN_ITEMS_RE.match(line.strip()) or TOP_LEVEL_OPEN_ITEMS_RE.match(line)):
            # Block content and every other top-level key are skipped, and
            # neither is ever reported. The key is matched on the stripped line
            # rather than at column 0, because a key one space in is a key that
            # means to declare items: reading it as block content is what
            # dropped a whole file with no finding. At column 0 the wider match
            # applies, where any trailing shape is a broken key and no prose can
            # reach: an accepted block consumes its own paragraph lines, so the
            # scan never sees one.
            i += 1
            continue
        declares = True
        indent = line[:len(line) - len(line.lstrip(" \t"))]
        if "\t" in indent:
            # Named apart from the indent refusal below, because the fix differs:
            # this one is spaces instead of the tab, that one is column 0.
            refuse(failures, rel, i + 1, "a tab before `open_items`. YAML forbids a tab in indentation, so nothing under the key is read. Write `open_items:` at column 0 and indent every line below it with spaces.")
        elif indent:
            refuse(failures, rel, i + 1, f"`open_items` at indent {len(indent)}. The key sits at column 0 with nothing after the colon, `open_items:`, then one `  - id: slug` line per item.")
        elif line.rstrip() == "open_items":
            refuse(failures, rel, i + 1, "`open_items` with no colon, so it is not a key. Write `open_items:` at column 0 with nothing after the colon, then one `  - id: slug` line per item.")
        elif not trailing_text(line).startswith(":"):
            # Its own message, because its own fix: the colon goes in and the
            # trailing text comes out, so the message names the text to delete.
            # The colonless-key message above would name half the edit.
            refuse(failures, rel, i + 1, f"`open_items` followed by {trailing_text(line)!r} and no colon, so the line is not a key. Write `open_items:` at column 0 with nothing after the colon, then one `  - id: slug` line per item.")
        elif not line.startswith("open_items:"):
            # Its own message, because the whole fault is the space or the tab
            # between the name and the colon. The value message below would name
            # a value this line does not carry, so a reader would look for text
            # to delete, find none, and run the check again unchanged.
            #
            # When the line carries a value as well, both faults go in this one
            # message and the value is named. The whitespace message alone sends
            # the reader to one edit, and the value refusal they were never told
            # about meets them on the next run. That is the same rule criteria 65
            # and 68 apply: a message that names half an edit sends the reader
            # back.
            value = trailing_text(line)[1:].strip()
            shape = "a space or a tab between `open_items` and its colon"
            if value:
                shape += f", and the value {value!r} after it"
            refuse(failures, rel, i + 1, f"{shape}. Write `open_items:` at column 0 with the colon against the name and nothing after it, then one `  - id: slug` line per item.")
        elif line.rstrip() != "open_items:":
            refuse(failures, rel, i + 1, "open_items: with a value on its own line. Write `open_items:` with nothing after the colon, then one `  - id: slug` line per item.")
        else:
            found, i = read_block(rel, lines, i + 1, last, today, failures)
            for item in found:
                if item["id"] in seen:
                    refuse(failures, rel, item["line"], f"id '{item['id']}' twice in one file. An id is unique in the file and is never reused after a close.")
                    continue
                seen.add(item["id"])
                item["file"] = rel
                items.append(item)
            continue
        i = block_end(lines, i + 1, last)
    if declares and not items:
        failures.append(f"{rel}: declares open_items: and yields no item")
    return declares, items


def load_file_list(root, failures):
    """The checked-in list of context files. One path per line, # starts a comment."""
    path = root / FILE_LIST
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        failures.append(f"{FILE_LIST}: missing or unreadable, so no file can be checked")
        return []
    except UnicodeDecodeError:
        failures.append(f"{FILE_LIST}: is not UTF-8 text, so no file can be checked")
        return []
    paths = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            paths.append(line)
    if not paths:
        failures.append(f"{FILE_LIST}: names no file, so nothing would be read")
    return paths


FILE, DIRECTORY, UNREADABLE = "file", "directory", "unreadable"


def entry_kind(path):
    """What a path is: FILE, DIRECTORY, or UNREADABLE when stat() will not say.

    `Path.is_file()` and `Path.is_dir()` both answer False when `stat()` raises,
    so a dangling or self-referential symlink looks the same as a plain file that
    is not there. Filtering a walk through `is_file()` therefore dropped such an
    entry with no finding and no place in the file count, which is the silent
    drop this script exists to prevent. `stat()` is called once here and its
    OSError becomes a kind the caller reports, never a swallowed False.

    Anything that stat describes and is not a directory is FILE, so a walked
    entry and a path argument reach `check_file()` on the same rule.
    """
    try:
        mode = path.stat().st_mode
    except OSError:
        return UNREADABLE
    return DIRECTORY if stat.S_ISDIR(mode) else FILE


def walk(path, root, failures, questions):
    """(files, unreadable) for every `*.md` entry below one directory.

    `Path.rglob` raises nothing on a directory the process cannot list: it
    swallows the OSError and yields nothing, so an unreadable directory holding
    a valid item file reported one file read, no finding and no item. That is
    the silent drop `entry_kind()` already removed for a single entry, so this
    walks one directory at a time and reports the OSError the same way, naming
    the path and the error type.

    A subdirectory reached through a symlink is not descended into, which is what
    `rglob` does today and what keeps a link pointing back up the tree from
    walking forever. The skip is a question and not a failure: the link is a
    legitimate shape, so nothing here says the tree is wrong, and the run still
    says out loud that it read nothing under it. Settled by the owner on 2026-09-12:
    "Report the skipped link as a finding, keep not descending."
    """
    files, unreadable = [], set()
    try:
        entries = sorted(path.iterdir())
    except OSError as exc:
        failures.append(f"{shown(path, root)}: cannot be listed, {type(exc).__name__}")
        return files, unreadable
    for entry in entries:
        kind = entry_kind(entry)
        if kind == DIRECTORY:
            if entry.is_symlink():
                # Following it is the one fix that is not available, so the
                # message names the other one. A path named in the file list is
                # described by one stat(), which resolves the link and never
                # recurses, and that is how the default run reads every file.
                questions.append(
                    f"{shown(entry, root)}: a symlinked directory, which the walk never follows, "
                    f"so no file under it is read. Name this path in {FILE_LIST} if it should be read."
                )
                continue
            # A real directory named *.md is nothing to read, and it is descended
            # into here, so it is not a finding either.
            found, blocked = walk(entry, root, failures, questions)
            files.extend(found)
            unreadable |= blocked
            continue
        if entry.suffix != ".md":
            continue
        if kind == UNREADABLE:
            failures.append(f"{shown(entry, root)}: no such file or directory")
            unreadable.add(entry)
        files.append(entry)
    return files, unreadable


def gather(given, root, failures, questions):
    """(files, unreadable): every *.md path to read, in the order given, once each.

    An entry the filesystem will not describe is a failure here, in the same
    words a path argument that does not resolve gets, because it is the same
    fault. It stays in `files` so that the count names it, and `unreadable`
    holds it so that the caller does not try to open what stat could not reach.
    A directory argument the process cannot list is a failure in `walk()`, and a
    symlinked subdirectory below it is a question there.
    """
    files, seen, unreadable = [], set(), set()
    for one in given:
        path = Path(one)
        if not path.is_absolute():
            path = root / path
        kind = entry_kind(path)
        if kind == DIRECTORY:
            found, blocked = walk(path, root, failures, questions)
            unreadable |= blocked
        elif kind == FILE:
            found = [path]
        else:
            failures.append(f"{shown(path, root)}: no such file or directory")
            continue
        for one_file in found:
            if one_file not in seen:
                seen.add(one_file)
                files.append(one_file)
    return files, unreadable


def run(root, given=None, today=None, stale_days=STALE_DAYS):
    """Check one tree.

    Returns (failures, questions, due, items, files, declaring). Findings print
    in the order the files were read.
    """
    root = Path(root)
    today = today or datetime.date.today()
    failures, questions = [], []
    if given is None:
        given = load_file_list(root, failures)
    files, unreadable = gather(given, root, failures, questions)

    declaring, items = 0, []
    for path in files:
        if path in unreadable:
            continue  # already a failure, and nothing here can open it
        declares, found = check_file(path, shown(path, root), today, failures, questions)
        declaring += 1 if declares else 0
        items.extend(found)

    if not declaring:
        questions.append(
            "no file read declares open_items:. That is a legitimate state and is almost "
            f"always the wrong paths. {len(files)} file(s) read under {root}."
        )

    cutoff = today - datetime.timedelta(days=stale_days)
    due = [
        f"{item['file']} · {item['id']} · checked {item['checked']} · older than {cutoff}"
        for item in items if item["checked"] < cutoff
    ]
    return failures, questions, due, items, files, declaring


def listing(items):
    """One line per item: file, id, dates, whether asks is set, triggers.

    The `asks` state is what step 3 of `wiki-open-items` branches on: an empty
    `asks` closes by work, a set one is a decision owed to the owner.
    """
    return [
        "{} · {} · opened {} · checked {} · asks {} · {}".format(
            item["file"], item["id"], item["opened"], item["checked"],
            "set" if item["asks"] else "empty", ", ".join(item["triggers"]),
        )
        for item in items
    ]


def main(argv):
    parser = argparse.ArgumentParser(
        prog="check-open-items.py",
        description="Check open_items frontmatter against the one form the schema states.",
    )
    parser.add_argument("paths", nargs="*", help=f"files or directories. Default: the list in {FILE_LIST}")
    parser.add_argument("--root", default=None, help="the path findings print relative to. Default: the container root")
    parser.add_argument("--stale-days", type=int, default=STALE_DAYS, help=f"the due window, in days. Default: {STALE_DAYS}")
    parser.add_argument("--today", default=None, help="the run date, YYYY-MM-DD. Default: today")
    parser.add_argument("--findings-only", action="store_true", help="print the findings and the counts, not the item listing")
    args = parser.parse_args(argv[1:])

    root = Path(args.root) if args.root else Path(__file__).resolve().parent.parent
    today = None
    if args.today:
        if not DATE_RE.match(args.today):
            print(f"--today '{args.today}' is not a date. Write it as YYYY-MM-DD.")
            return 1
        try:
            today = datetime.date(*(int(part) for part in args.today.split("-")))
        except ValueError:
            print(f"--today '{args.today}' is not a real calendar date.")
            return 1
    if args.stale_days < 0:
        print(f"--stale-days {args.stale_days} is negative. Write a whole number of days.")
        return 1

    failures, questions, due, items, files, declaring = run(root, args.paths or None, today, args.stale_days)

    for line in failures:
        print(line)
    if questions:
        if failures:
            print()
        print("Questions. Each one blocks and says nothing about the file being wrong:")
        for line in questions:
            print(line)
    if due:
        if failures or questions:
            print()
        print("Due. Nobody has tested these claims since the date shown. wiki-verify re-tests them:")
        for line in due:
            print(line)
    if items and not args.findings_only:
        if failures or questions or due:
            print()
        for line in listing(items):
            print(line)
    if failures or questions or due or (items and not args.findings_only):
        print()
    print(f"{len(files)} file(s) read")
    print(f"{declaring} file(s) declaring open_items:")
    print(f"{len(items)} item(s)")
    print(f"{len(failures)} failure(s)")
    print(f"{len(questions)} question(s)")
    print(f"{len(due)} due item(s)")
    return min(len(failures) + len(questions), 125)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
