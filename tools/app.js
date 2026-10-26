/* Local drafts and public reports only; no automatic GitHub writes. */
(function (root, factory) {
  "use strict";
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else { root.ClubTools = api; api.mount(root.document); }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";
  const DEFAULT_REPOSITORY = "Al-LeanMuscle-Club/AI-LeanMuscle-Club";
  const HANDLE = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/;

  function repository(value) {
    const result = String(value || "").trim();
    if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(result) || result.length > 220 || result.split("/").some(part => part === "." || part === "..")) throw new Error("请填写 owner/name 格式的 GitHub 仓库。");
    return result;
  }
  function handle(value) {
    const result = String(value || "").trim().replace(/^@/, "");
    if (!HANDLE.test(result)) throw new Error("请填写有效的 GitHub 用户名。");
    return result;
  }
  function isoDate(value, monday = false) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error("请选择 YYYY-MM-DD 格式的日期。");
    const date = new Date(value + "T00:00:00.000Z");
    if (!Number.isFinite(date.getTime()) || date.getUTCFullYear() < 1 || date.toISOString().slice(0, 10) !== value) throw new Error("请选择有效的日历日期。");
    if (monday && date.getUTCDay() !== 1) throw new Error("报告周必须从周一开始。");
    return value;
  }
  function localDate(date = new Date()) {
    return date.getFullYear() + "-" + String(date.getMonth() + 1).padStart(2, "0") + "-" + String(date.getDate()).padStart(2, "0");
  }
  function issueNumber(value, repo = null) {
    let number = String(value || "").trim();
    if (number.startsWith("https://")) {
      const url = new URL(number);
      const match = /^\/([^/]+\/[^/]+)\/issues\/([1-9][0-9]*)$/.exec(url.pathname);
      if (url.origin !== "https://github.com" || !match || url.search || url.username || url.password || (url.hash && !/^#(?:new_comment_field|issuecomment-[1-9][0-9]*)$/.test(url.hash)) || (repo !== null && match[1].toLowerCase() !== repository(repo).toLowerCase())) throw new Error("请填写当前仓库的打卡帖编号或完整 Issue 链接。");
      number = match[2];
    }
    if (!/^[1-9][0-9]*$/.test(number) || !Number.isSafeInteger(Number(number))) throw new Error("请填写有效的 Issue 编号或链接。");
    return number;
  }
  function issueUrl(repo, number) {
    return "https://github.com/" + repository(repo) + "/issues/" + issueNumber(number, repo);
  }
  function safeIssueUrl(value) {
    try {
      const url = new URL(value);
      const match = /^\/([^/]+\/[^/]+)\/issues\/([1-9][0-9]*)$/.exec(url.pathname);
      if (url.origin !== "https://github.com" || url.username || url.password || url.search || url.hash || !match) return null;
      return issueUrl(match[1], match[2]);
    } catch (_) { return null; }
  }
  function searchUrl(repo, username) {
    const query = 'is:issue author:' + handle(username) + ' "[Check-in]" in:title -label:example -"Fictional example" -虚构 sort:created-desc';
    return "https://github.com/" + repository(repo) + "/issues?q=" + encodeURIComponent(query);
  }
  function experienceSearchUrl(repo) {
    return "https://github.com/" + repository(repo) + "/issues?q=" + encodeURIComponent('is:issue "[Experience]" in:title -label:example -"Fictional example" -虚构 sort:updated-desc');
  }
  function buildComment({date, work, exercise}) {
    if (typeof work !== "boolean" || typeof exercise !== "boolean") throw new Error("请选择当天是否工作、是否运动。");
    return "/checkin " + isoDate(date) + " W=" + Number(work) + " E=" + Number(exercise);
  }
  function timestamp(value) {
    return typeof value === "string" && /^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(value) && Number.isFinite(Date.parse(value));
  }
  function reportWeeks(index) {
    const invalid = () => { throw new Error("周报格式不兼容，请查看仓库中的打卡周报。"); };
    if (!index || index.schema_version !== 3 || index.scoring_version !== 3 || !Array.isArray(index.weeks)) invalid();
    const seenWeeks = new Set();
    const weeks = index.weeks.map(week => {
      if (!week || week.schema_version !== 3 || week.scoring_version !== 3 || !Array.isArray(week.leaderboard)) invalid();
      const start = isoDate(week.week_start, true);
      const end = new Date(start + "T00:00:00Z"); end.setUTCDate(end.getUTCDate() + 6);
      if (week.week_end !== end.toISOString().slice(0, 10) || seenWeeks.has(start) || !timestamp(week.generated_at)) invalid();
      seenWeeks.add(start);
      const seenHandles = new Set();
      const rows = week.leaderboard.map(row => {
        if (!row || typeof row.handle !== "string" || !HANDLE.test(row.handle) || seenHandles.has(row.handle.toLowerCase()) || !Number.isSafeInteger(row.rank) || row.rank < 1 || typeof row.score !== "number" || !Number.isFinite(row.score) || row.score < 0 || row.score > 100) invalid();
        if ([row.work_days, row.exercise_days, row.checkin_days].some(value => !Number.isInteger(value) || value < 0 || value > 7) || row.work_days > row.checkin_days || row.exercise_days > row.checkin_days || row.checkin_days < 1) invalid();
        const source = safeIssueUrl(row.issue_url);
        if (!source || !Number.isSafeInteger(row.issue_number) || source.split("/").at(-1) !== String(row.issue_number) || typeof row.time_zone !== "string" || !row.time_zone) invalid();
        try { new Intl.DateTimeFormat("en", {timeZone: row.time_zone}).format(); } catch (_) { invalid(); }
        seenHandles.add(row.handle.toLowerCase());
        return {rank:row.rank,handle:row.handle,issue_number:row.issue_number,issue_url:source,work_days:row.work_days,exercise_days:row.exercise_days,checkin_days:row.checkin_days,score:row.score,time_zone:row.time_zone};
      });
      if (week.participants_count !== rows.length) invalid();
      rows.sort((a, b) => a.rank - b.rank || a.handle.toLowerCase().localeCompare(b.handle.toLowerCase()));
      return {schema_version:3,scoring_version:3,week_start:start,week_end:week.week_end,generated_at:week.generated_at,participants_count:rows.length,leaderboard:rows};
    });
    return weeks.sort((a, b) => b.week_start.localeCompare(a.week_start));
  }

  function mount(doc) {
    if (!doc) return;
    const pageWindow = doc.defaultView || globalThis;
    const get = id => doc.getElementById(id);
    const message = (id, text, error = false) => { get(id).textContent = text; get(id).classList.toggle("error", error); };
    const value = id => get(id).value;
    const hideDraft = () => { get("log-result").hidden = true; message("log-message", ""); };
    const links = ["create-journal", "share-experience", "join-community", "browse-experiences"];
    function updateLinks() {
      hideDraft();
      get("find-link").hidden = true;
      message("find-message", "");
      try {
        const repo = repository(value("repository"));
        for (const [id, template] of [["create-journal", "daily-checkin.yml"], ["share-experience", "experience.yml"], ["join-community", "community-chat.yml"]]) get(id).href = "https://github.com/" + repo + "/issues/new?template=" + template;
        get("browse-experiences").href = experienceSearchUrl(repo);
        links.forEach(id => get(id).removeAttribute("aria-disabled"));
        message("repository-message", "");
      } catch (error) {
        links.forEach(id => { get(id).removeAttribute("href"); get(id).setAttribute("aria-disabled", "true"); });
        message("repository-message", error.message, true);
      }
    }
    get("repository").addEventListener("input", updateLinks);
    get("repository").addEventListener("change", updateLinks);
    updateLinks();
    get("log-date").value = localDate();
    get("log-today").addEventListener("click", () => { get("log-date").value = localDate(); hideDraft(); });
    for (const id of ["log-issue", "log-date", "log-work", "log-exercise"]) {
      get(id).addEventListener("input", hideDraft);
      get(id).addEventListener("change", hideDraft);
    }
    get("log-form").addEventListener("submit", event => {
      event.preventDefault(); hideDraft();
      try {
        const href = issueUrl(value("repository"), value("log-issue"));
        const comment = buildComment({date:value("log-date"),work:get("log-work").checked,exercise:get("log-exercise").checked});
        get("log-output").value = comment;
        get("log-link").href = href + "#new_comment_field";
        get("log-result").hidden = false;
        message("log-message", "已生成。复制后到自己的打卡帖粘贴、检查并发布。");
      } catch (error) { message("log-message", error.message, true); }
    });
    get("copy-log").addEventListener("click", async () => {
      if (get("log-result").hidden) return;
      try {
        if (!pageWindow.navigator?.clipboard?.writeText) throw new Error("Clipboard unavailable");
        await pageWindow.navigator.clipboard.writeText(value("log-output"));
        message("log-message", "已复制。请粘贴到 GitHub，检查后自行发布。");
      } catch (_) {
        get("log-output").focus(); get("log-output").select();
        message("log-message", "当前环境无法自动复制，文字已选中，请手动复制。");
      }
    });
    get("find-handle").addEventListener("input", () => { get("find-link").hidden = true; message("find-message", ""); });
    get("find-form").addEventListener("submit", event => {
      event.preventDefault(); get("find-link").hidden = true;
      try {
        get("find-link").href = searchUrl(value("repository"), value("find-handle"));
        get("find-link").hidden = false;
        message("find-message", "查找包括已关闭的帖子；打卡请使用自己的最新打卡帖，并保持该帖开放。");
      } catch (error) { message("find-message", error.message, true); }
    });

    let weeks = [];
    function renderReport() {
      get("ranking-body").replaceChildren();
      get("ranking-table").hidden = true;
      const week = weeks.find(item => item.week_start === value("filter-week"));
      if (!week) return;
      const time = new Date(week.generated_at).toLocaleString("zh-CN", {timeZone:"Asia/Shanghai", hour12:false});
      get("report-snapshot").textContent = week.week_start + " 至 " + week.week_end + " · 更新于 " + time + "（北京时间）";
      message("report-message", week.leaderboard.length ? "本周 " + week.leaderboard.length + " 位成员公开上榜。" : "本周还没有公开打卡记录。可以建立自己的打卡帖，选择是否参加榜单。");
      for (const row of week.leaderboard) {
        const tr = doc.createElement("tr");
        for (const [label, text] of [["名次", "#" + row.rank], ["成员", "@" + row.handle], ["工作天数", row.work_days], ["运动天数", row.exercise_days], ["得分 / 100", row.score.toFixed(2)]]) {
          const td = doc.createElement("td"); td.setAttribute("data-label", label); td.textContent = String(text); tr.append(td);
        }
        const td = doc.createElement("td"); td.setAttribute("data-label", "打卡帖");
        const link = doc.createElement("a"); link.href = row.issue_url; link.textContent = "#" + row.issue_number + " ↗"; link.target = "_blank"; link.rel = "noopener noreferrer"; td.append(link); tr.append(td);
        get("ranking-body").append(tr);
      }
      get("ranking-table").hidden = !week.leaderboard.length;
    }
    get("filter-week").addEventListener("change", renderReport);
    async function loadReports() {
      get("retry-reports").hidden = true;
      get("retry-reports").disabled = true;
      get("filter-week").disabled = true;
      get("ranking-table").hidden = true;
      get("ranking-body").replaceChildren();
      get("report-snapshot").textContent = "";
      message("report-message", "正在读取公开周报…");
      try {
        if (pageWindow.location?.protocol === "file:") throw new Error("请通过已部署的网站或本地网页服务器打开，才能读取周报；打卡文字仍可在本页生成。");
        const fetcher = pageWindow.fetch ? pageWindow.fetch.bind(pageWindow) : globalThis.fetch;
        const response = await fetcher("../reports/daily/index.json");
        if (!response.ok) throw new Error("公开打卡周报尚未生成或暂时无法读取，请稍后重试。");
        weeks = reportWeeks(await response.json());
        get("filter-week").replaceChildren();
        for (const week of weeks) { const option = doc.createElement("option"); option.value = week.week_start; option.textContent = week.week_start + " 起的一周"; get("filter-week").append(option); }
        if (!weeks.length) {
          const option = doc.createElement("option"); option.value = ""; option.textContent = "暂无打卡周报"; get("filter-week").append(option); get("filter-week").value = "";
          message("report-message", "还没有打卡周报。首次定时统计后会在这里显示。每日打卡文字现在就可以准备。");
        } else { get("filter-week").disabled = false; get("filter-week").value = weeks[0].week_start; renderReport(); }
      } catch (error) {
        weeks = [];
        message("report-message", error instanceof Error ? error.message : "暂时无法读取周报，请稍后重试。", true);
        get("retry-reports").hidden = false;
      } finally { get("retry-reports").disabled = false; }
    }
    get("retry-reports").addEventListener("click", loadReports);
    function revealHash() {
      let id; try { id = decodeURIComponent((pageWindow.location?.hash || "").slice(1)); } catch (_) { return; }
      const target = get(id); if (!target) return;
      let parent = target.closest("details");
      while (parent) { parent.open = true; parent = parent.parentElement?.closest("details"); }
      target.scrollIntoView?.({block:"start"});
    }
    pageWindow.addEventListener?.("hashchange", revealHash);
    revealHash();
    loadReports();
  }
  return {DEFAULT_REPOSITORY, repository, handle, isoDate, localDate, issueNumber, issueUrl, safeIssueUrl, searchUrl, experienceSearchUrl, buildComment, reportWeeks, mount};
});
