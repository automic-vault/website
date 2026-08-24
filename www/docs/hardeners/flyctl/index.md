# flyctl hardener

Run `av harden flyctl` to apply this hardener and `av doctor flyctl` to verify it.

Uses the target executable selected by your current `PATH`, shows its exact path for confirmation, and embeds that path in a launcher stub. Then it migrates supported existing credentials into Automic Vault and runs the target through `av inject --allow-missing-keys` with those secrets. Automic Vault requests elevation only to install the launcher stub. This does not protect the target executable; anything that can replace it can read the injected credentials. Run `av scan` after hardening to find unsupported credentials or secrets written later.
