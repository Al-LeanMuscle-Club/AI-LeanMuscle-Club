# AI 薄肌俱乐部 💪🤖

[English](README.en.md) | **简体中文**

<!-- README:LANG=zh-CN -->

**练模型，也练身体。**

面向 AI 科研人员的交流社区，一起为运动、恢复和科研之外的生活留出时间。

[运动打卡](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=activity-record.yml) · [记录饮食](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=meal-record.yml) · [分享交流](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose) · [每周参与榜](reports/README.md)

## 今天想怎样参与

| 我想…… | 从这里开始 |
| --- | --- |
| 随手记录今天的运动，暂时不做周计划 | [自由运动打卡](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=activity-record.yml) |
| 保存一餐、照片或备餐灵感 | [饮食记录](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=meal-record.yml) |
| 新人报到、提问、找搭子、交流 Agent 工作流 | [社区交流](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose) · [各类示例](examples/README.md) |
| 做一份周计划，并自愿参加排名 | [创建周计划](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=weekly-plan.yml) · [积分细则](docs/SCORING.md) |

一句话或一张照片也欢迎。自由运动与饮食记录不要求先制定周计划，也不加入积分榜；发到这里的内容都是公开的。结构化周记录还会展示训练记录天数、饮食记录天数和部分完成情况，食物数量与身体指标不加分。

[成员辅助页与周榜](tools/index.html) · [新人、训练、饮食、搭子、Agent 与排名示例](examples/README.md)。辅助页可在本地运行，或由维护者按照[中文 Pages 启用指南](docs/PAGES_QUICKSTART.zh-CN.md)部署；成功部署后访问 Actions 中提供的站点地址。直接在 GitHub 打开 HTML 文件只会显示源码。社区 Issue 表单合并到默认分支后即可使用。

<p align="center">
  <a href="assets/club-poster.png"><img src="assets/club-poster.png" alt="AI 薄肌俱乐部：面向 AI 科研人员，一起兼顾科研与健康。练模型，也练身体。海报附微信群邀请二维码。" width="1000"></a>
</p>

当前微信群邀请二维码标注的有效期为 **2026 年 10 月 29 日前**。如果已经过期，请向现有成员获取最新邀请。邀请更新后，维护者可以替换 `assets/club-poster.png`。

了解俱乐部的[建群初衷](docs/ABOUT.zh-CN.md#建群初衷)与[面向哪些人](docs/ABOUT.zh-CN.md#面向哪些人)。

## 自愿制定周计划：三步开始

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

完成 S1 已确认的替代方案时，用 `/fallback S1 YYYY-MM-DD`；部分完成用 `/partial`，获得该次执行额度的一半；跳过用 `/skip`，不获得执行分。同一训练只计一次，使用最新有效状态。首次成功同步会确认本周计分训练，之后调整会单独展示，删掉未完成项目不能提高积分。每条评论只放一个命令。[完整操作与饮食记录说明 →](docs/MEMBER_GUIDE.zh-CN.md)

**快捷工具：** [查找我的计划／生成打卡评论](tools/index.html)（[本地打开方式](docs/MEMBER_GUIDE.md#browser-helper)）· [沿用上周计划](docs/MEMBER_GUIDE.zh-CN.md) · [自愿公开的报告数据](reports/index.json)

## 按运动、目标和科研节奏找到同行

| 维度 | 选项 |
| --- | --- |
| 每次训练的项目 | `strength` 力量、`basketball` 篮球、`running` 跑步、`swimming` 游泳、`cycling` 骑行、`walking` 步行、`mobility` 活动度、`other` 其他 |
| 每周主要目标 | `fat-loss` 减脂、`muscle-gain` 增肌、`cardio` 心肺、`skill` 技术、`habit` 维持习惯 |
| 本周科研节奏 | `regular` 常规、`deadline` 赶稿、`travel` 出差 |

一个人可以在同一周练力量、打篮球、跑步。运动项目与目标分开分类，不要求选择唯一运动类型。动作、组次、重量、里程、配速、精力和疲劳都可以选填，不影响基本打卡，也不增加积分。[各项目模板 →](examples/README.md)

## 每周社区概况

<!-- DEMO:START -->

### 虚拟用户演示榜 — 2026-10-12 周

**以下是静态虚构演示，不是真实成员、打卡或成绩，不计入下方真实社区人数或排名。** 演示截止时间为 2026-10-19 12:00 UTC；六位参榜虚拟用户和一位恢复周虚拟用户均来自离线示例。

| 名次 | 虚拟用户 | 运动项目 | 完整 / 计划 | 部分完成 | 训练日 | 饮食日 | 参与分 / 10 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | [demo-aurora](examples/demo-training-records.md#demo-aurora) | 跑步、力量、游泳 | 3 / 3 | 0 | 3 | 3 | **9** |
| 2 | [demo-birch](examples/demo-training-records.md#demo-birch) | 篮球、骑行、活动度 | 2 / 3 | 1 | 3 | 2 | **8** |
| 3 | [demo-cedar](examples/demo-training-records.md#demo-cedar) | 篮球、骑行、跑步、力量 | 2 / 4 | 2 | 4 | 1 | **7.5** |
| 4 | [demo-ember](examples/demo-training-records.md#demo-ember) | 篮球、游泳、步行 | 2 / 3 | 1 | 3 | 2 | **6** |
| 4 | [demo-delta](examples/demo-training-records.md#demo-delta) | 活动度、步行 | 1 / 2 | 0 | 1 | 1 | **6** |
| 6 | [demo-finch](examples/demo-training-records.md#demo-finch) | 活动度、力量、步行 | 0 / 3 | 2 | 2 | 2 | **5** |

完整与替代完成各计 1 次执行额度，部分完成计 0.5；训练日和饮食日不额外加分。恢复周不参榜。

[查看每位虚拟用户的完整计划、原始记录与积分组成](examples/demo-training-records.md) · [虚构榜单数据](examples/demo-leaderboard.json)

<!-- DEMO:END -->

<!-- CLUB:START -->

### 周次：2026-10-19 起

参与人数：**0** · 恢复/暂停人数：**0**

公开参与人数：**0** · 已记录完成：**0/0** · 周复盘：**0**

次数仅汇总选择公开的活跃成员各自的计划，不代表健康或运动能力排名。

计分规则：v2。整次完成或按预设替代方案完成计 1 次，部分完成计 0.5 次；已确认计划固定计分分母。

[完整周报](reports/2026-10-19.md) · [公开数据](reports/2026-10-19.json) · [查找计划与打卡助手](tools/index.html)

更新时间：2026-10-23T08:53:35.471818Z

### 周次：2026-10-12 起

参与人数：**0** · 恢复/暂停人数：**0**

公开参与人数：**0** · 已记录完成：**0/0** · 周复盘：**0**

次数仅汇总选择公开的活跃成员各自的计划，不代表健康或运动能力排名。

计分规则：v2。整次完成或按预设替代方案完成计 1 次，部分完成计 0.5 次；已确认计划固定计分分母。

[完整周报](reports/2026-10-12.md) · [公开数据](reports/2026-10-12.json) · [查找计划与打卡助手](tools/index.html)

更新时间：2026-10-23T08:53:35.471818Z

<!-- CLUB:END -->

首页保持简洁，完整的自愿排名和训练状态放在周报告。生成报告不会复制原始备注、餐食内容、身体指标或评论全文。选择 `No` 会使你的身份不出现在生成的榜单和索引中，**原始公开 Issue 仍然可见**。本页自动更新真实社区概况；[英文页面](README.en.md#weekly-community-board)链接到同一概况，避免出现两份不同的数据。

## 每周最多 10 分，一点小小的鼓励

| 项目 | 最高积分 |
| --- | ---: |
| 一个有效的 Active 周计划 | 1 |
| 个人计划执行：`6 ×（完成次数 + 0.5 × 部分完成次数）/ 已确认计划次数`，保留两位小数 | 6 |
| 一条非空的周末 `/review`，与完成情况无关 | 2 |
| 经维护者认可的有用经验 Issue | 1 |
| **每周上限** | **10** |

完成已确认的替代方案计作同一次训练的完成；部分完成获得半次执行额度，跳过不计执行分。参与榜分别展示计划、执行、复盘与贡献分，衡量个人承诺的兑现和社区参与。重量、里程、时长、热量、减重、照片和发帖数量都不额外加分。积分按周重置，自愿参加，同分并列。选择 Recovery，或本人评论 `/pause`，即可让该周退出排名，不产生欠分。经验贡献审批绑定作者、所属周和完整正文，只加标签不能获得贡献分。[完整规则与纠错方式（英文）→](docs/SCORING.md)

## 交流、饮食和科研工作流

统一使用 [社区 Issues](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new/choose) 新人报到、交流训练与恢复、分享饮食、科研与 Agent 工作流、找搭子和发布活动或公告。选择相应表单后，在该 Issue 的评论中继续交流；精选资源通过文档和 PR 沉淀。社区帖及回复不会自动获得贡献分；需要申请审核时，使用[经验分享 Issue](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml)。[社区 Issue 使用说明（英文）→](docs/COMMUNITY.md)

可以自愿用 `/meal YYYY-MM-DD` 记录餐食，附文字、照片、分量、热量估算来源和不确定性。这些记录不额外加分。当前没有配置统一热量目标、自动模型估算或餐食健康评分；饮食细节和身体数据始终选填。[饮食记录示例 →](docs/MEMBER_GUIDE.zh-CN.md)

分享 Agent 工作流时，推荐写：**原任务 → Agent 分担了什么 → 检查与返工 → 实际净节时 → 是否把时间留给了运动或休息**。积分由明确规则的 Python 工具计算；可选 AI 总结需要人工审核。[Agent 指南（英文）→](docs/AGENT_GUIDE.md)

## 参与原则与启用方式

诚实、友善，尊重不同的身体、训练基础与生活安排。休息和重新开始都欢迎。不要强迫训练、索要照片、公开保密科研资料、未经许可分享他人信息，或发布广告。公开 Issue、评论、图片和提交历史可能被复制与保留；不参加排名不会让记录变成私密。

维护者完成设置后，报告流程会在相关 Issue／评论变化后，以及**每天北京时间 09:15**更新当前和上一报告周，GitHub 的定时任务可能延迟。报告周按北京时间选择，每次打卡日期按成员所填时区解释，历史报告允许纠正。仓库权限与计分标签需要[手工设置（英文）](docs/SETUP.md)，社区 Issue 表单需要合并到默认分支后使用。当前没有连接外部 AI 模型或微信群采集器。

[中文参与指南](docs/MEMBER_GUIDE.zh-CN.md) · [贡献指南（英文）](CONTRIBUTING.md) · [行为准则（英文）](CODE_OF_CONDUCT.md) · [维护者设置（英文）](docs/SETUP.md)
