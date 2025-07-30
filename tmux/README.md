# tmux usage

Use the `tmux` terminal multiplexer to run interactive sessions which persist in the background. This is particularly useful when connected over SSH to avoid interrupting active tasks.

## CLI

#### List sessions

    tmux ls

#### Attach to specific session based on listed number

    tmux a -t 0

#### Attach to most recent session

    tmux a


## Active use

#### Detach from active session (leaving it running)

1. Input `Ctrl+B`
2. Input `d`

#### Split the active window vertically

This results in two columns, with the left one losing focus.

1. Input `Ctrl+B`
2. Input `%`

#### Split the active window horizontally

This results in two rows, with the top one losing focus.

1. Input `Ctrl+B`
2. Input `"`

## Configuration

#### Override 2000-line history limit

    echo 'set -g history-limit 65535' >> ~/.tmux.conf

#### Reload config in active sessions

1. Input `Ctrl+B`
2. Type `:`
3. Type `source ~/.tmux.conf`
4. Input `Enter`
