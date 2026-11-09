# circuitsmngr-c
circuitsmngr device connect utility

# Installation and Configuration
```console
$ pipx install git+https://github.com/seankndy/circuitsmngr-c.git
```
Configuration example is in `config/c.json`, you can copy this to `$HOME/.config/c.json`.

# Shell Completion (bash and zsh)
Install completion after installing the package:
```console
$ c --install-completion
```
This detects your shell (bash or zsh) from `$SHELL`, falling back to the shell you ran it from. It writes the
completion script to `~/.local/share/circuitsmngr-c/` and adds a line that sources it to `~/.zshrc`, `~/.bashrc`,
or (on macOS) `~/.bash_profile`. You can run it again safely, and you should run it again after upgrading.

To pick the shell yourself, use `c --install-completion zsh` or `c --install-completion bash`.

To manage your rc file yourself, print the script and source it however you like:
```console
$ c --completion-script zsh > ~/.zsh/c-completion.zsh
```

Install and enable completion in one step:
```console
$ pipx install git+https://github.com/seankndy/circuitsmngr-c.git && c --install-completion
```

If you previously pasted the old `_c_complete` bash function into your rc file, remove it.
The `--bash-completion` flag it uses still works as an alias of `--complete`.
