# Organizing the community with Issues

Use one repository to connect training, research rhythms, and shared experience. Members can take part in several sports and pursue a changing goal; they do not need a separate account, folder, or subgroup for each combination.

## Choose the right place

| Place | Purpose |
| --- | --- |
| README | Club purpose, participation steps, quick links, and an anonymous weekly overview |
| Activity-record and meal-record Issues | Free records without a weekly plan or ranking; labels `activity-record` and `meal-record` |
| Weekly-plan Issues | One person's weekly plan, short records, optional meal logs, and reflection |
| Experience Issues | Reusable experiences eligible for the existing maintainer approval process |
| Community Issues | Introductions, questions, conversations, partners, events, and announcements |
| Documentation and PRs | Curated resources, examples, rules, and tool changes |
| Browser helper and generated reports | Prepare comments, find plans, and browse opted-in records |

Community Issue posts and replies do not earn contribution points automatically. To request review, summarize a reusable experience in an Experience sharing Issue and link the source. Contribution credit requires `experience`, `points-approved`, and a trusted approval record matching the body, author, and week. Multiple posts about the same work cannot exceed one contribution point per author per week.

## Six community Issue forms

Open [New issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose), choose a topic, and continue the conversation in its comments. The forms become available after `.github/ISSUE_TEMPLATE/` is merged into the default branch with Issues enabled. No weekly plan, leaderboard opt-in, extra category setting, or new community label is required.

| Topic | Issue form | Title prefix |
| --- | --- | --- |
| Newcomer introductions / 新人报到 | [Beginners](../.github/ISSUE_TEMPLATE/beginners.yml) | `[Hello]` |
| Training and recovery / 训练交流 | [Training and recovery](../.github/ISSUE_TEMPLATE/training-and-recovery.yml) | `[Training]` |
| Food conversations / 饮食分享 | [Nutrition](../.github/ISSUE_TEMPLATE/nutrition.yml) | `[Food]` |
| Research and Agents / 科研与 Agent | [Research and Agents](../.github/ISSUE_TEMPLATE/research-and-agents.yml) | `[Research / Agent]` |
| Finding partners and events / 找搭子与活动 | [Buddies and events](../.github/ISSUE_TEMPLATE/buddies-and-events.yml) | `[Buddies]` |
| Community notices / 社区公告 | [Announcements](../.github/ISSUE_TEMPLATE/announcements.yml) | `[Club]` |

Use title prefixes to find related Issues. Announcements are ordinary Issues: anyone who can open an Issue can submit one. Maintainers review proposed notices and decide which to publish as official notices or pin; a template does not enforce maintainer-only posting.

Welcome new and returning members through the Beginners Issue form. The [six independent example files](../examples/README.en.md) illustrate introductions, training, food, partners, research/Agents, and participation points. Published demonstrations must be clearly marked as fictional and excluded from participation scoring and member statistics.

## Independent classification

| Dimension | Canonical values | Where recorded |
| --- | --- | --- |
| Sport | `strength`, `basketball`, `running`, `swimming`, `cycling`, `walking`, `mobility`, `other` | Every planned session |
| Primary goal | `fat-loss`, `muscle-gain`, `cardio`, `skill`, `habit` | The weekly plan |
| Research week | `regular`, `deadline`, `travel` | The weekly plan |
| Content | Plan, check-in, experience, conversation, lasting resource | Its form or destination |

These fields are independent. A mixed-sport week can contain basketball and strength while the primary goal is cardio. Changing next week's goal does not rewrite the goal stored in last week's plan.

The reporting tools read fields, not guessed activities in prose. Old three-column session rows remain valid and use `other`; adding an explicit sport makes future filtering more useful. Optional descriptive labels may be added by maintainers, but member records do not require dozens of labels or combined categories such as “basketball × fat-loss × beginner.” Scoring uses `weekly-plan`, `experience`, and `points-approved`, with a trusted approval ledger as well as the contribution label. A label alone is not approval. Independent `activity-record` and `meal-record` Issues are unscored, so free records cannot accidentally become a training commitment or score.

## Keep participation lightweight

No daily PRs, personal data files, verification photographs, or exact calorie tracking are required. A short check-in works across sports; optional details belong in notes. Share ideas that another researcher can adapt rather than setting one required routine.

The board describes weekly participation, not athletic ability. Partial sessions receive half execution credit while remaining separate from full completions; distinct valid meal-record dates can be displayed without adding points. A confirmed scoring snapshot keeps deleted commitments from shrinking the denominator, while the current plan remains editable. See [scoring](SCORING.md).

The homepage shows compact counts and report links. Full opt-in standings belong in weekly reports, not an ever-growing list of members on the homepage. Historical reports are revisable snapshots; opt-outs must be respected whenever a report is regenerated. Original public Issues, comments, and Git history remain public even after opting out.

## Curate with permission and context

Maintainers may turn a useful contribution into an experience card or reusable example with its author's agreement. Link to its origin, preserve the context and limits, and avoid republishing personal food, body, health, or confidential research details. Agent summaries need human review and source links.

See [member instructions](MEMBER_GUIDE.md), [scoring](SCORING.md), and [maintainer setup](SETUP.md).

## GitHub references

- [Creating an Issue](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue)
- [Creating Issue forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-issue-forms)
- [Issue form syntax](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms)

<!-- club-published-issue-examples:start -->
## Published examples

These are fictional, unscored examples. Choose a language below to open its Issue.

| Topic | 中文 Issue | English Issue |
| --- | --- | --- |
| Newcomer introductions | [#16](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/16) | [#19](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/19) |
| Finding exercise buddies | [#17](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/17) | [#20](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/20) |
| Research and Agents | [#18](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/18) | [#21](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/21) |

<!-- club-published-issue-examples:end -->
