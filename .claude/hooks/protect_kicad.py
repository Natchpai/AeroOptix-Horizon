#!/usr/bin/env python3
"""Claude Code PreToolUse guard for native KiCad design files.

Advisory defense-in-depth; not an OS filesystem sandbox.
"""
import json
import re
import sys

PROTECTED_EXTENSIONS = (
    '.kicad_sch', '.kicad_pcb', '.kicad_pro', '.kicad_sym',
    '.kicad_mod', '.kicad_wks', '.step', '.stp', '.wrl',
)
# Project convention: any file within Library/ is protected.
LIBRARY_SEGMENT = re.compile(r'(^|/)library(/|$)', re.I)
PATHISH = re.compile(r'(?i)(?:\.kicad_(?:sch|pcb|pro|sym|mod|wks)|\.step\b|\.stp\b|\.wrl\b|(?:^|[\\/]|\s)library[\\/])')
MUTATING = re.compile(
    r'(?i)\b(?:rm|mv|cp|sed|perl|tee|truncate|touch|install|patch|'
    r'git\s+(?:checkout|restore|reset|clean|apply)|'
    r'powershell|pwsh|'
    r'set-content|add-content|clear-content|remove-item|move-item|copy-item|'
    r'out-file|new-item|rename-item|writealltext|writeallbytes)\b|>>?|\|\s*tee\b'
)

def protected(path):
    if not isinstance(path, str):
        return False
    norm = path.strip().strip('"\'').replace('\\', '/').lower()
    return norm.endswith(PROTECTED_EXTENSIONS) or bool(LIBRARY_SEGMENT.search(norm))

def check(event):
    tool = event.get('tool_name', '')
    args = event.get('tool_input') or {}
    if not isinstance(args, dict):
        return 'Invalid tool input'
    if tool in ('Edit', 'Write', 'MultiEdit'):
        for field in ('file_path', 'path', 'filename'):
            if protected(args.get(field)):
                return 'Native KiCad or Library file modification blocked; propose changes instead.'
    if tool in ('Bash', 'PowerShell'):
        command = args.get('command', '')
        if isinstance(command, str) and PATHISH.search(command) and MUTATING.search(command):
            return 'Potential shell modification of KiCad/Library files blocked (heuristic).'
    return None

def main():
    try:
        event = json.load(sys.stdin)
        reason = check(event)
    except (ValueError, TypeError, AttributeError):
        reason = 'Malformed hook input; blocking tool call.'
    if reason:
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'deny',
            'permissionDecisionReason': reason
        }}))

if __name__ == '__main__':
    main()
