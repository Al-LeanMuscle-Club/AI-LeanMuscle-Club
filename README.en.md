# AI Lean Muscle Club 💪🤖

**English** | [简体中文](README.md)

<!-- README:LANG=en -->
<!-- README:COMMUNITY-FIRST -->

**Train model and train body. Just for fun and health.**

A community for AI researchers: record work and exercise, follow a weekly board, and exchange real experiences.

**[Start my check-in journal](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=daily-checkin.yml) · [Share an experience](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) · [Start a conversation](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=community-chat.yml)**

## Daily check-ins

1. Create one long-running Issue and choose its time zone. Select **Yes** for **Public leaderboard** to appear on the board; the default is No.
2. Comment on your own Issue each day. `W` means work, `E` means exercise; `1` means yes and `0` means no:

   ```text
   /checkin 2026-10-26 W=1 E=0
   ```

3. The board updates daily at **01:15 UTC / 09:15 Beijing time**. Each Monday–Sunday week counts distinct work and exercise dates. The latest valid check-in replaces earlier ones for the same date.

<a id="member-helper"></a>

The [check-in helper][member-helper] finds your journal, prepares comment text, and displays standings. Review and post the text yourself; the page never posts for you.

## Weekly board

<a id="weekly-community-board"></a>

For weekly work days $W$ and exercise days $E$:

$$
S = 100 \sqrt{\min(W/5, 1) \cdot \min(E/4, 1)}
$$

Five work days and four exercise days reach 100 points. Either count at zero makes the score zero. This measures self-reported participation, not work hours, exercise volume, or physical condition. [Full rules](docs/SCORING.md)

[See the latest board](README.md#周榜) · [Weekly reports](reports/daily/README.md). The first report will appear after the new daily calculation runs.

<a id="news"></a>

## News · Featured member experiences

Personal experiences from community members. Follow a title to read the full story in Chinese, ask questions, or share your own approach in the original thread.

- **[Lessons from losing 30 kg · #35](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/35)** — [@rentainhe](https://github.com/rentainhe) shares how enjoying basketball became a starting point for gradually building exercise and eating habits. Also available as an [edited story (Chinese)](docs/experiences/2026-10-24-rentainhe.md).
- **[Let the agent run experiments; head downstairs for a workout · #44](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/44)** — [@Aaronhuang-778](https://github.com/Aaronhuang-778) describes using time while an agent runs tasks to exercise, while also making room for rest.
- **[Early Bird: the idea and the practice · #42](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/42)** — [@ChawDoe](https://github.com/ChawDoe) describes the EarlyBird community's shared breakfasts and group check-ins as a way to build regular daily routines.
- **[Finding work–life balance while chasing deadlines · #41](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/41)** — [@EasonXiao-888](https://github.com/EasonXiao-888) shares attempts to keep some movement, meals, and rest in busy weeks, then gradually return to a regular rhythm afterward.

Reply in these threads or [share your own experience](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml). Experiences and conversations do not add points.

All Issues and comments are public, including journals outside the board. [Member guide](docs/MEMBER_GUIDE.md) · [Code of conduct](CODE_OF_CONDUCT.md) · [Maintainer setup](docs/SETUP.md)

[member-helper]: docs/SETUP.md#9-optional-browser-helper-and-pages-deployment
