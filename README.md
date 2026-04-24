# patchwork-env

> A CLI tool to diff and reconcile `.env` files across multiple deployment environments.

---

## Installation

```bash
pip install patchwork-env
```

Or install from source:

```bash
git clone https://github.com/yourname/patchwork-env.git
cd patchwork-env && pip install -e .
```

---

## Usage

Compare `.env` files across environments to find missing or conflicting keys:

```bash
# Diff two environment files
patchwork-env diff .env.staging .env.production

# Reconcile and generate a merged output
patchwork-env reconcile .env.development .env.production --output .env.resolved

# Check all environments against a base template
patchwork-env audit .env.example --check .env.staging .env.production .env.development
```

**Example output:**

```
[MISSING in production]  DATABASE_POOL_SIZE
[MISSING in staging]     SENTRY_DSN
[CONFLICT]               LOG_LEVEL  staging=debug | production=error
```

---

## Commands

| Command       | Description                                      |
|---------------|--------------------------------------------------|
| `diff`        | Show key differences between two `.env` files    |
| `reconcile`   | Merge two files, resolving or flagging conflicts |
| `audit`       | Validate multiple envs against a base template   |

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

[MIT](LICENSE)