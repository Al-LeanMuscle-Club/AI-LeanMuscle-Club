# Organizing the community

Use one repository to connect training, research rhythms, and shared experience. Members can take part in several sports and pursue a changing goal; they do not need a separate account, folder, or subgroup for each combination.

## Choose the right place

| Place | Purpose |
| --- | --- |
| README | Club purpose, participation steps, quick links, and an anonymous weekly overview |
| Weekly-plan Issues | One person's weekly plan, short records, optional meal logs, and reflection |
| Experience Issues | Reusable experiences eligible for the existing maintainer approval process |
| Discussions | Questions, conversations, partners, events, and announcements |
| Documentation and PRs | Curated resources, examples, rules, and tool changes |
| Browser helper and generated reports | Prepare comments, find plans, and browse opted-in records |

A Discussion does not earn a contribution point automatically. If its author wants an experience considered for points, they can summarize it in an experience Issue, link the source, and request maintainer review. Multiple posts about the same work cannot exceed the one-point-per-author-per-week contribution cap.

## Five Discussion categories

A maintainer must enable **Settings → General → Features → Discussions** and create the following categories. Adding template files does not create categories or enable Discussions.

| Category name | Required slug / template | Suggested format |
| --- | --- | --- |
| Training and recovery | `training-and-recovery` | Open-ended discussion |
| Nutrition | `nutrition` | Open-ended discussion |
| Research and Agents | `research-and-agents` | Open-ended discussion |
| Buddies and events | `buddies-and-events` | Open-ended discussion |
| Announcements | `announcements` | Announcement |

The first four have forms in `.github/DISCUSSION_TEMPLATE/`. The filename must match the category's actual slug; verify it after creating or renaming a category. Announcement posts use GitHub's ordinary editor and maintainer permissions. Templates must be on the repository's default branch before they are used.

Start with these broad categories. A growing category can later gain an additional dedicated space if its conversations justify the split.

## Independent classification

| Dimension | Canonical values | Where recorded |
| --- | --- | --- |
| Sport | `strength`, `basketball`, `running`, `swimming`, `cycling`, `walking`, `mobility`, `other` | Every planned session |
| Primary goal | `fat-loss`, `muscle-gain`, `cardio`, `skill`, `habit` | The weekly plan |
| Research week | `regular`, `deadline`, `travel` | The weekly plan |
| Content | Plan, check-in, experience, conversation, lasting resource | Its form or destination |

These fields are independent. A mixed-sport week can contain basketball and strength while the primary goal is cardio. Changing next week's goal does not rewrite the goal stored in last week's plan.

The reporting tools read fields, not guessed activities in prose. Old three-column session rows remain valid and use `other`; adding an explicit sport makes future filtering more useful. Optional descriptive labels may be added by maintainers, but member records do not require dozens of labels or combined categories such as “basketball × fat-loss × beginner.” The only labels needed by scoring remain `weekly-plan`, `experience`, and `points-approved`.

## Keep participation lightweight

No daily PRs, personal data files, verification photographs, or exact calorie tracking are required. A short check-in works across sports; optional details belong in notes. Share ideas that another researcher can adapt rather than setting one required routine.

The homepage shows compact counts and report links. Full opt-in standings belong in weekly reports, not an ever-growing list of members on the homepage. Historical reports are revisable snapshots; opt-outs must be respected whenever a report is regenerated. Original public Issues, comments, and Git history remain public even after opting out.

## Curate with permission and context

Maintainers may turn a useful contribution into an experience card or reusable example with its author's agreement. Link to its origin, preserve the context and limits, and avoid republishing personal food, body, health, or confidential research details. Agent summaries need human review and source links.

See [member instructions](MEMBER_GUIDE.md), [scoring](SCORING.md), and [maintainer setup](SETUP.md).

## GitHub references

- [Discussion categories](https://docs.github.com/en/discussions/managing-discussions-for-your-community/managing-categories-for-discussions)
- [Discussion category forms](https://docs.github.com/en/discussions/managing-discussions-for-your-community/creating-discussion-category-forms)
- [Form syntax](https://docs.github.com/en/discussions/managing-discussions-for-your-community/syntax-for-discussion-category-forms)

