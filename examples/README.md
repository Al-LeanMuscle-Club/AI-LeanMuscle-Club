[English](README.en.md) | 简体中文 / Bilingual

# Optional record templates / 可选记录模板

These are fictional examples of record formats, not actual participation, training prescriptions, or nutrition targets. Copy only fields you find useful. Do not publish these examples as real community activity.

这些是记录格式的假想示例，不是真实打卡、训练处方或营养目标。只复制对你有用的字段，不要把示例作为真实社区活动发布。

See [the member guide](../docs/MEMBER_GUIDE.md) / [成员使用指南](../docs/MEMBER_GUIDE.zh-CN.md) for accepted commands and scoring. Put each command in its own comment on your weekly Issue. Optional prose after it does not add points or enter generated report data; it remains public in the source Issue.

## Six community examples / 六类参与示例

Every file contains two short fictional scenarios. They are reference material, not live posts or real participation data.

| Topic / 主题 | 中文示例 | English examples | Where to participate / 参与位置 |
| --- | --- | --- | --- |
| 新人报到 | [新人报到](beginners.md) | [Beginners](beginners.en.md) | [新人报到 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=beginners.yml) · `[Hello]` |
| 训练交流与打卡 | [训练交流与记录](training-and-recovery.md) | [Training and recovery](training-and-recovery.en.md) | [训练交流 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=training-and-recovery.yml) / [自由运动记录](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=activity-record.yml) |
| 饮食记录与分享 | [饮食记录与分享](nutrition.md) | [Nutrition](nutrition.en.md) | [饮食分享 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=nutrition.yml) / [饮食记录](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=meal-record.yml) |
| 找搭子 | [找搭子与活动](buddies-and-events.md) | [Buddies and events](buddies-and-events.en.md) | [找搭子 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=buddies-and-events.yml) · `[Buddies]` |
| 科研与 Agent | [科研与 Agent](research-and-agents.md) | [Research and Agents](research-and-agents.en.md) | [科研与 Agent Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=research-and-agents.yml) / [经验分享 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) |
| 排名 | [排名演示](ranking.md) | [Ranking](ranking.en.md) | 独立离线示例，不写入 `reports/`；真实计分使用 [每周计划 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml) |

所有社区交流都使用 Issues 表单。主题按 `[Hello]`、`[Training]`、`[Food]`、`[Buddies]`、`[Research / Agent]` 等标题前缀区分，无需启用额外类别或新增社区标签。维护者公告使用 [公告 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=announcements.yml)（`[Club]`）。

Community conversations use Issue forms and title prefixes; no additional category setup or new community labels are required. Templates do not create live posts or fake members. Published demonstrations must stay clearly marked as fictional and unscored. A research/Agent community Issue does not automatically earn points: use the separate experience Issue and the existing approval-label plus trusted-ledger review process when requesting contribution recognition.

公开演示帖须明确标注虚构，不作为真实参与或计分记录。社区分享不会自动计分；科研与 Agent 经验需要另建经验 Issue，并沿用审批标签及可信 ledger 流程申请贡献认可。

## 虚拟用户训练记录与演示榜 / Fictional training-record demo

首页的虚拟榜单展示 6 位虚拟用户的参与积分，另有 1 位恢复成员的记录。演示周固定为 **2026-10-12 至 2026-10-18**，所有人物和活动均为虚构。

[完整训练记录与复盘](demo-training-records.md) · [虚拟输入数据](demo-training-records.json) · [演示榜单数据](demo-leaderboard.json)

演示文件保存在 `examples/`，README 演示表使用独立的 `DEMO` 区块；真实社区概况由原有 `CLUB` 区块自动更新。修改虚拟记录后，在仓库目录重新生成两种语言的榜单：

```bash
python scripts/render_demo_board.py
python scripts/render_demo_board.py --check
```

## A mixed-sport week / 混合运动周

Enter these lines in the **Planned sessions** field, after choosing your own activities and schedule:

```text
S1 | Tuesday | strength | My chosen gym session | My chosen at-home alternative
S2 | Thursday | basketball | Practice with a friend
S3 | Saturday | running | My chosen route
```

The fifth column belongs only to that session. A `/fallback S1 ...` can count once for S1 because this example declares an alternative for S1. The general Busy-week fallback note alone does not declare an alternative for S2 or S3. The same session cannot earn completion credit twice.

第五列只对应本次训练。示例为 S1 提前写了替代方案，因此 `/fallback S1 ...` 可以计为 S1 完成一次；通用 Busy-week fallback 说明不会自动为 S2、S3 声明替代方案。同一编号不能重复获得完成积分。

## Strength / 力量训练

```text
/done S1 2026-10-27 | Completed the session I planned.
Optional exercise notes / 可选动作记录:
- Exercise / 动作:
- Sets and repetitions / 组数与次数:
- Load, if I want to share / 自愿公开的重量:
- Adjustment or observation / 调整或体会:
```

## Basketball / 篮球

```text
/done S2 2026-10-29 | Practice or game / 技术练习或比赛.
Focus / 重点:
Duration, optional / 可选时长:
What I noticed / 体会:
How it fitted the workday / 怎样安排进工作日:
```

## Running / 跑步

```text
/done S3 2026-10-31 | My planned run / 计划中的跑步.
Duration, optional / 可选时间:
Distance or pace, optional / 可选距离或配速:
Perceived effort / 主观强度:
Energy afterward / 之后的精力感受:
```

Use the same light structure for swimming, cycling, walking, mobility, or other activities. No detailed metric is required.

游泳、骑行、步行、活动度练习等也可以沿用相同的简短结构，不要求详细指标。

## An honest partial session / 如实记录部分完成

```text
/partial S1 2026-10-27 | Did part of the session before my schedule changed.
What I did / 实际完成的内容:
What I will adjust / 准备调整的地方:
```

`partial` gives half a session of execution credit while remaining separate from full completion. The latest valid status wins if you later correct the record. An incomplete week can still receive reflection points.

`partial` 获得半次执行额度，并单独保留部分完成状态，不算完整完成。之后更正时以最新有效状态为准；没有完成计划也可以正常获得复盘积分。

## A food record without calorie counting / 不算热量的饮食记录

```text
/meal 2026-10-28 | Lunch / 午餐
What I ate / 食物:
Portion context, if known / 已知的分量信息:
What helped during a busy day / 忙碌时有帮助的安排:
What I might change / 下次想调整的地方:
Photo / 照片: optional / 选填
```

## A food record with an optional estimate / 带可选估算的饮食记录

```text
/meal 2026-10-28 | Dinner / 晚餐
Food and portion / 食物和分量:
Estimate source / 估算来源: label, weighed recipe, personal estimate, or model estimate
Estimated range / 估算范围: leave blank if unknown / 不清楚时留空
Assumptions / 假设:
Unknowns / 未知信息: oil, sauce, portion size, or mixed ingredients
Correction later, if needed / 之后可补充修正:
```

There is no automatic model service behind this template. Calories and nutrient numbers are optional estimates, not health grades, meal rankings, or point multipliers. No extra points come from eating less or logging more food photos.

模板没有连接自动模型服务。热量和营养数值是可选估算，不是健康评级、餐食排名或积分倍率；吃得更少、上传更多饮食照片都不会额外加分。

## Weekly reflection and Agent time savings / 周复盘与 Agent 净节时

```text
/review
Research context / 科研安排: regular, deadline, or travel
What worked / 有效的安排:
What got in the way / 遇到的障碍:
Next week's adjustment / 下周准备调整的地方:

Optional Agent workflow / 可选 Agent 工作流:
Original task / 原任务:
What the Agent handled / Agent 分担的内容:
Setup, checking, and rework / 设置、检查与返工:
Net time saved, if known / 已知的净节时:
Did I use it for exercise or rest? / 是否真的用于运动或休息:
Limits / 适用范围与局限:
```

Keep claims about time savings grounded in what you observed. A personal observation about energy or work does not establish that an activity causes better research performance for everyone. Reusable experiences can be submitted through the experience Issue form; contribution credit requires a maintainer's `points-approved` label plus a trusted repository approval entry matching the current body, author, and week, and stays capped at one point per member per week.

节时说明以实际观察为准。个人精力或工作感受不能证明某种运动会普遍提高科研表现。可复用经验可以通过经验分享 Issue 提交，贡献积分需要维护者添加 `points-approved` 并提交匹配当前正文、作者和周次的可信仓库审批记录，单独标签不足以计分；每人每周仍最多 1 分。
