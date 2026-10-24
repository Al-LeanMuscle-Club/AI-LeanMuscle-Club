/* Local helpers only: no credentials, telemetry, or automatic GitHub writes. */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else {
    root.ClubTools = api;
    api.mount(root.document);
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DEFAULT_REPOSITORY = "Al-LeanMuscle-Club/AI-LeanMuscle-Club";
  const SPORTS = ["strength", "basketball", "running", "swimming", "cycling", "walking", "mobility", "other"];
  const GOALS = ["fat-loss", "muscle-gain", "cardio", "skill", "habit"];
  const SPORT_LABELS = {strength:"力量", basketball:"篮球", running:"跑步", swimming:"游泳", cycling:"骑行", walking:"步行", mobility:"活动恢复", other:"其他"};
  const GOAL_LABELS = {"fat-loss":"减脂", "muscle-gain":"增肌", cardio:"心肺", skill:"运动技能", habit:"保持习惯"};
  const COMMANDS = ["done", "fallback", "partial", "skip", "meal"];
  const ALL_COMMAND_LINES = /^\s*\/(?:done|fallback|partial|skip|meal|review|pause)(?:\s|$)/im;
  const HANDLE = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/;

  function repository(value) {
    const result = String(value || "").trim();
    if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(result) || result.length > 220 || result.split("/").some(part => part === "." || part === "..")) {
      throw new Error("请填写 owner/name 格式的 GitHub 仓库。");
    }
    return result;
  }

  function handle(value) {
    const result = String(value || "").trim().replace(/^@/, "");
    if (!HANDLE.test(result)) throw new Error("请填写有效的 GitHub 用户名。");
    return result;
  }

  function isoDate(value, requireMonday = false) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error("请选择 YYYY-MM-DD 格式的日期。");
    const date = new Date(value + "T00:00:00.000Z");
    if (!Number.isFinite(date.getTime()) || date.getUTCFullYear() < 1 || date.toISOString().slice(0, 10) !== value) throw new Error("请选择有效的日历日期。");
    if (requireMonday && date.getUTCDay() !== 1) throw new Error("Week starting must be a Monday / 请选择周一。");
    return value;
  }

  function issueNumber(value, repo = null) {
    let text = String(value || "").trim();
    if (text.startsWith("https://")) {
      const url = new URL(text);
      const match = /^\/([^/]+\/[^/]+)\/issues\/([1-9][0-9]*)$/.exec(url.pathname);
      if (url.origin !== "https://github.com" || !match || url.search || url.hash || url.username || url.password ||
          (repo !== null && match[1].toLowerCase() !== repository(repo).toLowerCase())) {
        throw new Error("请粘贴当前仓库的完整 Issue 链接，或直接填写编号。");
      }
      text = match[2];
    }
    if (!/^[1-9][0-9]*$/.test(text) || !Number.isSafeInteger(Number(text))) throw new Error("请填写有效的 Issue 编号或链接。");
    return text;
  }

  function sessionId(value) {
    const id = String(value || "").trim().toUpperCase();
    if (!/^S[1-9][0-9]?$/.test(id)) throw new Error("训练编号应为 S1 至 S99。");
    return id;
  }

  function searchUrl(repo, username, week) {
    const query = 'is:issue label:weekly-plan author:' + handle(username) + ' in:body "' + isoDate(week, true) + '"';
    return "https://github.com/" + repository(repo) + "/issues?q=" + encodeURIComponent(query);
  }

  function freeRecordSearchUrl(repo, username, label) {
    if (!["activity-record", "meal-record"].includes(label)) throw new Error("请选择自由运动或饮食记录。");
    const query = "is:issue label:" + label + " author:" + handle(username) + " sort:created-desc";
    return "https://github.com/" + repository(repo) + "/issues?q=" + encodeURIComponent(query);
  }

  function issueUrl(repo, number) {
    return "https://github.com/" + repository(repo) + "/issues/" + issueNumber(number, repo);
  }

  function safeIssueUrl(value) {
    try {
      const parsed = new URL(value);
      if (parsed.protocol !== "https:" || parsed.hostname !== "github.com" || parsed.port || parsed.username || parsed.password || parsed.search || parsed.hash) return null;
      const match = /^\/([^/]+\/[^/]+)\/issues\/([1-9][0-9]*)$/.exec(parsed.pathname);
      if (!match) return null;
      return issueUrl(match[1], match[2]);
    } catch (_) {
      return null;
    }
  }

  function buildComment({status, session, date, notes = ""}) {
    if (!COMMANDS.includes(status)) throw new Error("请选择支持的记录类型。");
    const day = isoDate(date);
    const text = String(notes).replace(/\r\n?/g, "\n").trim();
    if (ALL_COMMAND_LINES.test(text)) throw new Error("每条评论只放一个命令，请删除记录里的其他命令行。");
    const command = status === "meal" ? "/meal " + day : "/" + status + " " + sessionId(session) + " " + day;
    return command + (text ? "\n" + text : "");
  }

  function parsePlan(text) {
    const normalized = String(text || "").replace(/\r\n?/g, "\n");
    const matches = [...normalized.matchAll(/^###[ \t]+(.+?)[ \t]*$/gm)];
    const sections = [];
    const seen = new Set();
    for (let i = 0; i < matches.length; i++) {
      const heading = matches[i][1];
      if (seen.has(heading)) throw new Error("计划字段标题有重复，请使用原 Issue 的 Markdown 正文。");
      seen.add(heading);
      sections.push({heading, value: normalized.slice(matches[i].index + matches[i][0].length, i + 1 < matches.length ? matches[i + 1].index : normalized.length).trim()});
    }
    for (const heading of ["Week starting", "Time zone", "Participation mode", "Public leaderboard", "Planned sessions"]) {
      if (!seen.has(heading)) throw new Error("请粘贴周计划 Issue 的 Markdown 正文，保留 ### 字段标题。");
    }
    return sections;
  }

  function carryPlan(text, week) {
    const target = isoDate(week, true);
    const sections = parsePlan(text);
    for (const section of sections) {
      if (section.heading === "Week starting") section.value = target;
      if (section.heading === "Public leaderboard") section.value = "No";
      if (section.heading === "Planned sessions") {
        section.value = section.value.replace(/^[ \t]*(?:-[ \t]+)?\[[ xX]\][ \t]*/gm, "");
      }
    }
    return sections.map(section => "### " + section.heading + "\n\n" + section.value).join("\n\n") + "\n";
  }

  function displayNumber(value, max = Infinity) {
    return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= max ? value : null;
  }

  function count(value, max = Infinity) {
    return Number.isSafeInteger(value) && displayNumber(value, max) !== null ? value : null;
  }

  function timestamp(value) {
    return typeof value === "string" && /^\d{4}-\d{2}-\d{2}T/.test(value) && Number.isFinite(Date.parse(value)) ? value : null;
  }

  function scoringVersion(value) {
    return count(value) > 0 ? value : null;
  }

  function scoringLabel(value) {
    const version = scoringVersion(value);
    return version === null ? "规则版本未记录 · 保留原分数" : "评分规则 v" + version + (version === 2 ? "" : " · 保留原分数");
  }

  function scoringExplanation(value) {
    const version = scoringVersion(value);
    if (version === 2) return "评分规则 v2：执行分 = 6 ×（整次完成 + 0.5 × 部分完成）÷ 已确认计划次数。替代完成计入整次完成；饮食记录不加分。确认后删除计划项不会缩小计分分母；贡献分还需匹配审批记录。";
    if (version === null) return "该报告的规则版本未记录。历史分数和完成比例保留原样，未按当前公式重算。";
    return "该报告标注评分规则 v" + version + "，本页尚无该版本的公式说明。分数与完成比例按原报告显示。";
  }

  function reportWeeks(data) {
    if (!data || data.schema_version !== 2 || !Array.isArray(data.weeks)) throw new Error("公开报告暂不支持当前格式，请稍后再试。");
    const seen = new Set();
    return data.weeks.filter(week => {
      if (!week || typeof week !== "object") return false;
      try { isoDate(week.week_start, true); } catch (_) { return false; }
      if (seen.has(week.week_start) || !Array.isArray(week.leaderboard)) return false;
      seen.add(week.week_start);
      return true;
    }).sort((a, b) => b.week_start.localeCompare(a.week_start));
  }

  function publicRows(data) {
    const rows = [];
    const seen = new Set();
    for (const week of reportWeeks(data)) {
      for (const row of week.leaderboard) {
        if (!row || typeof row !== "object" || !HANDLE.test(row.handle || "")) continue;
        const url = safeIssueUrl(row.issue_url);
        const planned = count(row.planned, 14);
        const completed = count(row.completed, 14);
        const confirmed = count(row.confirmed_planned, 14) ?? planned;
        const current = count(row.current_planned, 14) ?? planned;
        if (!url || planned === null || confirmed === null || confirmed < 1 || current === null || completed === null || completed > confirmed || displayNumber(row.total_points, 10) === null) continue;
        const key = week.week_start + "/" + row.handle.toLowerCase();
        if (seen.has(key)) continue;
        seen.add(key);
        const sessions = [];
        for (const session of Array.isArray(row.sessions) ? row.sessions : []) {
          if (!session || !/^S[1-9][0-9]?$/.test(session.id || "") || !SPORTS.includes(session.sport) || !["planned", "completed", "fallback", "partial", "skipped"].includes(session.status)) continue;
          let day = null;
          try { if (session.date !== null && session.date !== undefined) day = isoDate(session.date); } catch (_) { continue; }
          sessions.push({id:session.id, day:["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].includes(session.day) ? session.day : "", sport:session.sport,
            status:session.status, date:day, used_fallback:session.used_fallback === true,
            confirmed:typeof session.confirmed === "boolean" ? session.confirmed : null});
        }
        rows.push({
          week: week.week_start, handle: row.handle, issue_url: url,
          rank: count(row.rank) > 0 ? row.rank : null,
          generated_at: timestamp(week.generated_at),
          scoring_version: scoringVersion(week.scoring_version),
          goal: GOALS.includes(row.goal) ? row.goal : "habit",
          research_week: ["regular", "deadline", "travel"].includes(row.research_week) ? row.research_week : "regular",
          sports: Array.isArray(row.sports) ? [...new Set(row.sports.filter(sport => SPORTS.includes(sport)))] : [],
          completed, planned, confirmed_planned:confirmed, current_planned:current,
          has_confirmed_plan:count(row.confirmed_planned, 14) !== null,
          plan_changed:row.plan_changed === true,
          completion_rate:displayNumber(row.completion_rate, 1),
          execution_rate:displayNumber(row.execution_rate, 1),
          partial:count(row.partial, 14) ?? 0, skipped:count(row.skipped, 14) ?? 0,
          points:row.total_points, total_points:row.total_points,
          plan_points:displayNumber(row.plan_points, 1), execution_points:displayNumber(row.execution_points, 6),
          review_points:displayNumber(row.review_points, 2), contribution_points:displayNumber(row.contribution_points, 1),
          recorded_training_days:count(row.recorded_training_days, 7), meal_days:count(row.meal_days, 7),
          sessions,
        });
      }
    }
    return rows.sort((a, b) => b.week.localeCompare(a.week) || b.points - a.points ||
      (a.rank ?? Infinity) - (b.rank ?? Infinity) || a.handle.toLowerCase().localeCompare(b.handle.toLowerCase()));
  }

  function filterRows(rows, filters) {
    const member = String(filters.handle || "").trim().replace(/^@/, "").toLowerCase();
    return rows.filter(row => (!filters.week || row.week === filters.week) && (!member || row.handle.toLowerCase().includes(member)) && (!filters.sport || row.sports.includes(filters.sport)) && (!filters.goal || row.goal === filters.goal));
  }

  function memberSummary(rows, username) {
    const member = String(username || "").trim().replace(/^@/, "").toLowerCase();
    const selected = [];
    const seen = new Set();
    for (const row of rows) {
      if (!member || row.handle.toLowerCase() !== member || seen.has(row.week)) continue;
      seen.add(row.week);
      selected.push(row);
    }
    selected.sort((a, b) => b.week.localeCompare(a.week));
    const knownTraining = selected.filter(row => count(row.recorded_training_days, 7) !== null);
    const knownMeals = selected.filter(row => count(row.meal_days, 7) !== null);
    return {rows:selected, weeks:seen.size,
      training_days:knownTraining.length ? knownTraining.reduce((sum, row) => sum + row.recorded_training_days, 0) : null,
      meal_days:knownMeals.length ? knownMeals.reduce((sum, row) => sum + row.meal_days, 0) : null,
      training_weeks_known:knownTraining.length, meal_weeks_known:knownMeals.length};
  }

  function localDate(date = new Date()) {
    return [date.getFullYear(), String(date.getMonth() + 1).padStart(2, "0"), String(date.getDate()).padStart(2, "0")].join("-");
  }

  function weekDates(date = new Date()) {
    const monday = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7));
    const next = new Date(monday);
    next.setDate(next.getDate() + 7);
    return {current: localDate(monday), next: localDate(next)};
  }

  function mount(doc) {
    if (!doc) return;
    const get = id => doc.getElementById(id);
    const value = id => get(id).value;
    const setMessage = (id, text, error = false) => {
      get(id).textContent = text;
      get(id).classList.toggle("error", error);
    };
    const dates = weekDates();
    get("find-week").value = dates.current;
    get("carry-week").value = dates.next;
    get("log-date").value = localDate();
    get("log-today").addEventListener("click", () => {
      get("log-date").value = localDate();
      setMessage("log-message", "日期已设为今天；补记之前的运动可自行修改日期。");
    });

    get("find-form").addEventListener("submit", event => {
      event.preventDefault();
      get("find-link").hidden = true;
      try {
        get("find-link").href = searchUrl(value("repository"), value("find-handle"), value("find-week"));
        get("find-link").hidden = false;
        setMessage("find-message", "搜索链接已准备好，点击下方链接查看 GitHub 上的计划。");
      } catch (error) { setMessage("find-message", error.message, true); }
    });

    const statusHelp = {
      done: "整次完成按 1 次计入执行分。同一训练编号只计一次；可以附上内容、时长和感受。",
      fallback: "该次训练已声明的替代方案按 1 次完成计分，仍使用原训练编号。未声明的替代方案不会计为完成。",
      partial: "部分完成按 0.5 次计入执行分。最新有效状态覆盖旧状态，不会重复累加。",
      skip: "跳过会保留记录，不计执行分，也没有欠账。以后可以重新开始。",
      meal: "记录吃了什么、可选分量和感受，发布时可在 GitHub 添加照片。同一天多餐只算一个饮食记录日，不增加参与分。",
    };
    function updateStatus() {
      const status = value("log-status");
      get("log-session").disabled = status === "meal";
      get("status-help").textContent = statusHelp[status];
      get("log-result").hidden = true;
      setMessage("log-message", "");
    }
    get("log-status").addEventListener("change", updateStatus);
    updateStatus();
    for (const [id, status] of [["plan-workout", "done"], ["plan-meal", "meal"]]) {
      get(id).addEventListener("click", () => {
        get("log-status").value = status;
        updateStatus();
      });
    }
    get("log-form").addEventListener("submit", event => {
      event.preventDefault();
      get("log-result").hidden = true;
      try {
        const url = issueUrl(value("repository"), value("log-issue"));
        get("log-output").value = buildComment({status: value("log-status"), session: value("log-session"), date: value("log-date"), notes: value("log-notes")});
        get("log-link").href = url;
        get("log-result").hidden = false;
        setMessage("log-message", "文字已在浏览器中生成。检查日期和训练编号，复制后到自己的 GitHub 计划评论区发布。");
      } catch (error) { setMessage("log-message", error.message, true); }
    });

    get("carry-form").addEventListener("submit", event => {
      event.preventDefault();
      get("carry-result").hidden = true;
      try {
        get("carry-output").value = carryPlan(value("carry-source"), value("carry-week"));
        get("carry-result").hidden = false;
        setMessage("carry-message", "草稿已生成，公开排名选项已重置为 No。请检查每个字段，再创建下一周的计划。");
      } catch (error) { setMessage("carry-message", error.message, true); }
    });

    async function copy(output, message) {
      const element = get(output);
      try {
        if (!globalThis.navigator.clipboard) throw new Error("Clipboard unavailable");
        await globalThis.navigator.clipboard.writeText(element.value);
        setMessage(message, "已复制。请粘贴到 GitHub，检查后点击发布。");
      } catch (_) {
        element.focus();
        element.select();
        setMessage(message, "当前环境无法自动复制，文字已选中，请手动复制。");
      }
    }
    get("copy-log").addEventListener("click", () => copy("log-output", "log-message"));
    get("copy-carry").addEventListener("click", () => copy("carry-output", "carry-message"));

    let rows = [];
    let weeks = [];
    let availableWeeks = [];
    let olderError = "";
    const shownNumber = value => value === null || value === undefined ? "未记录" : String(value);
    const shownTime = value => timestamp(value) ? new Date(value).toLocaleString("zh-CN", {timeZone:"Asia/Shanghai", hour12:false}) + "（北京时间）" : "未提供生成时间";
    const progress = row => row.completed + " 整次 + " + row.partial + " 部分 / " + row.confirmed_planned + (row.has_confirmed_plan ? " 已确认" : " 原计划");
    function cell(tr, label, text) {
      const td = doc.createElement("td");
      td.setAttribute("data-label", label);
      if (text !== undefined) td.textContent = text;
      tr.append(td);
      return td;
    }
    function note(element, text) {
      const small = doc.createElement("small");
      small.textContent = text;
      element.append(small);
    }
    function source(td, row) {
      const a = doc.createElement("a");
      a.textContent = "查看计划 ↗";
      a.href = row.issue_url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      td.append(a);
    }
    function renderReports() {
      const selectedWeek = value("filter-week");
      const matching = selectedWeek ? filterRows(rows, {week:selectedWeek, handle:value("filter-handle"), sport:value("filter-sport"), goal:value("filter-goal")}) : [];
      get("ranking-body").replaceChildren();
      get("ranking-table").hidden = !matching.length;
      for (const row of matching.slice(0, 100)) {
        const tr = doc.createElement("tr");
        cell(tr, "原周榜名次", row.rank === null ? "未提供" : "#" + row.rank);
        const member = cell(tr, "成员", "@" + row.handle);
        note(member, GOAL_LABELS[row.goal] + " · " + (row.sports.map(sport => SPORT_LABELS[sport]).join(" / ") || "未分类"));
        const execution = cell(tr, "计划完成情况", progress(row));
        const rate = row.execution_rate ?? row.completion_rate;
        if (rate !== null) note(execution, (row.execution_rate !== null ? "报告计分比例 " : "报告完整完成比例 ") + Math.round(rate * 10000) / 100 + "%");
        const score = cell(tr, "参与分 / 10");
        const total = doc.createElement("strong");
        total.textContent = row.points + " 分";
        score.append(total);
        note(score, "计划 " + shownNumber(row.plan_points) + " · 执行 " + shownNumber(row.execution_points) + " · 复盘 " + shownNumber(row.review_points) + " · 分享 " + shownNumber(row.contribution_points));
        const plan = cell(tr, "计划状态", !row.has_confirmed_plan ? "旧报告 · 原计划" : row.plan_changed ? "计划已调整" : "按已确认计划");
        note(plan, row.has_confirmed_plan ? "当前 " + row.current_planned + " 次 · 计分分母 " + row.confirmed_planned + " 次" : "原报告计划 " + row.planned + " 次");
        const pending = row.sessions.filter(session => session.confirmed === false).length;
        if (pending) note(plan, pending + " 项尚未确认，不进入执行分");
        source(cell(tr, "来源"), row);
        get("ranking-body").append(tr);
      }
      const week = weeks.find(item => item.week_start === selectedWeek);
      get("report-snapshot").textContent = week ? "所选周 " + selectedWeek + " · 快照生成于 " + shownTime(week.generated_at) + "。更早周的分数更正需单独重算；网站完成发布后才会显示更新。" : "报告发布后，这里会显示所选周的快照生成时间。";
      get("score-guide").hidden = !week || scoringVersion(week.scoring_version) !== 2;
      get("report-rules").textContent = week ? scoringExplanation(week.scoring_version) : "报告载入后会显示该周的评分规则；历史分数按原报告保留，不重新推算。";
      const message = !weeks.length ? "还没有可展示的公开周报。你仍可用上方工具创建计划、找计划和准备打卡。" : matching.length ? "所选周找到 " + matching.length + " 位公开成员，按整周参与分排列，相同总分并列。" + (matching.length > 100 ? " 当前显示前 100 位，请缩小筛选范围查看其他成员。" : "") : rows.some(row => row.week === selectedWeek) ? "当前筛选没有匹配成员，可以清空用户名、运动或目标筛选。" : "本周暂时没有同意公开且处于 Active 状态的记录。";
      setMessage("report-message", message);
    }
    function renderHistory() {
      const username = value("history-handle").trim();
      const summary = memberSummary(rows, username);
      get("member-stats").replaceChildren();
      get("member-stats").hidden = !summary.weeks;
      get("history-body").replaceChildren();
      get("history-table").hidden = !summary.weeks;
      if (summary.weeks) {
        for (const [label, number, detail] of [
          ["公开参与周", summary.weeks, "已加载报告中的周数"],
          ["训练记录日", summary.training_days, "有天数数据 " + summary.training_weeks_known + " / " + summary.weeks + " 周"],
          ["饮食记录日", summary.meal_days, "有天数数据 " + summary.meal_weeks_known + " / " + summary.weeks + " 周 · 不加分"],
        ]) {
          const stat = doc.createElement("div");
          const strong = doc.createElement("strong");
          strong.textContent = shownNumber(number);
          const title = doc.createElement("span");
          title.textContent = label;
          stat.append(strong, title);
          note(stat, detail);
          get("member-stats").append(stat);
        }
        for (const row of summary.rows) {
          const tr = doc.createElement("tr");
          cell(tr, "报告周", row.week);
          cell(tr, "当周名次", row.rank === null ? "未提供" : "#" + row.rank);
          cell(tr, "计划完成情况", progress(row));
          cell(tr, "参与分 / 10", String(row.points));
          cell(tr, "训练日", shownNumber(row.recorded_training_days));
          cell(tr, "饮食日", shownNumber(row.meal_days));
          const td = cell(tr, "来源与快照");
          source(td, row);
          note(td, shownTime(row.generated_at));
          note(td, scoringLabel(row.scoring_version));
          get("history-body").append(tr);
        }
      }
      setMessage("history-message", !username ? "输入完整 GitHub 用户名查看自己的记录。仅统计已加载的公开周计划报告，自由记录不在此汇总。" : summary.weeks ? "@" + summary.rows[0].handle + " · 已找到 " + summary.weeks + " 个公开参与周。中断、未公开或尚未加载的周不会补成 0。" : "已加载报告中没有该用户名的公开记录。请检查完整用户名，也可以载入更早周报或用上方工具找计划。");
    }
    function renderFreeRecords() {
      const username = value("history-handle").trim();
      get("free-record-links").hidden = true;
      if (!username) {
        setMessage("free-record-message", "输入完整用户名后，可到 GitHub 回顾自己的自由运动和饮食记录，无须参加周榜。");
        return;
      }
      try {
        get("free-activity-link").href = freeRecordSearchUrl(value("repository"), username, "activity-record");
        get("free-meal-link").href = freeRecordSearchUrl(value("repository"), username, "meal-record");
        get("free-record-links").hidden = false;
        setMessage("free-record-message", "链接已准备好，包含打开和已关闭的记录。这些记录不加分，也不并入上方周计划统计。");
      } catch (error) { setMessage("free-record-message", error.message, true); }
    }
    function updateData() {
      rows = publicRows({schema_version:2, weeks});
      const selected = value("filter-week");
      get("filter-week").replaceChildren();
      for (const week of weeks) {
        const option = doc.createElement("option");
        option.value = week.week_start;
        option.textContent = week.week_start + " 开始的一周";
        get("filter-week").append(option);
      }
      get("filter-week").value = weeks.some(week => week.week_start === selected) ? selected : weeks[0]?.week_start || "";
      const loaded = new Set(weeks.map(week => week.week_start));
      const remaining = availableWeeks.filter(week => !loaded.has(week));
      get("load-older").hidden = !remaining.length;
      get("load-older").textContent = "载入更早的 " + Math.min(12, remaining.length) + " 周";
      get("history-window").textContent = "已加载 " + weeks.length + " / " + availableWeeks.length + " 个报告周" + (weeks.length ? "（" + weeks[weeks.length - 1].week_start + " 至 " + weeks[0].week_start + "）" : "") + "。仅统计同意公开的 Active 周计划记录，自由记录不在此汇总；旧报告缺少的天数显示“未记录”。" + olderError;
      renderReports();
      renderHistory();
    }
    for (const id of ["filter-week", "filter-handle", "filter-sport", "filter-goal"]) get(id).addEventListener(id === "filter-handle" ? "input" : "change", renderReports);
    get("history-handle").addEventListener("input", renderHistory);
    get("history-handle").addEventListener("input", renderFreeRecords);
    get("repository").addEventListener("input", renderFreeRecords);
    get("repository").addEventListener("change", renderFreeRecords);
    renderFreeRecords();

    async function fetchReport(path) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);
      try {
        const response = await fetch(path, {signal:controller.signal, credentials:"omit"});
        if (!response.ok) throw new Error("报告暂不可读");
        return await response.json();
      } finally { clearTimeout(timeout); }
    }
    get("load-older").addEventListener("click", async () => {
      get("load-older").disabled = true;
      get("load-older").textContent = "正在读取较早的公开周报…";
      const loaded = new Set(weeks.map(week => week.week_start));
      const batch = availableWeeks.filter(week => !loaded.has(week)).slice(0, 12);
      const results = await Promise.allSettled(batch.map(async week => {
        const board = await fetchReport("../reports/" + isoDate(week, true) + ".json");
        if (board.week_start !== week || !reportWeeks({schema_version:2, weeks:[board]}).length) throw new Error("报告周不匹配");
        return board;
      }));
      let failed = 0;
      for (const result of results) {
        if (result.status === "fulfilled") weeks.push(result.value);
        else failed++;
      }
      weeks = reportWeeks({schema_version:2, weeks});
      olderError = failed ? " 有 " + failed + " 个较早周报读取失败，可以再次点击重试；现有记录已保留。" : "";
      get("load-older").disabled = false;
      updateData();
    });
    async function loadReports() {
      if (globalThis.location && globalThis.location.protocol === "file:") {
        setMessage("report-message", "直接打开本地 HTML 无法读取报告，请使用 GitHub Pages 或本地网页服务器。上方找计划和文字工具仍可使用。");
        return;
      }
      try {
        const index = await fetchReport("../reports/index.json");
        weeks = reportWeeks(index);
        const validAvailable = [];
        for (const week of Array.isArray(index.available_weeks) ? index.available_weeks : []) {
          try { validAvailable.push(isoDate(week, true)); } catch (_) { /* Ignore invalid archive filenames. */ }
        }
        availableWeeks = [...new Set([...weeks.map(week => week.week_start), ...validAvailable])].sort().reverse();
        updateData();
      } catch (_) {
        setMessage("report-message", "暂时无法读取公开报告。报告可能尚未生成或部署，也可能是网络问题；可以稍后刷新。上方找计划和文字工具仍可使用。", true);
      }
    }
    loadReports();
  }

  return {DEFAULT_REPOSITORY, SPORTS, GOALS, repository, handle, isoDate, issueNumber, sessionId, searchUrl, freeRecordSearchUrl, issueUrl, safeIssueUrl, buildComment, parsePlan, carryPlan, scoringVersion, scoringLabel, scoringExplanation, reportWeeks, publicRows, filterRows, memberSummary, localDate, weekDates, mount};
});
