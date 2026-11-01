# SafeStack Vault
Encrypted JSON secrets using Fernet. Never commit key or vault files; use an OS keychain for production.

Use `python safestack-vault/vault.py put VAULT KEY NAME` to enter a secret at a non-echoing terminal prompt. The former plaintext `VALUE` argument is no longer accepted.

For automation, use `python safestack-vault/vault.py put VAULT KEY NAME --stdin` and supply the secret through a protected input stream. Stdin is stored exactly, including empty input and trailing newlines; do not put secret literals in shell commands. The Python `put` API and existing vault format are unchanged.
