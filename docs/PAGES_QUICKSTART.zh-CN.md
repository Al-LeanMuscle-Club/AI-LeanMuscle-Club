# 成员辅助页：GitHub Pages 启用指南

本仓库的打卡辅助页是静态网页，不需要部署后端或公开任何 GitHub Token。它用于查找自己的长期打卡帖、准备每天的工作/运动打卡文字和查看 100 分制周榜；不会代替用户发帖。

## 维护者启用步骤

1. 仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。
2. 在 Actions 中手动运行 **Publish optional member helper**，检查 build 与 deploy 两个 Job 均成功。
3. 部署成功后，打开 Actions Job 中显示的 Pages URL。网站根路径会跳转到 `/tools/`。
4. 如果希望每次相关变更后自动发布，在 Settings → Secrets and variables → Actions → Variables 中新增 `PUBLISH_MEMBER_HELPER=true`。
5. 部署成功后，`update-entry` Job 先检查英文首页 `README.md` 和中文首页 `README.zh-CN.md`，再将两者的成员工具链接改为本次部署返回的正式地址。`README.en.md` 仅保留旧链接导航。部署前链接指向启用说明，不会把源码页或未上线地址当成成员工具。
6. 打开首页中的成员工具链接，验证手机上能准备 `/checkin YYYY-MM-DD W=1 E=0` 文字，并打开自己的打卡帖自行发布。仓库 About 的 Website 可填写同一正式地址。

## 部署内容

Pages 构建只复制 `tools/` 和 `reports/`，并建立跳转到 `/tools/` 的根目录入口。不会发布 `examples/`、`data/ranking-state.json`、`.club-cache` 或原始 Issue 数据。

构建阶段会检查网页 JS、HTML 和 `reports/daily/index.json` 的存在与 JSON 有效性。辅助页只读取新的 v3 周榜，不把旧的 10 分制历史记录放进 100 分制榜单。没有真人公开记录时应显示空状态。

## 常见情况

- **README 指向 GitHub 源码**：点击仓库内的 `tools/index.html` 只会展示源文件。应使用 Pages 部署后的 URL。
- **workflow 被跳过**：这是仓库默认 opt-in 的行为。先手动运行一次；自动发布需设置 `PUBLISH_MEMBER_HELPER=true`。
- **部署成功但 README 未更新**：检查 `update-entry` Job；若默认分支保护禁止机器人直接提交，可将部署摘要中的地址手动填入上述两份完整首页末尾的 `[member-helper]:` 定义，再提交 PR。
- **周榜空白**：先确认 `reports/daily/index.json` 生成成功，再检查成员是否创建了有效打卡帖、选择 Yes 并发出有效评论，最后检查 Pages 是否发布了最新报告。
- **手机无法自动复制**：选中文本手动复制到原始 GitHub Issue；工具不自动提交。
- **Fork**：每个 Fork 的 Pages 域名与仓库路径不同，请以本仓库 Actions 真实部署结果为准。

更多维护细节见 [SETUP.md](SETUP.md)。

Pages 首次启用属于仓库设置，合并代码不会自动替代 Settings → Pages 的选择。工作流只在部署成功后更新入口；失败不会写入假定的网址。
