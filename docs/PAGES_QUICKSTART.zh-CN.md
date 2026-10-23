# 成员辅助页：GitHub Pages 启用指南

本仓库的成员辅助页是静态网页，不需要部署后端或公开任何 GitHub Token。它用于准备打卡内容、查找周计划和查看已公开的参与报告；不会代替用户发帖。

## 维护者启用步骤

1. 仓库 Settings → Pages → Build and deployment → Source 选择 **GitHub Actions**。
2. 在 Actions 中手动运行 **Publish optional member helper**，检查 build 与 deploy 两个 Job 均成功。
3. 部署成功后，打开 Actions Job 中显示的 Pages URL。网站根路径会跳转到 `/tools/`。
4. 如果希望每次相关变更后自动发布，在 Settings → Secrets and variables → Actions → Variables 中新增 `PUBLISH_MEMBER_HELPER=true`。
5. **确认站点可用后**，再把正式在线地址补充到仓库 README，切勿把尚未启用的站点写成“已上线”。

## 部署内容

Pages 构建只复制 `tools/`、`reports/`、`examples/`，并建立简短的根目录入口。不会发布 `data/ranking-state.json`、`.club-cache` 或原始 Issue 数据。

构建阶段会检查网页 JS、HTML 和 `reports/index.json` 的存在与 JSON 有效性。没有真人公开记录时应显示空状态，不要把示例排行榜当成真实记录。

## 常见情况

- **README 指向 GitHub 源码**：点击仓库内的 `tools/index.html` 只会展示源文件。应使用 Pages 部署后的 URL。
- **workflow 被跳过**：这是仓库默认 opt-in 的行为。先手动运行一次；自动发布需设置 `PUBLISH_MEMBER_HELPER=true`。
- **周榜空白**：先确认 `reports/index.json` 生成成功，再检查 Pages 发布是否成功。
- **手机无法自动复制**：选中文本手动复制到原始 GitHub Issue；工具不自动提交。
- **Fork**：每个 Fork 的 Pages 域名与仓库路径不同，请以本仓库 Actions 真实部署结果为准。

更多维护细节见 [SETUP.md](SETUP.md)。
