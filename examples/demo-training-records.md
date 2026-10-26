# Fictional training records / 虚拟用户训练记录

**Historical 10-point examples / 旧版 10 分制历史示例。** [Current check-ins / 当前打卡方式](../docs/MEMBER_GUIDE.zh-CN.md).

> **Synthetic demo only / 仅为虚构演示。** These people, plans, meals, and reflections are invented. They are not real members or activity and never enter live community statistics. 人物、计划、餐食和复盘均属虚构，不是真实成员或活动，不写入真实周报或统计。

Demo week / 演示周：**2026-10-12** · Cutoff / 截止：**2026-10-19 12:00 UTC**

The six Active/Yes demo plans below are scored by the repository's unchanged `build_week` function, with temporary in-memory confirmations and no trusted contribution approvals. Six fictional score rows appear on the [demo board](demo-board.en.md); the Recovery member is documented separately below.

以下六份 Active/Yes 虚构计划直接使用现有计分器，以临时内存确认计算，不读取真实审批 ledger。[演示榜](demo-board.md)展示六位虚拟用户的演示积分；恢复周成员在文末单独说明。

Full/fallback = 1, partial = 0.5, skipped/unrecorded = 0. Execution points = `6 × (full + 0.5 × partial) / confirmed planned`. The full-completion rate does not count partial as full. Meal days count distinct dates and add no points.

完整或替代完成计 1 次额度，部分完成计 0.5，跳过或尚未记录计 0。执行积分按已确认活动数计算；部分完成不计作完整完成。饮食天数按不同日期统计，不加分。

[Fixture / 原始虚构数据](demo-training-records.json) · [Computed board / 计算结果](demo-leaderboard.json) · [Historical scoring rules / 历史积分规则](../docs/SCORING.v2.md)

## demo-aurora

**Fictional member / 虚拟用户；not a GitHub profile / 不代表 GitHub 账号。**

Demo rank / 演示名次：**1** · Full / 完整：**3 / 3** · Partial / 部分：**0** · Training days / 训练日：**3** · Meal days / 饮食日：**3**

Points / 积分：plan / 计划 **1** + execution / 执行 **6** + review / 复盘 **2** + contribution / 贡献 **0** = **9 / 10**

### Plan and final status / 周计划与最终状态

Week / 周次：2026-10-12 · Time zone / 时区：Asia/Shanghai · Goal / 目标：habit · Research week / 科研节奏：regular

| ID | Planned day / 计划日 | Sport / 项目 | Plan / 内容 | Fallback / 替代 | Final status / 最终状态 | Actual date / 实际日期 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Monday | Strength / 力量 | Gym session log / 健身房活动记录 | — | Full / 完整完成 | 2026-10-12 |
| S2 | Wednesday | Running / 跑步 | Park run log / 公园跑步记录 | — | Full / 完整完成 | 2026-10-14 |
| S3 | Saturday | Swimming / 游泳 | Pool visit log / 泳池活动记录 | — | Full / 完整完成 | 2026-10-17 |

### Original plan / 原始周计划

```text
### Week starting

2026-10-12

### Time zone

Asia/Shanghai

### Participation mode

Active

### Public leaderboard

Yes

### Primary goal

habit

### Research week

regular

### Planned sessions

S1 | Monday | strength | Gym session log / 健身房活动记录
S2 | Wednesday | running | Park run log / 公园跑步记录
S3 | Saturday | swimming | Pool visit log / 泳池活动记录

### Busy-week fallback

Adjust the next plan if needed; no undeclared alternative is counted. / 如需调整可用于下次计划，未声明替代不计为完成。

### Notes

FICTIONAL DEMO / 虚构演示. Entirely synthetic records for an offline README demonstration; no real person, health result, or training prescription. / 全部为README离线展示的合成记录，不代表真实人物、健康结果或训练处方。
```

### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘

#### Record 1 / 原始记录 1

Recorded at / 评论时间：`2026-10-12T12:01:00Z`

```text
/done S1 2026-10-12 | Chose 35 minutes of strength activity. / 自选力量活动35分钟。
```

#### Record 2 / 原始记录 2

Recorded at / 评论时间：`2026-10-14T12:02:00Z`

```text
/done S2 2026-10-14 | Kept the original appointment / 按原安排留下记录
```

#### Record 3 / 原始记录 3

Recorded at / 评论时间：`2026-10-17T12:03:00Z`

```text
/done S3 2026-10-17 | Weekend activity recorded / 记录周末活动
```

#### Record 4 / 原始记录 4

Recorded at / 评论时间：`2026-10-12T12:04:00Z`

```text
/meal 2026-10-12 | Breakfast: toast and egg / 早餐吐司和鸡蛋
```

#### Record 5 / 原始记录 5

Recorded at / 评论时间：`2026-10-12T12:05:00Z`

```text
/meal 2026-10-12 | Lunch: rice and vegetables; same recorded day / 午餐米饭蔬菜，同日去重
```

#### Record 6 / 原始记录 6

Recorded at / 评论时间：`2026-10-14T12:06:00Z`

```text
/meal 2026-10-14 | Cafeteria lunch; quantities not recorded / 食堂午餐，未记录分量
```

#### Record 7 / 原始记录 7

Recorded at / 评论时间：`2026-10-18T12:07:00Z`

```text
/meal 2026-10-18 | A meal prepared at home / 一餐家常饭
```

#### Record 8 / 原始记录 8

Recorded at / 评论时间：`2026-10-18T13:00:00Z`

```text
/review
Three planned sessions were recorded. I will keep the same simple record format next week. / 记录了三次计划活动，下周继续用简短格式。
```

## demo-birch

**Fictional member / 虚拟用户；not a GitHub profile / 不代表 GitHub 账号。**

Demo rank / 演示名次：**2** · Full / 完整：**2 / 3** · Partial / 部分：**1** · Training days / 训练日：**3** · Meal days / 饮食日：**2**

Points / 积分：plan / 计划 **1** + execution / 执行 **5** + review / 复盘 **2** + contribution / 贡献 **0** = **8 / 10**

### Plan and final status / 周计划与最终状态

Week / 周次：2026-10-12 · Time zone / 时区：Asia/Shanghai · Goal / 目标：skill · Research week / 科研节奏：regular

| ID | Planned day / 计划日 | Sport / 项目 | Plan / 内容 | Fallback / 替代 | Final status / 最终状态 | Actual date / 实际日期 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Tuesday | Basketball / 篮球 | Court practice log / 球场练习记录 | — | Full / 完整完成 | 2026-10-13 |
| S2 | Thursday | Cycling / 骑行 | Bike outing log / 骑车活动记录 | — | Full / 完整完成 | 2026-10-15 |
| S3 | Sunday | Mobility / 活动度 | Movement break log / 活动间隙记录 | — | Partial / 部分完成 | 2026-10-18 |

### Original plan / 原始周计划

```text
### Week starting

2026-10-12

### Time zone

Asia/Shanghai

### Participation mode

Active

### Public leaderboard

Yes

### Primary goal

skill

### Research week

regular

### Planned sessions

S1 | Tuesday | basketball | Court practice log / 球场练习记录
S2 | Thursday | cycling | Bike outing log / 骑车活动记录
S3 | Sunday | mobility | Movement break log / 活动间隙记录

### Busy-week fallback

Adjust the next plan if needed; no undeclared alternative is counted. / 如需调整可用于下次计划，未声明替代不计为完成。

### Notes

FICTIONAL DEMO / 虚构演示. Entirely synthetic records for an offline README demonstration; no real person, health result, or training prescription. / 全部为README离线展示的合成记录，不代表真实人物、健康结果或训练处方。
```

### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘

#### Record 1 / 原始记录 1

Recorded at / 评论时间：`2026-10-13T12:01:00Z`

```text
/done S1 2026-10-13 | Spent 30 minutes on shooting practice. / 投篮练习30分钟。
```

#### Record 2 / 原始记录 2

Recorded at / 评论时间：`2026-10-15T12:02:00Z`

```text
/done S2 2026-10-15 | Bike outing recorded / 已记录骑车活动
```

#### Record 3 / 原始记录 3

Recorded at / 评论时间：`2026-10-18T12:03:00Z`

```text
/partial S3 2026-10-18 | Only part of the planned activity; kept it partial / 只完成部分内容，如实记为部分完成
```

#### Record 4 / 原始记录 4

Recorded at / 评论时间：`2026-10-13T12:04:00Z`

```text
/meal 2026-10-13 | Lunch brought from home / 自带午餐
```

#### Record 5 / 原始记录 5

Recorded at / 评论时间：`2026-10-13T12:05:00Z`

```text
/meal 2026-10-13 | Dinner on the same day; not a second meal day / 同一天晚餐，不额外增加饮食天数
```

#### Record 6 / 原始记录 6

Recorded at / 评论时间：`2026-10-17T12:06:00Z`

```text
/meal 2026-10-17 | Weekend noodles / 周末面食
```

#### Record 7 / 原始记录 7

Recorded at / 评论时间：`2026-10-18T13:00:00Z`

```text
/review
Two full records and one partial record reflect this week. I will leave more room between tasks next week. / 本周如实保留两次完整和一次部分记录，下周给安排之间多留余地。
```

## demo-cedar

**Fictional member / 虚拟用户；not a GitHub profile / 不代表 GitHub 账号。**

Demo rank / 演示名次：**3** · Full / 完整：**2 / 4** · Partial / 部分：**2** · Training days / 训练日：**4** · Meal days / 饮食日：**1**

Points / 积分：plan / 计划 **1** + execution / 执行 **4.5** + review / 复盘 **2** + contribution / 贡献 **0** = **7.5 / 10**

### Plan and final status / 周计划与最终状态

Week / 周次：2026-10-12 · Time zone / 时区：Asia/Shanghai · Goal / 目标：habit · Research week / 科研节奏：deadline

| ID | Planned day / 计划日 | Sport / 项目 | Plan / 内容 | Fallback / 替代 | Final status / 最终状态 | Actual date / 实际日期 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Monday | Strength / 力量 | Gym notebook entry / 健身房日志 | — | Full / 完整完成 | 2026-10-12 |
| S2 | Wednesday | Basketball / 篮球 | Ball practice log / 球类练习记录 | Shorter ball-handling practice / 缩短的控球练习 | Fallback / 替代完成 | 2026-10-14 |
| S3 | Friday | Running / 跑步 | Run entry between tasks / 任务间隙跑步记录 | — | Partial / 部分完成 | 2026-10-16 |
| S4 | Sunday | Cycling / 骑行 | Weekend bike entry / 周末骑车记录 | — | Partial / 部分完成 | 2026-10-18 |

### Original plan / 原始周计划

```text
### Week starting

2026-10-12

### Time zone

Asia/Shanghai

### Participation mode

Active

### Public leaderboard

Yes

### Primary goal

habit

### Research week

deadline

### Planned sessions

S1 | Monday | strength | Gym notebook entry / 健身房日志
S2 | Wednesday | basketball | Ball practice log / 球类练习记录 | Shorter ball-handling practice / 缩短的控球练习
S3 | Friday | running | Run entry between tasks / 任务间隙跑步记录
S4 | Sunday | cycling | Weekend bike entry / 周末骑车记录

### Busy-week fallback

Only the fifth-column S2 alternative for demo-cedar is scored. / 只有demo-cedar的S2第五列事先声明了计分替代活动。

### Notes

FICTIONAL DEMO / 虚构演示. Entirely synthetic records for an offline README demonstration; no real person, health result, or training prescription. / 全部为README离线展示的合成记录，不代表真实人物、健康结果或训练处方。
```

### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘

#### Record 1 / 原始记录 1

Recorded at / 评论时间：`2026-10-12T12:01:00Z`

```text
/done S1 2026-10-12 | Recorded 25 minutes of strength activity. / 力量活动25分钟。
```

#### Record 2 / 原始记录 2

Recorded at / 评论时间：`2026-10-14T12:02:00Z`

```text
/fallback S2 2026-10-14 | Used the alternative declared in S2 before the week / 使用S2第五列提前声明的替代活动
```

#### Record 3 / 原始记录 3

Recorded at / 评论时间：`2026-10-16T12:03:00Z`

```text
/partial S3 2026-10-16 | Stopped after part of the planned activity / 仅记录实际完成的部分
```

#### Record 4 / 原始记录 4

Recorded at / 评论时间：`2026-10-18T12:04:00Z`

```text
/partial S4 2026-10-18 | Partly completed; did not mark a full completion / 部分完成，没有记作整次完成
```

#### Record 5 / 原始记录 5

Recorded at / 评论时间：`2026-10-14T12:05:00Z`

```text
/meal 2026-10-14 | Lunch prepared ahead / 提前准备的午餐
```

#### Record 6 / 原始记录 6

Recorded at / 评论时间：`2026-10-14T12:06:00Z`

```text
/meal 2026-10-14 | A second meal on the same date / 同一日期的另一餐
```

#### Record 7 / 原始记录 7

Recorded at / 评论时间：`2026-10-18T13:00:00Z`

```text
/review
A deadline changed the week. The declared alternative was used once, and both partial records remain partial. / 赶稿改变了安排，一次使用预设替代方案，两次部分记录保持如实。
```

## demo-ember

**Fictional member / 虚拟用户；not a GitHub profile / 不代表 GitHub 账号。**

Demo rank / 演示名次：**4** · Full / 完整：**2 / 3** · Partial / 部分：**1** · Training days / 训练日：**3** · Meal days / 饮食日：**2**

Points / 积分：plan / 计划 **1** + execution / 执行 **5** + review / 复盘 **0** + contribution / 贡献 **0** = **6 / 10**

### Plan and final status / 周计划与最终状态

Week / 周次：2026-10-12 · Time zone / 时区：Asia/Shanghai · Goal / 目标：cardio · Research week / 科研节奏：regular

| ID | Planned day / 计划日 | Sport / 项目 | Plan / 内容 | Fallback / 替代 | Final status / 最终状态 | Actual date / 实际日期 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Monday | Swimming / 游泳 | Swimming activity log / 游泳活动日志 | — | Full / 完整完成 | 2026-10-12 |
| S2 | Thursday | Basketball / 篮球 | Basketball activity log / 篮球活动日志 | — | Full / 完整完成 | 2026-10-15 |
| S3 | Saturday | Walking / 步行 | Weekend walk log / 周末散步日志 | — | Partial / 部分完成 | 2026-10-17 |

### Original plan / 原始周计划

```text
### Week starting

2026-10-12

### Time zone

Asia/Shanghai

### Participation mode

Active

### Public leaderboard

Yes

### Primary goal

cardio

### Research week

regular

### Planned sessions

S1 | Monday | swimming | Swimming activity log / 游泳活动日志
S2 | Thursday | basketball | Basketball activity log / 篮球活动日志
S3 | Saturday | walking | Weekend walk log / 周末散步日志

### Busy-week fallback

Adjust the next plan if needed; no undeclared alternative is counted. / 如需调整可用于下次计划，未声明替代不计为完成。

### Notes

FICTIONAL DEMO / 虚构演示. Entirely synthetic records for an offline README demonstration; no real person, health result, or training prescription. / 全部为README离线展示的合成记录，不代表真实人物、健康结果或训练处方。 No weekly reflection was posted in this example. / 此例未发布周复盘。
```

### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘

#### Record 1 / 原始记录 1

Recorded at / 评论时间：`2026-10-12T12:01:00Z`

```text
/done S1 2026-10-12 | Spent 25 minutes at the pool, with a break in the middle. / 泳池活动25分钟，中途休息。
```

#### Record 2 / 原始记录 2

Recorded at / 评论时间：`2026-10-15T12:02:00Z`

```text
/done S2 2026-10-15 | Court activity recorded / 已记录球场活动
```

#### Record 3 / 原始记录 3

Recorded at / 评论时间：`2026-10-17T12:03:00Z`

```text
/partial S3 2026-10-17 | Only part of the planned walk was recorded / 只记录了计划散步的一部分
```

#### Record 4 / 原始记录 4

Recorded at / 评论时间：`2026-10-15T12:04:00Z`

```text
/meal 2026-10-15 | Lunch entry with no calorie estimate / 午餐记录，不估热量
```

#### Record 5 / 原始记录 5

Recorded at / 评论时间：`2026-10-15T12:05:00Z`

```text
/meal 2026-10-15 | Dinner entry on the same date / 同日的晚餐记录
```

#### Record 6 / 原始记录 6

Recorded at / 评论时间：`2026-10-18T12:06:00Z`

```text
/meal 2026-10-18 | Weekend meal entry / 周末一餐记录
```

## demo-delta

**Fictional member / 虚拟用户；not a GitHub profile / 不代表 GitHub 账号。**

Demo rank / 演示名次：**4** · Full / 完整：**1 / 2** · Partial / 部分：**0** · Training days / 训练日：**1** · Meal days / 饮食日：**1**

Points / 积分：plan / 计划 **1** + execution / 执行 **3** + review / 复盘 **2** + contribution / 贡献 **0** = **6 / 10**

### Plan and final status / 周计划与最终状态

Week / 周次：2026-10-12 · Time zone / 时区：Asia/Shanghai · Goal / 目标：habit · Research week / 科研节奏：travel

| ID | Planned day / 计划日 | Sport / 项目 | Plan / 内容 | Fallback / 替代 | Final status / 最终状态 | Actual date / 实际日期 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Tuesday | Walking / 步行 | Walk during a schedule gap / 日程间隙散步记录 | — | Full / 完整完成 | 2026-10-13 |
| S2 | Friday | Mobility / 活动度 | Optional movement session log / 自选活动记录 | — | Skipped / 跳过 | 2026-10-16 |

### Original plan / 原始周计划

```text
### Week starting

2026-10-12

### Time zone

Asia/Shanghai

### Participation mode

Active

### Public leaderboard

Yes

### Primary goal

habit

### Research week

travel

### Planned sessions

S1 | Tuesday | walking | Walk during a schedule gap / 日程间隙散步记录
S2 | Friday | mobility | Optional movement session log / 自选活动记录

### Busy-week fallback

Adjust the next plan if needed; no undeclared alternative is counted. / 如需调整可用于下次计划，未声明替代不计为完成。

### Notes

FICTIONAL DEMO / 虚构演示. Entirely synthetic records for an offline README demonstration; no real person, health result, or training prescription. / 全部为README离线展示的合成记录，不代表真实人物、健康结果或训练处方。
```

### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘

#### Record 1 / 原始记录 1

Recorded at / 评论时间：`2026-10-13T12:01:00Z`

```text
/done S1 2026-10-13 | Walked for 15 minutes without measuring the distance. / 散步15分钟，未测距离。
```

#### Record 2 / 原始记录 2

Recorded at / 评论时间：`2026-10-16T12:02:00Z`

```text
/skip S2 2026-10-16 | Schedule changed, so the session was skipped / 日程变化，如实记录跳过
```

#### Record 3 / 原始记录 3

Recorded at / 评论时间：`2026-10-13T12:03:00Z`

```text
/meal 2026-10-13 | Lunch while away / 在外午餐
```

#### Record 4 / 原始记录 4

Recorded at / 评论时间：`2026-10-13T12:04:00Z`

```text
/meal 2026-10-13 | Dinner on the same date / 同日的一餐晚饭
```

#### Record 5 / 原始记录 5

Recorded at / 评论时间：`2026-10-18T13:00:00Z`

```text
/review
One session was recorded and one was skipped. Writing both states made the week easy to look back on. / 一次记录完成，一次跳过，两种状态都保留，便于回顾。
```

## demo-finch

**Fictional member / 虚拟用户；not a GitHub profile / 不代表 GitHub 账号。**

Demo rank / 演示名次：**6** · Full / 完整：**0 / 3** · Partial / 部分：**2** · Training days / 训练日：**2** · Meal days / 饮食日：**2**

Points / 积分：plan / 计划 **1** + execution / 执行 **2** + review / 复盘 **2** + contribution / 贡献 **0** = **5 / 10**

### Plan and final status / 周计划与最终状态

Week / 周次：2026-10-12 · Time zone / 时区：Asia/Shanghai · Goal / 目标：habit · Research week / 科研节奏：deadline

| ID | Planned day / 计划日 | Sport / 项目 | Plan / 内容 | Fallback / 替代 | Final status / 最终状态 | Actual date / 实际日期 |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Tuesday | Mobility / 活动度 | Movement break entry / 活动间隙日志 | — | Partial / 部分完成 | 2026-10-13 |
| S2 | Thursday | Walking / 步行 | Walk after a task / 任务结束后的散步日志 | — | Partial / 部分完成 | 2026-10-15 |
| S3 | Sunday | Strength / 力量 | A planned gym entry / 计划中的健身房记录 | — | Unrecorded / 尚未记录 | — |

### Original plan / 原始周计划

```text
### Week starting

2026-10-12

### Time zone

Asia/Shanghai

### Participation mode

Active

### Public leaderboard

Yes

### Primary goal

habit

### Research week

deadline

### Planned sessions

S1 | Tuesday | mobility | Movement break entry / 活动间隙日志
S2 | Thursday | walking | Walk after a task / 任务结束后的散步日志
S3 | Sunday | strength | A planned gym entry / 计划中的健身房记录

### Busy-week fallback

Adjust the next plan if needed; no undeclared alternative is counted. / 如需调整可用于下次计划，未声明替代不计为完成。

### Notes

FICTIONAL DEMO / 虚构演示. Entirely synthetic records for an offline README demonstration; no real person, health result, or training prescription. / 全部为README离线展示的合成记录，不代表真实人物、健康结果或训练处方。
```

### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘

#### Record 1 / 原始记录 1

Recorded at / 评论时间：`2026-10-13T12:01:00Z`

```text
/partial S1 2026-10-13 | Did only 5 minutes of mobility practice; the rest was not completed. / 只做了5分钟活动度练习，其余未完成。
```

#### Record 2 / 原始记录 2

Recorded at / 评论时间：`2026-10-15T12:02:00Z`

```text
/partial S2 2026-10-15 | Partial record without extra metrics / 部分完成，未填额外数据
```

#### Record 3 / 原始记录 3

Recorded at / 评论时间：`2026-10-13T12:03:00Z`

```text
/meal 2026-10-13 | Simple meal entry / 简单的一餐记录
```

#### Record 4 / 原始记录 4

Recorded at / 评论时间：`2026-10-16T12:04:00Z`

```text
/meal 2026-10-16 | Prepared food from home / 家里准备的餐食
```

#### Record 5 / 原始记录 5

Recorded at / 评论时间：`2026-10-18T13:00:00Z`

```text
/review
There are two partial records and no record for S3. An unreported session is left unreported, without guessing what happened. / 有两次部分记录，S3未打卡；保留未记录状态，不推测是否运动。
```

## Recovery member / 恢复周成员

This fictional Recovery/No plan is excluded from scored standings, with no points debt. It appears here only as an example of taking a recovery week. 以下 Recovery/No 虚构计划不参加计分，也不产生欠分，仅演示如何记录恢复周。

### demo-recovery

```text
### Week starting

2026-10-12

### Time zone

Asia/Shanghai

### Participation mode

Recovery

### Public leaderboard

No

### Primary goal

habit

### Research week

regular

### Planned sessions

S1 | Wednesday | walking | Optional walk note; not a scored commitment / 可选散步备注，不作为计分承诺
S2 | Saturday | mobility | Optional movement note; no completion required / 可选活动备注，不要求完成

### Busy-week fallback

Adjust the next plan if needed; no undeclared alternative is counted. / 如需调整可用于下次计划，未声明替代不计为完成。

### Notes

FICTIONAL DEMO / 虚构演示. Entirely synthetic records for an offline README demonstration; no real person, health result, or training prescription. / 全部为README离线展示的合成记录，不代表真实人物、健康结果或训练处方。
```

### Original check-ins, meal logs, and reflection / 原始打卡、饮食与复盘

#### Record 1 / 原始记录 1

Recorded at / 评论时间：`2026-10-14T12:01:00Z`

```text
/meal 2026-10-14 | An optional meal note during the recovery week / 恢复周的一条自愿餐食备注
```

#### Record 2 / 原始记录 2

Recorded at / 评论时间：`2026-10-18T13:00:00Z`

```text
/review
This fictional week uses Recovery mode and stays out of the named standings. There is no missed-session debt. / 这个虚构周选择Recovery且不参具名榜单，不产生欠打卡。
```
