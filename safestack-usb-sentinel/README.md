# SafeStack USB Sentinel
Hashes files on a mounted USB or staging directory before opening them. It never auto-executes files.

The CLI emits a JSON object mapping relative filenames to SHA-256 digests. Names are JSON-escaped with ASCII output, so newlines and terminal controls cannot forge records. Parse the output as JSON; it is not a checksum-list format. The Python `scan` API retains the original filename keys.
