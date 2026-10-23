# AI 薄肌俱乐部 💪🤖

[English](README.md) | **简体中文**

**练模型，也练身体。**

面向 AI 科研人员的交流社区，一起为运动、恢复和科研之外的生活留出时间。

[制定周计划](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml) · [查看大家的计划](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues?q=label%3Aweekly-plan) · [分享经验](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) · [评分规则（英文）](docs/SCORING.md) · [维护者设置指南（英文）](docs/SETUP.md)

<p align="center">
  <a href="assets/club-poster.png"><img src="assets/club-poster.png" alt="AI 薄肌俱乐部：面向 AI 科研人员，一起兼顾科研与健康。练模型，也练身体。海报附微信群邀请二维码。" width="1000"></a>
</p>

当前微信群邀请二维码标注的有效期为 **2026 年 10 月 29 日前**。如果已经过期，请向现有成员获取最新邀请。邀请更新后，维护者可以替换 `assets/club-poster.png`。

## 建群初衷

AI 科研发展很快，总有读不完的论文、跑不完的实验、需要检查的结果和接踵而至的 deadline。压力大的时候，运动和休息很容易成为最先被推迟的事情。

我发起这个俱乐部，是想找到一些同样认真对待科研和健康的同行。做 AI 研究的同时，我已经坚持健身十年，但仍在学习怎样让两者长期协调。最初的想法很简单：建一个聊天群，让大家分享经验、寻找运动搭子，互相鼓励着坚持下去。

短短几个小时，就有 200 多人加入。这个仓库希望把群里的交流沉淀下来：分享切实可行的计划，做简单的记录，从没能完成的训练中总结经验，也积累实用的科研与健身工作流。

我们想讨论的，都是具体的问题：

- AI 和科研安排不断变化，怎样给运动留出稳定的时间？
- 哪些训练安排更适合高强度脑力工作，又怎样影响我们各自的精力和恢复？
- 算上检查和返工，哪些任务交给 Agent 后真的能减轻负担？省下的时间，能否留给运动和生活？

我们希望慢慢找到一种中断之后也愿意回来的节奏。做好研究、保持健康、充分休息和认真生活，都值得拥有时间。

—— 发起人 Yukang Chen

## 面向哪些人

面向高校、科研机构和企业中实际从事 AI 研究的同行，也欢迎正在开展 AI 科研的学生。健身新手和有经验的运动者都欢迎加入。这里没有引用量门槛、身材要求，也不强制参加积分排名。

“薄肌”是俱乐部的名字，并不是对成员体型的要求。大家可以选择适合自己的运动、目标和公开参与程度。阅读、聊天、分享，或者安排一个恢复周，都是参与社区的方式。

## 三步开始参与

1. [创建一个周计划 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml)，填写时区、当前目标、科研节奏和现实可行的训练安排。**默认不加入公开排名**。
2. 训练后在自己的 Issue 下评论。简短命令就够了，照片和详细运动数据始终选填。
3. 周末以 `/review` 开头，写几句这一周的感受、遇到的困难和下周调整。

下面是格式示例，不是训练处方：

```text
S1 | Tuesday | strength | 去健身房训练 | 在家做简短训练
S2 | Thursday | basketball | 投篮练习
S3 | Saturday | running | 轻松跑
```

星期保留完整英文名称，训练编号使用 `S1`–`S99`。可选的第五列是**该次训练**预先声明的忙周替代方案。旧版三列计划继续兼容；描述、评论和复盘都可以用中文。

```text
/done S1 2026-10-27 | 今天缩短了训练时间。
```

完成 S1 已声明的替代方案时，用 `/fallback S1 YYYY-MM-DD`；部分完成用 `/partial`，跳过用 `/skip`，后二者只记录状态，不获得执行分。同一训练只计一次，使用最新有效状态。每条评论只放一个命令。[完整操作与饮食记录说明 →](docs/MEMBER_GUIDE.zh-CN.md)

**快捷工具：** [查找我的计划／生成打卡评论](tools/index.html)（[本地打开方式](docs/MEMBER_GUIDE.md#browser-helper)）· [沿用上周计划](docs/MEMBER_GUIDE.zh-CN.md) · [自愿公开的报告数据](reports/index.json)

## 按运动、目标和科研节奏找到同行

| 维度 | 选项 |
| --- | --- |
| 每次训练的项目 | `strength` 力量、`basketball` 篮球、`running` 跑步、`swimming` 游泳、`cycling` 骑行、`walking` 步行、`mobility` 活动度、`other` 其他 |
| 每周主要目标 | `fat-loss` 减脂、`muscle-gain` 增肌、`cardio` 心肺、`skill` 技术、`habit` 维持习惯 |
| 本周科研节奏 | `regular` 常规、`deadline` 赶稿、`travel` 出差 |

一个人可以在同一周练力量、打篮球、跑步。运动项目与目标分开分类，不要求选择唯一运动类型。动作、组次、重量、里程、配速、精力和疲劳都可以选填，不影响基本打卡，也不增加积分。[各项目模板 →](examples/README.md)

## 每周社区概况

[查看最新概况 →](README.md#weekly-community-board) · [完整周报告 →](reports/README.md)

首页保持简洁，完整的自愿排名和训练状态放在周报告。生成报告不会复制原始备注、餐食内容、身体指标或评论全文。选择 `No` 会使你的身份不出现在生成的榜单和索引中，**原始公开 Issue 仍然可见**。中文页链接到同一份自动更新的概况，避免出现两份不同的数据。

## 每周最多 10 分，一点小小的鼓励

| 项目 | 最高积分 |
| --- | ---: |
| 一个有效的 Active 周计划 | 1 |
| 个人计划执行：`6 × 完成次数 / 计划次数`，保留两位小数 | 6 |
| 一条非空的周末 `/review`，与完成情况无关 | 2 |
| 经维护者认可的有用经验 Issue | 1 |
| **每周上限** | **10** |

完成预先声明的替代方案计作同一次训练的完成；部分完成和跳过保留记录，不获得执行分。重量、里程、时长、热量、减重、照片和发帖数量都不额外加分。积分按周重置，自愿参加，同分并列。选择 Recovery，或本人评论 `/pause`，即可让该周退出排名，不产生欠分。[完整规则与纠错方式（英文）→](docs/SCORING.md)

## 交流、饮食和科研工作流

维护者开启并建立栏目后，可以在 [Discussions](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/discussions) 中交流训练与恢复、饮食、科研与 Agent、搭子与活动，以及公告。周计划与日常打卡留在 Issues；精选资源通过文档和 PR 沉淀。讨论帖不会自动获得贡献分；需要参与现有认可流程时，使用[经验分享 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml)。[社区栏目说明（英文）→](docs/COMMUNITY.md)

可以自愿用 `/meal YYYY-MM-DD` 记录餐食，附文字、照片、分量、热量估算来源和不确定性。这些记录不额外加分。当前没有配置统一热量目标、自动模型估算或餐食健康评分；饮食细节和身体数据始终选填。[饮食记录示例 →](docs/MEMBER_GUIDE.zh-CN.md)

分享 Agent 工作流时，推荐写：**原任务 → Agent 分担了什么 → 检查与返工 → 实际净节时 → 是否把时间留给了运动或休息**。积分由明确规则的 Python 工具计算；可选 AI 总结需要人工审核。[Agent 指南（英文）→](docs/AGENT_GUIDE.md)

## 参与原则与启用方式

诚实、友善，尊重不同的身体、训练基础与生活安排。休息和重新开始都欢迎。不要强迫训练、索要照片、公开保密科研资料、未经许可分享他人信息，或发布广告。公开 Issue、评论、图片和提交历史可能被复制与保留；不参加排名不会让记录变成私密。

维护者完成设置后，报告流程计划在**每天北京时间 09:15**更新当前和上一报告周，GitHub 的定时任务可能延迟。报告周按北京时间选择，每次打卡日期按成员所填时区解释，历史报告允许纠正。仓库权限、标签和讨论栏目需要[手工设置（英文）](docs/SETUP.md)，上传文件不会自动开启这些功能。当前没有连接外部 AI 模型或微信群采集器。

[中文参与指南](docs/MEMBER_GUIDE.zh-CN.md) · [贡献指南（英文）](CONTRIBUTING.md) · [行为准则（英文）](CODE_OF_CONDUCT.md) · [维护者设置（英文）](docs/SETUP.md)
