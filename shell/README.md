# shell

Bash/shell/terminal use.

## Paste arbitrary data into a file

Sometimes, it is more convenient to avoid an editor due to the many annoyances associated with copy-paste (particularly when connecting from Windows or interfaces like Apache Guacamole).

1. Run `cat > filename`

2. Paste into the terminal

3. Press `Ctrl + C`

## Retry command automatically on failure

Use `bash` to run a command with automatic restart on failure (be careful, might be worth adding a sleep!):

    bash -c 'function retry { command-to-repeatedly-retry-goes-here || (retry) }; retry'
