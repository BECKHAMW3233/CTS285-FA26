#!/usr/bin/env python3
"""
story_check.py - check the map of a choose-your-own-adventure story.

Use it:
    python story_check.py FILE           check the story
    python story_check.py FILE --map     check it, then print a Mermaid map

FILE can be a Python (.py), C++ (.cpp), or Twee (.twee) file.

How it reads your story
    Python and C++ : a passage is a function named passage_something.
                     An ending is a function named ending_something.
                     A call to another passage is a link.
                     The start passage is passage_start.
    Twee           : a passage is a  :: Name  block.
                     A [[link]] is a link.
                     An ending has a name that starts with Ending.
                     The start passage is set in StoryData (default: Start).

What it finds
    ORPHAN       a passage the player can never reach
    DEAD END     a passage with no links that is not an ending
    BROKEN LINK  a link to a passage that does not exist
    TRAP         a passage from which the player can never reach an ending
    NO START     the start passage is missing
    NO ENDING    the player can never reach any ending

The program exits with code 1 when it finds a problem, and 0 when it does not.
"""

import json
import re
import sys

NODE = r"(?:passage|ending)_\w+"
SPECIAL_TWEE_TAGS = {"startup", "header", "footer", "script", "stylesheet"}

FIXES = {
    "ORPHAN": "Add a choice in another passage that leads here.",
    "DEAD END": "Add a choice, or rename it to start with ending.",
    "BROKEN LINK": "Fix the spelling, or write the missing passage.",
    "TRAP": "Add a choice that leads toward an ending.",
    "NO START": "Name your first passage passage_start (Twee: set it in StoryData).",
    "NO ENDING": "Add an ending and link to it.",
}


# ---------------------------------------------------------------
# Step 1: remove comments and strings, so they cannot look like code
# ---------------------------------------------------------------
def strip_code(text, lang):
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        three = text[i:i + 3]
        two = text[i:i + 2]
        if lang == "py" and three in ('"""', "'''"):
            end = text.find(three, i + 3)
            end = n if end == -1 else end + 3
            out.append("\n" * text.count("\n", i, end))
            i = end
        elif lang == "py" and c == "#":
            while i < n and text[i] != "\n":
                i += 1
        elif lang == "cpp" and two == "//":
            while i < n and text[i] != "\n":
                i += 1
        elif lang == "cpp" and two == "/*":
            end = text.find("*/", i + 2)
            end = n if end == -1 else end + 2
            out.append("\n" * text.count("\n", i, end))
            i = end
        elif c in "\"'":
            j = i + 1
            while j < n and text[j] != c and text[j] != "\n":
                j += 2 if text[j] == "\\" else 1
            out.append('""')
            i = j + 1 if j < n and text[j] == c else j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def find_calls(body):
    """Return the passage names called in a block of code, in order."""
    found = []
    for name in re.findall(rf"\b({NODE})\s*\(", body):
        if name not in found:
            found.append(name)
    return found


# ---------------------------------------------------------------
# Step 2: read the story into a dictionary  {passage: [links]}
# ---------------------------------------------------------------
def read_python(text):
    lines = strip_code(text, "py").expandtabs(4).split("\n")
    nodes = {}
    i = 0
    while i < len(lines):
        match = re.match(rf"^(\s*)def\s+({NODE})\s*\(", lines[i])
        if not match:
            i += 1
            continue
        indent = len(match.group(1))
        name = match.group(2)
        body = []
        i += 1
        while i < len(lines):
            line = lines[i]
            if line.strip() and len(line) - len(line.lstrip()) <= indent:
                break
            body.append(line)
            i += 1
        nodes[name] = find_calls("\n".join(body))
    return nodes, "passage_start"


def read_cpp(text):
    code = strip_code(text, "cpp")
    nodes = {}
    for match in re.finditer(rf"\bvoid\s+({NODE})\s*\([^)]*\)\s*\{{", code):
        depth, j = 1, match.end()
        while j < len(code) and depth:
            if code[j] == "{":
                depth += 1
            elif code[j] == "}":
                depth -= 1
            j += 1
        nodes[match.group(1)] = find_calls(code[match.end():j - 1])
    return nodes, "passage_start"


def twee_links(body):
    links = []
    for inner in re.findall(r"\[\[([^\[\]]+?)\]\]", body):
        if "->" in inner:
            target = inner.rsplit("->", 1)[1]
        elif "<-" in inner:
            target = inner.split("<-", 1)[0]
        elif "|" in inner:
            target = inner.split("|", 1)[1]
        else:
            target = inner
        target = target.strip()
        if target not in links:
            links.append(target)
    return links


def read_twee(text):
    nodes, start = {}, "Start"
    for chunk in re.split(r"(?m)^::[ \t]*", text)[1:]:
        header, _, body = chunk.partition("\n")
        name = re.split(r"\s*[\[{]", header, maxsplit=1)[0].strip()
        tags = set(" ".join(re.findall(r"\[([^\]]*)\]", header)).split())
        if name == "StoryData":
            try:
                start = json.loads(body).get("start", start)
            except ValueError:
                pass
        elif name == "StoryTitle" or tags & SPECIAL_TWEE_TAGS:
            continue
        else:
            nodes[name] = twee_links(body)
    return nodes, start


def read_story(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lower = path.lower()
    if lower.endswith(".py"):
        return "python", *read_python(text)
    if lower.endswith((".cpp", ".cc", ".cxx")):
        return "c++", *read_cpp(text)
    if lower.endswith((".twee", ".tw")):
        return "twee", *read_twee(text)
    sys.exit("Unknown file type. Use .py, .cpp, or .twee.")


# ---------------------------------------------------------------
# Step 3: look for problems
# ---------------------------------------------------------------
def is_ending(name):
    return name.lower().startswith("ending")


def analyze(nodes, start):
    """Return a list of (kind, passage, message)."""
    found = []

    for name, links in nodes.items():
        for target in links:
            if target not in nodes:
                found.append(("BROKEN LINK", name,
                              f"{name} links to {target}, which does not exist."))

    dead_ends = set()
    for name, links in nodes.items():
        if not links and not is_ending(name):
            dead_ends.add(name)
            found.append(("DEAD END", name,
                          f"{name} has no links and is not an ending."))

    if start not in nodes:
        found.append(("NO START", start, f"The start passage {start} was not found."))
        return found

    reached, queue = {start}, [start]
    while queue:
        for target in nodes[queue.pop()]:
            if target in nodes and target not in reached:
                reached.add(target)
                queue.append(target)

    for name in nodes:
        if name not in reached:
            found.append(("ORPHAN", name,
                          f"{name} cannot be reached from {start}."))

    can_finish = {name for name in nodes if is_ending(name)}
    changed = True
    while changed:
        changed = False
        for name, links in nodes.items():
            if name not in can_finish and any(t in can_finish for t in links):
                can_finish.add(name)
                changed = True

    if not any(is_ending(name) for name in reached):
        found.append(("NO ENDING", start, "The player can never reach an ending."))
    else:
        for name in sorted(reached):
            if name not in can_finish and name not in dead_ends:
                found.append(("TRAP", name,
                              f"From {name} the player can never reach an ending."))
    return found


# ---------------------------------------------------------------
# Step 4: print the report, and the map if asked
# ---------------------------------------------------------------
def mermaid_map(nodes, start, findings):
    ids = {name: f"n{i}" for i, name in enumerate(nodes)}
    bad = {passage for _, passage, _ in findings}
    lines = ["```mermaid", "flowchart TD"]
    for name in nodes:
        label = name.replace('"', "'")
        lines.append(f'    {ids[name]}["{label}"]')
    for name, links in nodes.items():
        for target in links:
            if target in ids:
                lines.append(f"    {ids[name]} --> {ids[target]}")
    lines.append("    classDef endNode fill:#1f3a1f,stroke:#4c4,color:#fff")
    lines.append("    classDef badNode fill:#3a1f1f,stroke:#c44,color:#fff")
    lines.append("    classDef startNode stroke-width:4px")
    for css, members in (
        ("endNode", [n for n in nodes if is_ending(n)]),
        ("badNode", [n for n in nodes if n in bad]),
        ("startNode", [n for n in nodes if n == start]),
    ):
        if members:
            lines.append(f"    class {','.join(ids[m] for m in members)} {css}")
    lines.append("```")
    return "\n".join(lines)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    path = args[0]
    kind, nodes, start = read_story(path)
    findings = analyze(nodes, start)

    endings = sum(1 for n in nodes if is_ending(n))
    links = sum(len(v) for v in nodes.values())
    print(f"File     : {path} ({kind})")
    print(f"Passages : {len(nodes)} ({endings} endings)")
    print(f"Links    : {links}")
    print()
    if findings:
        print(f"FINDINGS ({len(findings)})")
        for tag, _, message in findings:
            print(f"  {tag:<11} {message}")
            print(f"  {'':<11} Fix: {FIXES[tag]}")
    else:
        print("OK: no orphans, no dead ends, no broken links, no traps.")

    if "--map" in sys.argv:
        print()
        print(mermaid_map(nodes, start, findings))
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
