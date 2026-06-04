import re

MODEL_HAIKU = 'claude-haiku-4-5-20251001'
MODEL_SONNET = 'claude-sonnet-4-6'
MODEL_OPUS = 'claude-opus-4-8'

# Multi-word phrases use substring match; single words use whole-word match.
_OPUS = [
    'architect', 'security audit', 'full assessment',
    'from scratch', 'comprehensive', 'complex strategy',
    'full incident', 'complete audit',
]

_HAIKU = [
    'check', 'read', 'show', 'list', 'grep', 'find', 'verify',
    'status', 'view', 'ping', 'test', 'ssh', 'cat', 'look',
    'display', 'get', 'fetch', 'confirm', 'inspect',
    'scan', 'monitor', 'watch', 'tail', 'head', 'count',
    'what is', 'how many',
]

_SONNET = [
    'write', 'fix', 'plan', 'report', 'analyze', 'analyse', 'build',
    'implement', 'configure', 'debug', 'generate', 'update', 'add',
    'investigate', 'rca', 'create', 'optimize', 'improve', 'setup',
    'install', 'deploy', 'refactor', 'explain', 'help',
]


def _match(keywords: list, text: str, words: set) -> bool:
    for kw in keywords:
        if ' ' in kw:
            if kw in text:
                return True
        elif kw in words:
            return True
    return False


def classify(task: str) -> str:
    """Return the Claude model ID best suited for this task description."""
    t = task.lower()
    words = set(re.findall(r'\b\w+\b', t))
    if _match(_OPUS, t, words):
        return MODEL_OPUS
    if _match(_HAIKU, t, words):
        return MODEL_HAIKU
    if _match(_SONNET, t, words):
        return MODEL_SONNET
    return MODEL_SONNET
