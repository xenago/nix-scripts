# tmux usage

Override 2000-line history limit:

`echo "set -g history-limit 65535" >> ~/.tmux.conf`

To reload config in active windows:

1. Input `Ctrl+B`
2. Type `:`
3. Type `source ~/.tmux.conf`
4. Input `Enter`

