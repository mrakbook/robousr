# Contributing

Thanks for considering a contribution to RoboUsr!

## Getting started

1. Fork and clone the repo
2. Create a venv and install deps (`pip install -r requirements.txt` if present, or see README)
3. Copy `.env.example` → `.env` and fill values
4. Import `db/schema.sql` and run the app locally (`./start_model.sh`, then `./start_bot.sh`)

## Pull requests

- Create a feature branch: `git checkout -b feat/short-title`  
- Keep changes focused and add tests if applicable  
- Ensure `black`/`flake8` or your editor's formatter keeps code tidy  
- Update docs if behavior or configuration changed  
- Fill the PR template, link related issues, and describe your testing

## Commit messages

Follow a clear style such as Conventional Commits (e.g., `feat:`, `fix:`, `docs:`).

## Code of Conduct

By participating you agree to uphold our **CODE_OF_CONDUCT.md**.
