# circuitsmngr-c
circuitsmngr device connect utility

# Installation and Configuration
```console
$ pipx install git+https://github.com/seankndy/circuitsmngr-c.git
```
Configuration example is in `config/c.json`, you can copy this to `$HOME/.config/c.json`.

# BASH Completion
circuitsmngr-c has BASH completion support.  You'll need to add something like the following to your bash env:
```shellscript
_c_complete()
{
    local cur opts

    COMPREPLY=()
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cur="${COMP_WORDS[COMP_CWORD]}"
    cur=$(echo $cur | tr '[:upper:]' '[:lower:]')

    clientop=0
    for w in "${COMP_WORDS[@]}"; do
        if [ "$w" == "--client" ] || [ "$w" == "-c" ]; then
            clientop=1
        fi
    done

    if [ "$clientop" -eq 1 ]; then
        if [ "$COMP_CWORD" -eq 3 ]; then
            opts=$(c --client "${prev}" --bash-completion service "${cur}")
        else
            opts=$(c --bash-completion client "${cur}")
        fi
    else
        opts=$(c --bash-completion network "${cur}")
    fi

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}
complete -F _c_complete c
```
