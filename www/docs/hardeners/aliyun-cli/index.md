# Aliyun Cli hardener

Run `av harden aliyun-cli` to apply this hardener and `av doctor aliyun-cli` to verify it.

`av harden aliyun-cli` installs the Automic Vault signed, Hardened Runtime
Alibaba Cloud CLI Isotope and moves AccessKey and STS profile credentials into
Automic Vault custody. It configures Alibaba Cloud CLI's native External
credential provider so only the verified live `aliyun` Target can request the
credential for its exact profile.

OAuth, bearer-token, and private-key profiles are refused until their protocols
can be represented and validated without weakening the Secret Gate.
