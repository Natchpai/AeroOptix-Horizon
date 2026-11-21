#!/usr/bin/env python3
"""Claude Code PreToolUse guard for KiCad files, PDF reads and Git commands.

Rules live in protect.json next to this file. Three rule sets, each checked
deny > ask > allow, the same order as Claude Code's own permissions:
- top-level `deny`/`ask`/`allow`: paths that Edit, Write and shell commands
  would change;
- `pdf`: PDFs that Read and shell commands would read. A PDF that matches no
  glob gets `ask`;
- `git`: named checks on git and gh commands, with flags in any order.
deny -> blocked; ask -> the user is prompted; no match -> normal permissions.

Advisory defense-in-depth; not an OS sandbox. Shell analysis is token-based.
It follows chains, pipes, background jobs, subshells, $(...), shell keywords
(if/then/do/...), wrappers and heredocs fed to a shell or interpreter. It
cannot see paths or commands built at runtime, Git aliases or script files.
"""
import json
import os
import posixpath
import re
import shlex
import subprocess
import sys

RANK = {'allow': 0, 'ask': 1, 'deny': 2}
ORDER = ('deny', 'ask', 'allow')
FILE_TOOLS = ('Edit', 'Write', 'MultiEdit', 'NotebookEdit')
READ_TOOLS = ('Read',)
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
# words that run the next word as the command
WRAPPERS = {'env', 'command', 'time', 'nohup', 'exec', 'sudo', 'xargs', '&', 'call',
            'timeout', 'nice'}
# wrapper options that take a value (the value is not the command)
WRAPPER_ARG = {
    'env': {'-u', '--unset', '-C', '--chdir'},
    'sudo': {'-u', '--user', '-g', '--group', '-h', '--host', '-p', '--prompt', '-C',
             '--close-from', '-D', '--chdir'},
    'xargs': {'-I', '-n', '--max-args', '-P', '--max-procs', '-L', '--max-lines', '-d',
              '--delimiter', '-E', '-s', '--max-chars', '-a', '--arg-file'},
    'timeout': {'-s', '--signal', '-k', '--kill-after'},
    'nice': {'-n', '--adjustment'},
}
# shell words that come before a command (if git push ...; then git push ...)
KEYWORDS = {'if', 'then', 'do', 'else', 'elif', 'while', 'until', '!', '{'}
# shells whose -c / -Command string is itself a command
SUBSHELLS = {'bash', 'sh', 'zsh', 'dash', 'powershell', 'pwsh', 'cmd'}
SUBSHELL_FLAGS = {'-c', '-lc', '-ic', '-command', '/c', '/k'}
CD = {'cd', 'pushd', 'set-location', 'sl', 'chdir'}
# <<EOF and <<-'EOF', not the <<< here-string
HEREDOC = re.compile(r"(?<!<)<<(?!<)-?\s*(['\"]?)([A-Za-z_][\w-]*)\1")
HEREDOC_TAG = re.compile(r'__heredoc(\d+)__')

# PDFs: these commands list, move or print text, and never read PDF content
PDF_NO_READ = {'ls', 'dir', 'gci', 'get-childitem', 'find', 'stat', 'du', 'mkdir',
               'echo', 'printf', 'gh'}
PDF_GIT_READ = {'show', 'cat-file'}          # other git subcommands do not print content
PDF_RE = re.compile(r"""[^\s'"`()=,;<>|]+\.pdf(?![\w.])""", re.IGNORECASE)

# Git: the named checks the "git" block may list
GIT_CHECKS = {
    'push-protected': 'pushes to a protected branch ({branches}) or pushes every branch',
    'force-push': 'force-pushes (--force, -f or a +refspec)',
    'force-with-lease': 'force-pushes with --force-with-lease',
    'push-delete': 'deletes a remote branch or tag',
    'push-tags': 'pushes tags',
    'reset-hard': 'runs git reset --hard',
    'clean-force': 'runs git clean with -f',
    'branch-delete': 'deletes a local branch',
    'branch-rename': 'renames a local branch',
    'tag': 'creates, moves or deletes a tag',
    'rebase': 'rebases (git rebase or git pull --rebase)',
    'commit-amend': 'amends a commit',
    'gh-pr-merge': 'merges a pull request',
    'gh-release': 'creates, edits or deletes a GitHub release',
}
GIT_GLOBAL_ARG = {'-C', '-c', '--git-dir', '--work-tree', '--namespace', '--config-env'}
PUSH_ARG = {'-o', '--push-option', '--repo', '--receive-pack', '--exec'}
PUSH_NO_HEAD = {'--tags', '--all', '--mirror', '--branches', '--delete'}
GH_GLOBAL_ARG = {'-R', '--repo', '--hostname'}
TAG_ARG = {'--contains', '--no-contains', '--merged', '--no-merged', '--points-at',
           '--sort', '--format', '--column'}


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


def compile_set(block):
    return {k: [(g, glob_re(g)) for g in block.get(k, [])] for k in RANK}


def load_rules(path=None):
    """Compile protect.json. Unknown git check names are ignored here;
    tools/check_permissions.py reports them."""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'protect.json')
    with open(path, encoding='utf-8') as f:
        cfg = json.load(f)
    rules = compile_set(cfg)
    rules['pdf'] = compile_set(cfg.get('pdf', {}))
    git = cfg.get('git', {})
    rules['git'] = {'deny': set(git.get('deny', [])), 'ask': set(git.get('ask', [])),
                    'branches': {b.lower() for b in git.get('protected_branches',
                                                            ['main', 'master'])}}
    return rules


def classify(path, rules, default=None):
    """Return (level, glob): deny > ask > allow, else (default, None)."""
    if not isinstance(path, str) or not path.strip():
        return None, None
    # resolve ".." so an allow glob (for example scratchpad/**) cannot hide a
    # protected file behind a "scratchpad/../" segment
    p = posixpath.normpath(path.strip().strip('"\'').replace('\\', '/')).lower()
    for level in ORDER:
        for g, rx in rules[level]:
            if rx.match(p) or rx.match(p + '/'):
                return level, g
    return default, None


# ---------------------------------------------------------------- shell parsing

def strip_heredocs(command):
    """Move heredoc bodies out of the command text.

    Each heredoc operator becomes a word __heredocN__. Return (text, bodies).
    segments() parses a body only when it feeds a shell or an interpreter, so
    commit messages and similar text are not commands."""
    out, bodies, pending = [], [], []

    def tag(m):
        pending.append((len(bodies), m.group(2)))
        bodies.append([])
        return f' __heredoc{len(bodies) - 1}__ '

    for ln in command.split('\n'):
        if pending:
            idx, end = pending[0]
            if ln.strip() == end:
                pending.pop(0)
            else:
                bodies[idx].append(ln)
            continue
        out.append(HEREDOC.sub(tag, ln))
    return '\n'.join(out), ['\n'.join(b) for b in bodies]


def split_segments(command):
    """Split on && || ; | & newlines ( ) ` and a standalone { or }, outside quotes.

    A & that is part of a redirect (2>&1, &>file) does not split; nor do the
    braces of ${VAR}, {} or {a,b}."""
    segs, cur, quote, i, n = [], '', None, 0, len(command)
    while i < n:
        c = command[i]
        prev = command[i - 1] if i else ' '
        nxt = command[i + 1] if i + 1 < n else ' '
        if quote:
            cur += c
            if c == quote:
                quote = None
            i += 1
            continue
        if c in '"\'':
            quote = c
            cur += c
        elif command.startswith(('&&', '||'), i):
            segs.append(cur)
            cur = ''
            i += 1
        elif (c in ';|\n()`'
              or (c == '&' and prev not in ('<', '>') and nxt != '>')
              or (c in '{}' and prev.isspace() and (nxt.isspace() or nxt == ';'))):
            segs.append(cur)
            cur = ''
        else:
            cur += c
        i += 1
    segs.append(cur)
    return [s for s in (x.strip() for x in segs) if s]


def tokens(seg):
    try:
        return shlex.split(seg)
    except ValueError:
        return [t.strip('"\'') for t in seg.split()]


def base(tok):
    name = posixpath.basename(tok.replace('\\', '/')).lower()
    return name[:-4] if name.endswith('.exe') else name


def unwrap(toks):
    """Drop leading shell keywords, env assignments and wrapper words with
    their options (if, then, do, !, env -u X, sudo, xargs -n 1, timeout 60, &)."""
    i, wrapper = 0, None
    while i < len(toks):
        t, b = toks[i], base(toks[i])
        if t in KEYWORDS or re.match(r'^[A-Za-z_][A-Za-z0-9_]*=', t):
            wrapper = None
        elif b in WRAPPERS:
            wrapper = b
        elif wrapper and t.startswith('-'):
            if t in WRAPPER_ARG.get(wrapper, ()):
                i += 1                               # skip the option's value
        elif wrapper == 'timeout' and re.match(r'^\d+(\.\d+)?[smhd]?$', t):
            wrapper = None                           # the duration; the command follows
        else:
            break
        i += 1
    return toks[i:]


def segments(command, depth=0, bodies=None):
    """Yield (segment text, tokens) for each simple command, entering bash -c
    strings and heredocs fed to a shell. A heredoc fed to an interpreter is
    added to that segment's text, so the write and PDF scans see it."""
    if bodies is None:
        if depth == 0:
            command = command.replace('\\', '/')
        command, bodies = strip_heredocs(command)
    for seg in split_segments(command):
        toks = unwrap(tokens(seg))
        if not toks:
            continue
        cmd = base(toks[0])
        fed = [bodies[int(k)] for k in HEREDOC_TAG.findall(seg) if int(k) < len(bodies)]
        if fed and cmd in INTERPRETERS:
            seg = '\n'.join([seg, *fed])
        yield seg, toks
        if depth < 3 and cmd in SUBSHELLS:
            for i, t in enumerate(toks[:-1]):
                if t.lower() in SUBSHELL_FLAGS:
                    yield from segments(' '.join(toks[i + 1:]), depth + 1, bodies)
                    break
            else:
                for body in fed:
                    yield from segments(body, depth + 1)


def shell_targets(command):
    """Paths a shell command would write to (best effort)."""
    targets = []
    for seg, toks in segments(command):
        # redirections: > file, >> file, >file
        for i, t in enumerate(toks):
            m = re.match(r'^\d?>>?(.*)$', t)
            if m:
                targets.append(m.group(1) or (toks[i + 1] if i + 1 < len(toks) else ''))
        cmd = base(toks[0])
        args = [t for t in toks[1:] if not t.startswith('-')]
        if cmd in WRITE_ALL:
            targets += args
        elif cmd in WRITE_LAST and args:
            targets.append(args[-1])
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


def shell_pdfs(command):
    """PDF paths a shell command may read: any mention, except in listing commands."""
    found = []
    for seg, toks in segments(command):
        cmd = base(toks[0])
        if cmd in PDF_NO_READ:
            continue
        if cmd == 'git':
            sub = git_argv(toks[1:])
            if not sub or sub[0] not in PDF_GIT_READ:
                continue
        found += PDF_RE.findall(seg)
    return found


# ---------------------------------------------------------------- git and gh

def git_argv(args):
    """Skip git global options (-C dir, -c k=v, --no-pager); return [sub, ...]."""
    i = 0
    while i < len(args) and args[i].startswith('-'):
        i += 2 if args[i] in GIT_GLOBAL_ARG else 1
    return args[i:]


def git_dir(args, cwd):
    """The directory a git call runs in: cwd plus any -C."""
    d, i = cwd, 0
    while i < len(args) and args[i].startswith('-'):
        if args[i] == '-C' and i + 1 < len(args):
            d = os.path.join(d or '', args[i + 1])
        i += 2 if args[i] in GIT_GLOBAL_ARG else 1
    return d


def parse_opts(args, with_arg=()):
    """Return (long flags, short flag letters, positionals)."""
    longs, shorts, pos, i = [], set(), [], 0
    while i < len(args):
        a = args[i]
        if a == '--':
            pos += args[i + 1:]
            break
        if a in with_arg:
            i += 2
            continue
        if a.startswith('--'):
            longs.append(a.split('=', 1)[0])
        elif re.match(r'^-[A-Za-z]+$', a):
            shorts.update(a[1:])
        elif not a.startswith('-'):
            pos.append(a)
        i += 1
    return longs, shorts, pos


def current_branch(cwd):
    try:
        out = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=cwd or None,
                             capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else None


def push_hits(args, cwd, branches):
    longs, shorts, pos = parse_opts(args, PUSH_ARG)
    hits = []
    if '--force' in longs or 'f' in shorts:
        hits.append('force-push')
    elif '--force-with-lease' in longs:
        hits.append('force-with-lease')
    if '--delete' in longs or 'd' in shorts:
        hits.append('push-delete')
    if '--tags' in longs or '--follow-tags' in longs:
        hits.append('push-tags')
    if {'--all', '--mirror', '--branches'} & set(longs):
        hits.append('push-protected')
    refspecs = pos[1:]
    if not refspecs and not (PUSH_NO_HEAD & set(longs) or 'd' in shorts):
        refspecs = ['HEAD']                          # git push [remote]: the current branch
    for r in refspecs:
        if r.startswith('+'):
            hits.append('force-push')
            r = r[1:]
        if r == ':':                                 # "matching" pushes every common branch
            hits.append('push-protected')
            continue
        src, colon, dst = r.partition(':')
        if colon and not src:
            hits.append('push-delete')
        if src.startswith('refs/tags/') or dst.startswith('refs/tags/'):
            hits.append('push-tags')
        dest = dst or src
        if dest in ('HEAD', '@'):
            dest = current_branch(cwd)
            if dest is None:
                hits.append('push-unknown')
                continue
        if re.sub(r'^refs/heads/', '', dest).lower() in branches:
            hits.append('push-protected')
    return hits


def git_hits(toks, cwd, branches):
    """Named checks that one git or gh command trips."""
    cmd = base(toks[0])
    if cmd == 'gh':
        args, i = toks[1:], 0
        while i < len(args) and args[i].startswith('-'):
            i += 2 if args[i] in GH_GLOBAL_ARG else 1
        args = args[i:]
        if args[:2] == ['pr', 'merge']:
            return ['gh-pr-merge']
        if args[:1] == ['api'] and re.search(r'/pulls/[^/\s]+/merge\b', ' '.join(args)):
            return ['gh-pr-merge']
        if args[:1] == ['release'] and len(args) > 1 and args[1] not in ('list', 'view', 'download'):
            return ['gh-release']
        return []
    if cmd != 'git':
        return []
    argv = git_argv(toks[1:])
    if not argv:
        return []
    sub, args = argv[0], argv[1:]
    longs, shorts, pos = parse_opts(args)
    if sub == 'push':
        return push_hits(args, git_dir(toks[1:], cwd), branches)
    if sub == 'reset' and '--hard' in longs:
        return ['reset-hard']
    if sub == 'clean' and ('--force' in longs or 'f' in shorts):
        return ['clean-force']
    if sub == 'branch':
        hits = []
        if '--delete' in longs or shorts & {'d', 'D'}:
            hits.append('branch-delete')
        if '--move' in longs or shorts & {'m', 'M'}:
            hits.append('branch-rename')
        return hits
    if sub == 'tag':
        longs, shorts, pos = parse_opts(args, TAG_ARG)
        listing = '--list' in longs or 'l' in shorts
        writes = (shorts & {'a', 's', 'u', 'f', 'd', 'm', 'F', 'e'}) or (set(longs) & {
            '--delete', '--annotate', '--sign', '--local-user', '--force', '--message',
            '--file', '--edit'})
        return [] if listing or not (pos or writes) else ['tag']
    if sub == 'rebase':
        return ['rebase']
    if sub == 'pull':
        # the last of -r, --rebase[=mode] and --no-rebase wins, as in git
        last = [a for a in args if a in ('-r', '--rebase', '--no-rebase')
                or a.startswith('--rebase=') or re.match(r'^-[A-Za-z]*r[A-Za-z]*$', a)]
        if last and last[-1] != '--no-rebase' and \
                last[-1].split('=', 1)[-1].lower() not in ('false', 'no', 'off', '0'):
            return ['rebase']
    if sub == 'commit' and '--amend' in longs:
        return ['commit-amend']
    return []


def git_decisions(command, cwd, git_rules):
    """[(level, check, segment)] for the git and gh commands in a shell command."""
    out = []
    for seg, toks in segments(command):
        if base(toks[0]) in CD and len(toks) > 1:
            cwd = os.path.join(cwd or '', toks[1])
            continue
        for hit in git_hits(toks, cwd, git_rules['branches']):
            if hit == 'push-unknown':                # treat like a protected push, one level down
                if 'push-protected' in git_rules['deny'] | git_rules['ask']:
                    out.append(('ask', hit, seg))
                continue
            for level in ('deny', 'ask'):
                if hit in git_rules[level]:
                    out.append((level, hit, seg))
                    break
    return out


# ---------------------------------------------------------------- decision

def reason_for(kind, level, item, rule, branches):
    how = 'Blocked' if level == 'deny' else 'Needs your approval'
    if kind == 'git':
        if rule == 'push-unknown':
            what = 'pushes the current branch, which the guard could not read'
            rule = 'push-protected'
        else:
            what = GIT_CHECKS[rule].format(branches=', '.join(sorted(branches)))
        return (f'{how}: "{item}" {what} (git check "{rule}" in .claude/hooks/protect.json). '
                'Run it only after approval of this exact Git action in chat.')
    if kind == 'pdf':
        rule_txt = f'{level} rule "{rule}"' if rule else 'no rule, so the PDF default (ask)'
        tail = (' A datasheet PDF is read only after approval of that file in chat, '
                'when NotebookLM cannot answer (rules/pdf.md).') if level == 'ask' else ''
        return (f'{how}: "{item}" matches {rule_txt} in the "pdf" block of '
                f'.claude/hooks/protect.json.{tail}')
    return (f'{how}: "{item}" matches {level} rule "{rule}" in .claude/hooks/protect.json. '
            'Change that file to adjust the rule.')


def check(event, rules):
    tool = event.get('tool_name', '')
    args = event.get('tool_input')
    if not isinstance(args, dict):
        return 'deny', 'Invalid tool input', ''
    found = []                                   # (level, kind, item, rule)
    if tool in FILE_TOOLS:
        for c in (args.get(k) for k in ('file_path', 'path', 'filename', 'notebook_path')):
            found.append((*classify(c, rules), 'edit', c))
    elif tool in READ_TOOLS:
        c = args.get('file_path')
        if isinstance(c, str) and c.strip().strip('"\'').lower().endswith('.pdf'):
            found.append((*classify(c, rules['pdf'], default='ask'), 'pdf', c))
    elif tool in SHELLS and isinstance(args.get('command'), str):
        command = args['command']
        for c in shell_targets(command):
            found.append((*classify(c, rules), 'edit', c))
        for c in shell_pdfs(command):
            found.append((*classify(c, rules['pdf'], default='ask'), 'pdf', c))
        for level, rule, seg in git_decisions(command, event.get('cwd'), rules['git']):
            found.append((level, rule, 'git', seg))
    else:
        return None
    worst = None
    for f in found:
        if f[0] in ('deny', 'ask') and (worst is None or RANK[f[0]] > RANK[worst[0]]):
            worst = f
    if worst is None:
        return None
    level, rule, kind, item = worst
    return level, reason_for(kind, level, item, rule, rules['git']['branches']), ''


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
