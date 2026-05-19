# jug-eared

**jug-eared** is the routing and registry service of the [SecuBot-UdeA](https://github.com/SecuBot-UdeA) ecosystem. Its sole responsibility is knowing which Secubot and Discord bot instance belongs to each team, and routing messages to the correct destination.

## Role in the ecosystem

```
Parser ──► jug-eared ──► Secubot (team X)
                    └──► Discord bot (team X)

Discord bot ──► jug-eared ──► Parser
Parser      ──► jug-eared ──► Secubot (team X)
Secubot     ──► jug-eared ──► Discord bot (team X)
```

jug-eared does not contain business logic. It does not verify alerts, calculate points, or communicate with external sources. It only routes.

## Responsibilities

- Maintain a registry of teams and their associated service instances (Secubot endpoint, Discord bot endpoint)
- Route incoming messages to the correct team's services
- Provide a simple API for service registration and deregistration

## Out of scope

- Alert normalization → that is [parser](https://github.com/SecuBot-UdeA/parser)
- Gamification logic → that is [secubot](https://github.com/SecuBot-UdeA/secubot)
- User-facing notifications → that is [discord](https://github.com/SecuBot-UdeA/discord)

## Tech stack

- **Language:** Python 3.11+
- **Framework:** FastAPI
- **Package manager:** pip / virtualenv

## Getting started

```bash
git clone https://github.com/SecuBot-UdeA/jug-eared.git
cd jug-eared
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `PORT` | Port to run the service on (default: `8000`) |

Copy `.env.example` to `.env` and fill in your values.

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

## License

[MIT](LICENSE)
