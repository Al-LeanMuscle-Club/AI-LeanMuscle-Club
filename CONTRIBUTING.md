# Contributing to AI Lean Muscle Club

We are a community of AI researchers making room for movement and life alongside research. You can keep a daily journal, exchange experiences, or simply reply to someone. No fitness background or publication threshold is required.

## Check in and follow the weekly board

Create one [daily check-in Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=daily-checkin.yml), choose its time zone, and keep using it across weeks. Select **Yes** for **Public leaderboard** only if you want your username and counts on the board; the default is No.

Each day, comment on your own Issue:

```text
/checkin 2026-10-26 W=1 E=0
```

Replace the date and flags with what actually happened. `W` means work and `E` means exercise; each is 0 or 1. Repeated comments for the same day do not add days. [Member guide](docs/MEMBER_GUIDE.md) · [Scoring](docs/SCORING.md)

## Share experiences and respond

Use [experience sharing](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) for your context, what you tried, results, and limits. A short question or note can use [conversation](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=community-chat.yml). Replies, invitations, and encouragement are welcome; none adds points.

Credit original authors, distinguish personal experience from general advice, and share only material you are free to disclose. GitHub Issues and comments are public even when you choose not to appear on the board. Follow the [code of conduct](CODE_OF_CONDUCT.md).

## Improve the repository

Use a small branch and explain the user-facing behavior you changed. Run the checks in [AGENTS.md](AGENTS.md). Scoring changes need explicit agreement, updated examples, and regression coverage. Do not include private health details, raw Issue downloads, credentials, or real member photos in fixtures.

The active implementation is daily-check-in v3; [historical code and reports](docs/LEGACY.md) stay separate. [Maintainer setup](docs/SETUP.md) · [Agent guide](docs/AGENT_GUIDE.md)
