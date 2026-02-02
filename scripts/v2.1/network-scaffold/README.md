How to run it
```
chmod +x forge-the-network.sh
./forge-the-network.sh acmenet /path/to/workspace
```

Or with environment overrides for upstream URLs:
```
UPSTREAM_CORE_URL="https://github.com/beckn/protocol-specifications.git" \
UPSTREAM_DOMAIN_URL="https://github.com/beckn/DEG.git" \
UPSTREAM_CORE_REF="v2.0.0" \
UPSTREAM_DOMAIN_REF="main" \
./forge-the-network.sh acmenet
```
