# jug-eared

**jug-eared** is the routing and registry service of the [SecuBot-UdeA](https://github.com/SecuBot-UdeA) ecosystem. Its sole responsibility is knowing which team owns each repository, routing normalized alerts to Secubot, and sending notifications to the Discord service.

## Role in the ecosystem

```
Parser ──► jug-eared ──► Secubot (full alert + team_id)
                    └──► Discord service (notification)
```

jug-eared does not contain business logic. It does not verify alerts, calculate points, or communicate with external sources. It only routes.

## Responsibilities

- Maintain a registry of teams and their associated repositories
- Resolve which team owns an alert based on the `alert_id`
- Route incoming alerts to Secubot with team context
- Send alert notifications to the Discord service

## Out of scope

- Alert normalization → [parser-dependabot](https://github.com/SecuBot-UdeA/parser-dependabot)
- Gamification logic → Secubot
- User-facing Discord messages → Discord service

## Tech stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Package manager:** uv or pip

## Getting started

```bash
git clone https://github.com/SecuBot-UdeA/jug-eared.git
cd jug-eared

# with uv
uv venv && source .venv/bin/activate
uv pip install .

# or with pip
python -m venv .venv && source .venv/bin/activate
pip install .

# run
cp .env.example .env  # fill in your values
uvicorn app.main:app --reload
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `SECUBOT_URL` | Secubot endpoint to forward full alerts |
| `DISCORD_URL` | Discord service endpoint to send notifications |

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)