# Echoist

This is a simple demo service. It accepts TCP connections and echoes what they sent.

## What it does?

1. Binds port 7
2. Drops privileges via fork - switches to _daemon_ user and group
3. Runs until SIGTERM/SIGKILL is received
