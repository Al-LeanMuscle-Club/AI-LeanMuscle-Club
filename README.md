# AI 薄肌俱乐部 💪🤖

[English](README.en.md) | **简体中文**

<!-- README:LANG=zh-CN -->
<!-- README:COMMUNITY-FIRST -->

**练模型，也练身体。**

面向 AI 科研人员的社区：每天记录工作与运动，每周看看自己的坚持，也交流真实经验。

**[建立我的打卡帖](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=daily-checkin.yml) · [分享经验](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml) · [随便聊聊](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=community-chat.yml)**

## 怎么打卡

1. 每人建一个长期 Issue，选好时区；想进入公开周榜时，把 **Public leaderboard** 选为 **Yes**（默认 No）。
2. 每天在自己的 Issue 下评论一行，`W` 表示是否工作、`E` 表示是否运动，`1` 是、`0` 否：

   ```text
   /checkin 2026-10-26 W=1 E=0
   ```

3. 周榜每天北京时间 **09:15** 定时更新。每周一至周日分别累计工作和运动天数，同一天重复打卡只算一次，以最新有效记录为准。

<a id="member-helper"></a>

[打卡辅助页][member-helper]可以帮你找自己的帖子、生成打卡文字、查看周榜。你检查后自行发布，页面不会代发。

## 周榜

<a id="每周社区概况"></a>

工作天数记为 $W$，运动天数记为 $E$，每周得分为：

$$
S = 100 \sqrt{\min(W/5, 1) \cdot \min(E/4, 1)}
$$

工作满 5 天、运动满 4 天即为 100 分；任一项为 0，得分为 0。它记录自报的参与，不比较工作时长、运动量或身体状态。[完整规则](docs/SCORING.md)

<!-- CLUB:START -->

新公式的周榜将在首次定时统计后显示。[查看周榜与历史](reports/daily/README.md)。

<!-- CLUB:END -->

<a id="news"></a>

## News · 精选经验分享

来自社区成员的亲身尝试。点击标题阅读完整经历，也欢迎在原帖下提问、交流自己的做法。

- **[减肥 30kg 的经验分享 · #35](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/35)** — [@rentainhe](https://github.com/rentainhe)：从喜欢的篮球开始，分享逐渐建立运动和饮食习惯的经历。另有[经验整理：从喜欢的运动开始](docs/experiences/2026-10-24-rentainhe.md)。
- **[让 agent 跑实验，我下楼练一会 · #44](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/44)** — [@Aaronhuang-778](https://github.com/Aaronhuang-778)：分享如何利用 Agent 运行任务的间隙去运动，并为休息保留空间。
- **[Early Bird 理论概述与实践 · #42](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/42)** — [@ChawDoe](https://github.com/ChawDoe)：从结伴吃早餐和群内接龙出发，讲述 EarlyBird 社团帮助成员建立规律作息的实践。
- **[赶 DDL 过程中如何 WLB · #41](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/41)** — [@EasonXiao-888](https://github.com/EasonXiao-888)：分享忙周保留少量活动、照顾吃饭与休息，以及忙完后逐步找回生活节奏的尝试。

欢迎直接在这些原帖下回复，也可以[分享自己的经历](https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/new?template=experience.yml)。经验分享与交流不额外加分。

所有 Issue 和评论都公开；不上榜也不会隐藏原帖。[成员指南](docs/MEMBER_GUIDE.zh-CN.md) · [参与原则](CODE_OF_CONDUCT.md) · [维护者设置](docs/SETUP.md)

[member-helper]: docs/PAGES_QUICKSTART.zh-CN.md
