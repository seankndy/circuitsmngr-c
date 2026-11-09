"""Shell completion scripts (bash, zsh) and installer with shell auto-detection."""

import os
import subprocess
import sys

SHELLS = ('bash', 'zsh')
MARKER = '# circuitsmngr-c completion'

BASH_SCRIPT = r'''# circuitsmngr-c bash completion
_c_complete()
{
    local cur prev clientop w opts
    COMPREPLY=()
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    cur=$(printf '%s' "$cur" | tr '[:upper:]' '[:lower:]')

    clientop=""
    for w in "${COMP_WORDS[@]:0:COMP_CWORD}"; do
        if [ "$clientop" = "-" ]; then
            clientop="$w"
        elif [ "$w" = "--client" ] || [ "$w" = "-c" ]; then
            clientop="-"
        fi
    done

    if [ "$prev" = "--client" ] || [ "$prev" = "-c" ]; then
        opts=$(c --complete client "$cur" 2>/dev/null) || return 0
    elif [ -n "$clientop" ] && [ "$clientop" != "-" ]; then
        opts=$(c --client "$clientop" --complete service "$cur" 2>/dev/null) || return 0
    else
        opts=$(c --complete network "$cur" 2>/dev/null) || return 0
    fi

    local IFS=$'\n'
    COMPREPLY=( $(compgen -W "$opts" -- "$cur") )
    return 0
}
complete -F _c_complete c
'''

ZSH_SCRIPT = r'''# circuitsmngr-c zsh completion
(( $+functions[compdef] )) || { autoload -Uz compinit && compinit -i }

_c() {
    local cur=${words[CURRENT]:l} prev=${words[CURRENT-1]} client="" out i
    local -a opts

    for (( i = 2; i < CURRENT - 1; i++ )); do
        [[ ${words[i]} == (-c|--client) ]] && client=${words[i+1]}
    done

    if [[ $prev == (-c|--client) ]]; then
        out=$(c --complete client "$cur" 2>/dev/null) || return 1
    elif [[ -n $client ]]; then
        out=$(c --client "$client" --complete service "$cur" 2>/dev/null) || return 1
    else
        out=$(c --complete network "$cur" 2>/dev/null) || return 1
    fi

    opts=("${(@f)out}")
    opts=(${opts:#})
    (( ${#opts} )) || return 1
    compadd -M 'm:{A-Z}={a-z}' -a opts
}
compdef _c c
'''

SCRIPTS = {'bash': BASH_SCRIPT, 'zsh': ZSH_SCRIPT}


def detect_shell():
    """Return 'bash' or 'zsh', or None if neither can be determined.

    Prefers the login shell ($SHELL), since that decides which rc file new
    terminals read; falls back to the parent process (the invoking shell).
    """
    name = os.path.basename(os.environ.get('SHELL', ''))
    if name in SHELLS:
        return name
    try:
        comm = subprocess.run(
            ['ps', '-p', str(os.getppid()), '-o', 'comm='],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        name = os.path.basename(comm).lstrip('-')
        if name in SHELLS:
            return name
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def rc_file(shell):
    home = os.path.expanduser('~')
    if shell == 'zsh':
        return os.path.join(os.environ.get('ZDOTDIR', home), '.zshrc')
    # macOS terminals start login shells, which read .bash_profile, not .bashrc
    if sys.platform == 'darwin':
        return os.path.join(home, '.bash_profile')
    return os.path.join(home, '.bashrc')


def script_path(shell):
    data_home = os.environ.get('XDG_DATA_HOME') or os.path.expanduser('~/.local/share')
    return os.path.join(data_home, 'circuitsmngr-c', 'completion.' + shell)


def install(shell=None):
    """Write the completion script and source it from the shell's rc file."""
    shell = shell or detect_shell()
    if shell not in SHELLS:
        raise Exception('could not detect shell (bash or zsh); pass it explicitly, '
                        'e.g. --install-completion zsh')

    path = script_path(shell)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as fh:
        fh.write(SCRIPTS[shell])

    rc = rc_file(shell)
    try:
        with open(rc) as fh:
            existing = fh.read()
    except FileNotFoundError:
        existing = ''

    if MARKER in existing:
        print('{} completion script updated at {} ({} already sources it)'.format(shell, path, rc))
        return

    with open(rc, 'a') as fh:
        if existing and not existing.endswith('\n'):
            fh.write('\n')
        fh.write('\n{}\n[ -f "{}" ] && . "{}"\n'.format(MARKER, path, path))

    print('{} completion installed: {} (sourced from {})'.format(shell, path, rc))
    print('Restart your shell or run: . {}'.format(rc))
