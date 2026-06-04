#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from classifier import classify, MODEL_HAIKU, MODEL_SONNET, MODEL_OPUS
from logger import log_session, get_stats, format_stats

_NAMES = {MODEL_HAIKU: 'Haiku', MODEL_SONNET: 'Sonnet', MODEL_OPUS: 'Opus'}
_MAP = {'haiku': MODEL_HAIKU, 'sonnet': MODEL_SONNET, 'opus': MODEL_OPUS}
_WORK = Path('/home/rohit-tanwar/claude-work')


def _detect_project() -> str:
    cwd = Path.cwd()
    for base in [_WORK, Path.home() / 'claude-work']:
        try:
            parts = cwd.relative_to(base).parts
            if parts:
                return parts[0]
        except ValueError:
            continue
    return cwd.name


def main():
    args = sys.argv[1:]

    if not args:
        print("Usage: cc \"your task\"")
        print("       cc --model haiku|sonnet|opus \"task\"")
        print("       cc --stats")
        sys.exit(0)

    if args[0] == '--stats':
        print(format_stats(get_stats(7)))
        return

    dry_run = '--dry-run' in args
    if dry_run:
        args = [a for a in args if a != '--dry-run']

    model_override = None
    if '--model' in args:
        idx = args.index('--model')
        if idx + 1 < len(args):
            model_override = _MAP.get(args[idx + 1].lower())
            args = args[:idx] + args[idx + 2:]

    task = ' '.join(args).strip()
    if not task:
        print("Error: no task provided.", file=sys.stderr)
        sys.exit(1)

    model = model_override or classify(task)
    project = _detect_project()
    print(f"→ {_NAMES.get(model, model)} | {project}")

    if dry_run:
        return

    log_session(model, task, project)
    os.execvp('claude', ['claude', '--model', model, task])


if __name__ == '__main__':
    main()
