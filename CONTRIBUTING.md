# Contributing to AI Lean Muscle Club

We are a community of AI researchers learning to make room for exercise, recovery, and life alongside research. Researchers in universities, research institutes, and industry are welcome, including students actively conducting AI research. You do not need a fitness background, an impressive physique, or a publication or citation threshold to participate.

Joining a conversation does not commit you to a training plan or a leaderboard. Choose the parts that help you.

## Record freely or join a conversation

Use the **Activity record / 自由运动记录** or **Meal record / 饮食记录** Issue form for a quick standalone record. These do not require a weekly plan or enter rankings. A short description is enough; measurements, calories, and photos are optional. Food Issues also stay outside weekly-plan meal-day counts.

Use the [Beginners Issue form](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=beginners.yml) to introduce yourself, whether you are starting, returning, or just looking around. [Six fictional example files](examples/README.en.md) show the formats. Community forms are available after merging them into the default branch; no weekly plan or leaderboard opt-in is required.

## Plan and check in without a pull request

1. Open the **Weekly plan** issue form for the coming Monday–Sunday week.
2. Choose your time zone, active or recovery mode, and whether to appear in public standings.
3. Choose a primary goal and research-week rhythm if useful. Give each activity a stable ID and a sport, for example `S1 | Monday | basketball | Shooting practice`. To declare a fallback for that session, add a fifth column: `| Short ball-handling practice`.
4. After a session, add a short comment to that same issue:

   ```text
   /done S1 2026-10-26 | Walked for 25 min after an experiment finished.
   ```

5. At the weekend, post `/review` followed by a few sentences about what worked and what to change.

You do not need to train or post every day. Notes, photos, and detailed exercise data are optional. Backfill an honest past session date if you forgot to log it. Use `/pause` when you need a break; a recovery week is also welcome.

The [browser helper](tools/index.html) prepares comments and plan drafts without credentials or automatic posting; [member instructions](docs/MEMBER_GUIDE.md) explain local use and the command-line alternatives. You can find your weekly plan or carry one forward into a new draft; review every draft and explicitly choose whether to opt in again.

Use `/fallback` for that session's declared alternative, `/partial` for a partly completed session, or `/skip` to record a missed session. `/done` and a valid `/fallback` each count as one session of execution credit; `/partial` counts as half, without becoming a full completion. The latest valid status replaces earlier records of the same session. The old three-column plan format still works.

Keep one weekly issue per person. If a plan needs to change, edit it and leave a short explanation in a comment. Preserve the IDs of completed activities. The first successful report sync confirms scoring sessions: later deletion does not reduce the scoring denominator, and added sessions can be recorded without adding execution points. The current plan remains editable and is shown separately. See [the scoring rules](docs/SCORING.md) for accepted formats, duplicate handling, and examples.

## Share experience and help others

Use [community Issues](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose) for questions, conversations, partner matching, events, and notices. Choose one of six topic forms and use its title prefix to find related posts. Community forms do not add scoring labels or award points. [Community organization](docs/COMMUNITY.md) explains how they relate to free records and scored plans.

Use the **Experience sharing** issue form for an idea that other members may find useful and that you would like a maintainer to consider for contribution points. Include enough context for someone to understand when it worked and when it might not.

Useful topics include training around deadlines, restarting after a break, finding exercise partners, food preparation, and Agent workflows that leave more time for movement. For Agent workflows, describe the original task, what the Agent did, the checking or rework required, and the actual time saved. Share only material that you are free to disclose.

Responding thoughtfully to another person's record is also welcome. Ask before giving detailed personal advice. Contribution credit requires both the `points-approved` label and a trusted repository approval entry bound to the Issue’s current body, author, and week. A maintainer prepares the entry for review using the approval command documented in [setup](docs/SETUP.md); a label alone does not add points. Editing an approved body needs renewed review. Posting more frequently does not increase the one-point weekly contribution limit.

Optional food photographs should include brief ingredient, portion, or preparation context when possible. Agent feedback is a discussion aid, with uncertainty stated clearly; it is not a diagnosis or an authoritative nutrition rating. The pilot has no separate food-health score. You may put `/meal YYYY-MM-DD` in its own weekly-Issue comment. Any calorie figures should include their source, portion assumptions, and uncertainty. Logging food is optional, has no extra point bonus, and does not require detailed nutrition tracking. Weekly-plan reports may show distinct valid `/meal` dates, with several meals on one day counted as one record day; free Meal record Issues stay independent.

## Use pull requests for lasting improvements

Pull requests are for documentation, reusable resources, templates, and code—not daily exercise records.

For a small improvement, open a focused pull request explaining what changes and why. For a change to the scoring system or participant workflow, discuss the proposal in an issue first. Include meaningful verification for code that changes scoring, privacy behavior, or automation. Do not include secrets, private health information, or identifiable information about someone else.

Experience reports should distinguish first-hand observation from broader claims. Link to reliable sources when making general health or nutrition claims, and state the limits of personal experience. Avoid promising that a particular physique or exercise will improve research performance for everyone.

## Maintain a welcoming, lightweight process

Maintainers should:

- Help new members complete a first plan and keep the record format short.
- Recognize honest reflection and useful support, including incomplete weeks.
- Review contribution approvals without rewarding popularity or posting volume.
- Let members correct records, adjust future plans, and leave standings without stigma.
- Keep the plan → record → reflection cycle easy to use; evaluate new features through a small voluntary pilot.
- Summarize a few useful lessons instead of requiring members to read every log.

See [the setup guide](docs/SETUP.md) for automation, [the Agent guide](docs/AGENT_GUIDE.md) for optional Agent assistance, and [the code of conduct](CODE_OF_CONDUCT.md) for community expectations.

## Public sharing and leaderboard choice

This repository is intended for public collaboration. Issues, comments, attached images, and code contributions can be read and copied by others. A leaderboard opt-out does not make the underlying records private. Your GitHub handle remains associated with anything you post.

Share the minimum personal information you want to make public. Body photos, body measurements, medical histories, exact locations, and employer-specific work details are never required. Do not upload other people's images, messages, or details without permission. Public information may persist in forks, caches, or Git history after a local deletion; keep sensitive records outside this public repository.
