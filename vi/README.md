# vi

Text editor

# Common commands

Quit without saving: `:q!`

Write changes to disk and quit: `:wq`

# Fixing paste formatting

https://unix.stackexchange.com/questions/682922/pasting-text-to-vi-adds-pound

    :set paste
    < paste the text >
    :set nopaste
