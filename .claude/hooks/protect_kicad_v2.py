#!/usr/bin/env python3
"""Claude Code PreToolUse guard for native KiCad files (v2).

Rules live in protect.json next to this file (allow > deny > ask).
deny -> blocked; ask -> the user is prompted; no match -> normal permissions.
Advisory defense-in-depth; not an OS sandbox. Bash/PowerShell analysis is
token-based and cannot see paths built at runtime or relative to a `cd`.
"""
import json
import os
import posixpath
import re
import shlex
import sys

RANK = {'allow': 0, 'ask': 1, 'deny': 2}
FILE_TOOLS = ('Edit', 'Write', 'MultiEdit', 'NotebookEdit')
SHELLS = ('Bash', 'PowerShell')
# commands whose every path argument is modified
WRITE_ALL = {'rm', 'mv', 'touch', 'truncate', 'tee', 'patch', 'rmdir', 'unlink',
             'remove-item', 'move-item', 'rename-item', 'set-content',
             'add-content', 'clear-content', 'out-file', 'new-item',
             # PowerShell aliases of the cmdlets above
             'del', 'erase', 'ri', 'rd', 'move', 'mi', 'ren', 'rni', 'sc', 'ac',
             'clc', 'ni'}
WRITE_LAST = {'cp', 'install', 'copy-item', 'ln', 'copy', 'cpi'}  # only the destination
INPLACE = {'sed', 'perl'}                              # only with -i
GIT_WRITE = {'checkout', 'restore', 'reset', 'clean', 'apply', 'rm', 'mv'}
OUTPUT_FLAGS = {'-o', '--output'}                      # e.g. kicad-cli ... -o PATH
INTERPRETERS = {'python', 'python3', 'py', 'node', 'powershell', 'pwsh', 'perl'}
WRITE_HINT = re.compile(r"(?i)open\([^)]*['\"][wax]|write|rmtree|unlink|remove|"
                        r"set-content|out-file|copy|rename|move")
PS_COPY = {'copy-item', 'copy', 'cpi'}                # PowerShell: -Destination may come first
SPLIT = re.compile(r'&&|\|\||[;|\n]|(?<![<>])&')       # a lone & also separates commands
# redirection target, with or without a space: > f, >> f, >f, 2>f, echo hi>f (not 2>&1)
REDIRECT = re.compile(r'''(?<![<>&])\d?>>?(?!&)\s*("[^"]*"|'[^']*'|[^\s<>&|;"']+)''')


def glob_re(g):
    out, i = '', 0
    g = g.replace('\\', '/').lower()
    while i < len(g):
        if g.startswith('**/', i):
            out += '(?:.*/)?'
            i += 3
        elif g.startswith('**', i):
            out += '.*'
            i += 2
        elif g[i] == '*':
            out += '[^/]*'
            i += 1
        elif g[i] == '?':
            out += '[^/]'
            i += 1
        else:
            out += re.escape(g[i])
            i += 1
    return re.compile('^' + out + '$')


def load_rules():
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'protect.json'), encoding='utf-8') as f:
        cfg = json.load(f)
    # optional extra shell commands, so new aliases need no code change
    WRITE_ALL.update(c.lower() for c in cfg.get('write_all') or [])
    WRITE_LAST.update(c.lower() for c in cfg.get('write_last') or [])
    return {k: [(g, glob_re(g)) for g in cfg.get(k) or []] for k in RANK}


def classify(path, rules):
    """Return (level, glob) for a path; level is None when nothing matches."""
    if not isinstance(path, str) or not path.strip():
        return None, None
    # resolve ".." so an allow glob (for example scratchpad/**) cannot hide a
    # protected file behind a "scratchpad/../" segment; "D:foo" (drive-relative)
    # is read as "D:/foo" so the directory part is still matched
    p = path.strip().strip('"\'').replace('\\', '/')
    p = posixpath.normpath(re.sub(r'^([A-Za-z]):(?=[^/])', r'\1:/', p)).lower()
    for level in ('allow', 'deny', 'ask'):
        for g, rx in rules[level]:
            if rx.match(p) or rx.match(p + '/'):
                return level, g
    return None, None


def shell_targets(command):
    """Paths a shell command would write to (best effort)."""
    targets = []
    for seg in SPLIT.split(command.replace('\\', '/')):
        try:
            toks = shlex.split(seg)
        except ValueError:
            toks = seg.split()
        targets += [m.group(1).strip('"\'') for m in REDIRECT.finditer(seg)]
        if not toks:
            continue
        cmd = os.path.basename(toks[0]).lower()
        cmd = cmd[:-4] if cmd.endswith('.exe') else cmd
        args = [t for t in toks[1:] if not t.startswith('-')]
        if cmd in WRITE_ALL:
            targets += args
        elif cmd in WRITE_LAST and args:
            targets.append(args[-1])
            if cmd in PS_COPY:                            # Copy-Item -Destination X -Path Y
                targets += [toks[i + 1] for i, t in enumerate(toks[:-1])
                            if t.lower().startswith('-d')]
        elif cmd in INPLACE and any(t.startswith('-i') for t in toks[1:]):
            targets += args
        elif cmd == 'git' and args and args[0] in GIT_WRITE:
            targets += args[1:]
        for i, t in enumerate(toks[:-1]):
            if t in OUTPUT_FLAGS:
                targets.append(toks[i + 1])
        if cmd in INTERPRETERS and WRITE_HINT.search(seg):
            targets += [t for t in toks[1:]]          # path-like strings inside
            targets += re.findall(r"[\w./:${}~-]+\.[\w]+|[\w./${}~-]*/[\w./${}~-]*", seg)
    return targets


def check(event, rules):
    tool = event.get('tool_name', '')
    args = event.get('tool_input')
    if not isinstance(args, dict):
        return 'deny', 'Invalid tool input', ''
    if tool in FILE_TOOLS:
        cands = [args.get(k) for k in ('file_path', 'path', 'filename', 'notebook_path')]
    elif tool in SHELLS and isinstance(args.get('command'), str):
        cands = shell_targets(args['command'])
    else:
        return None
    worst = (None, None, None)
    for c in cands:
        level, glob = classify(c, rules)
        if level in ('deny', 'ask') and (worst[0] is None or RANK[level] > RANK[worst[0]]):
            worst = (level, glob, c)
    if worst[0] is None:
        return None
    level, glob, path = worst
    how = ('Blocked' if level == 'deny' else 'Needs your approval')
    return level, (f'{how}: "{path}" matches {level} rule "{glob}" in '
                   '.claude/hooks/protect.json. Change that file to adjust the rule.'), ''


def main():
    try:
        event = json.load(sys.stdin)
        result = check(event, load_rules())
    except Exception as e:                      # fail closed, say why
        result = ('deny', f'protect_kicad_v2 error ({type(e).__name__}: {e}); '
                          'blocking to be safe.', '')
    if result:
        level, reason, _ = result
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': level,
            'permissionDecisionReason': reason}}))


if __name__ == '__main__':
    main()
