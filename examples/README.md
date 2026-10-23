# Optional record templates / 可选记录模板

These are fictional examples of record formats, not actual participation, training prescriptions, or nutrition targets. Copy only fields you find useful. Do not publish these examples as real community activity.

这些是记录格式的假想示例，不是真实打卡、训练处方或营养目标。只复制对你有用的字段，不要把示例作为真实社区活动发布。

See [the member guide](../docs/MEMBER_GUIDE.md) / [成员使用指南](../docs/MEMBER_GUIDE.zh-CN.md) for accepted commands and scoring. Put each command in its own comment on your weekly Issue. Optional prose after it does not add points or enter generated report data; it remains public in the source Issue.

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

`partial` preserves a useful record without awarding full completion credit. The latest valid status wins if you later correct the record. An incomplete week can still receive reflection points.

`partial` 保留有用的记录，但不按完整完成计分。之后更正时以最新有效状态为准；没有完成计划也可以正常获得复盘积分。

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

Keep claims about time savings grounded in what you observed. A personal observation about energy or work does not establish that an activity causes better research performance for everyone. Reusable experiences can be submitted through the experience Issue form; contribution credit requires a maintainer's `points-approved` label and stays capped at one point per member per week.

节时说明以实际观察为准。个人精力或工作感受不能证明某种运动会普遍提高科研表现。可复用经验可以通过经验分享 Issue 提交，由维护者添加 `points-approved` 后按原规则考虑贡献积分；每人每周仍最多 1 分。
