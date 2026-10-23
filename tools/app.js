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
  const COMMANDS = ["done", "fallback", "partial", "skip", "meal"];
  const ALL_COMMAND_LINES = /^\s*\/(?:done|fallback|partial|skip|meal|review|pause)(?:\s|$)/im;
  const HANDLE = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/;

  function repository(value) {
    const result = String(value || "").trim();
    if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(result) || result.length > 220 || result.split("/").some(part => part === "." || part === "..")) {
      throw new Error("Enter a GitHub repository as owner/name.");
    }
    return result;
  }

  function handle(value) {
    const result = String(value || "").trim().replace(/^@/, "");
    if (!HANDLE.test(result)) throw new Error("Enter a valid GitHub username.");
    return result;
  }

  function isoDate(value, requireMonday = false) {
    if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error("Choose a date in YYYY-MM-DD format.");
    const date = new Date(value + "T00:00:00.000Z");
    if (!Number.isFinite(date.getTime()) || date.getUTCFullYear() < 1 || date.toISOString().slice(0, 10) !== value) throw new Error("Choose a real calendar date.");
    if (requireMonday && date.getUTCDay() !== 1) throw new Error("Week starting must be a Monday / 请选择周一。");
    return value;
  }

  function issueNumber(value) {
    const text = String(value || "").trim();
    if (!/^[1-9][0-9]*$/.test(text) || !Number.isSafeInteger(Number(text))) throw new Error("Enter a positive issue number, such as 123.");
    return text;
  }

  function sessionId(value) {
    const id = String(value || "").trim().toUpperCase();
    if (!/^S[1-9][0-9]?$/.test(id)) throw new Error("Use a session ID from S1 to S99.");
    return id;
  }

  function searchUrl(repo, username, week) {
    const query = 'is:issue label:weekly-plan author:' + handle(username) + ' in:body "' + isoDate(week, true) + '"';
    return "https://github.com/" + repository(repo) + "/issues?q=" + encodeURIComponent(query);
  }

  function issueUrl(repo, number) {
    return "https://github.com/" + repository(repo) + "/issues/" + issueNumber(number);
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
    if (!COMMANDS.includes(status)) throw new Error("Choose a supported record type.");
    const day = isoDate(date);
    const text = String(notes).replace(/\r\n?/g, "\n").trim();
    if (ALL_COMMAND_LINES.test(text)) throw new Error("Use one command per comment. Remove command lines from the notes.");
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
      if (seen.has(heading)) throw new Error("The pasted plan has duplicate field headings. Use the raw issue body.");
      seen.add(heading);
      sections.push({heading, value: normalized.slice(matches[i].index + matches[i][0].length, i + 1 < matches.length ? matches[i + 1].index : normalized.length).trim()});
    }
    for (const heading of ["Week starting", "Time zone", "Participation mode", "Public leaderboard", "Planned sessions"]) {
      if (!seen.has(heading)) throw new Error("Paste the raw Markdown of a weekly-plan issue, including its ### field headings.");
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

  function publicRows(data) {
    if (!data || data.schema_version !== 2 || !Array.isArray(data.weeks)) throw new Error("Public reports are not available in the current format yet.");
    const rows = [];
    for (const week of data.weeks) {
      try { isoDate(week.week_start, true); } catch (_) { continue; }
      if (!Array.isArray(week.leaderboard)) continue;
      for (const row of week.leaderboard) {
        if (!row || typeof row !== "object" || !HANDLE.test(row.handle || "")) continue;
        const url = safeIssueUrl(row.issue_url);
        if (!url || !Number.isSafeInteger(row.planned) || !Number.isSafeInteger(row.completed) || displayNumber(row.planned) === null || displayNumber(row.completed) === null || row.completed > row.planned || displayNumber(row.total_points, 10) === null) continue;
        rows.push({
          week: week.week_start, handle: row.handle, issue_url: url,
          goal: GOALS.includes(row.goal) ? row.goal : "habit",
          sports: Array.isArray(row.sports) ? [...new Set(row.sports.filter(sport => SPORTS.includes(sport)))] : [],
          completed: row.completed, planned: row.planned, points: row.total_points,
        });
      }
    }
    return rows.sort((a, b) => b.week.localeCompare(a.week) || a.handle.toLowerCase().localeCompare(b.handle.toLowerCase()));
  }

  function filterRows(rows, filters) {
    const member = String(filters.handle || "").trim().replace(/^@/, "").toLowerCase();
    return rows.filter(row => (!member || row.handle.toLowerCase().includes(member)) && (!filters.sport || row.sports.includes(filters.sport)) && (!filters.goal || row.goal === filters.goal));
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

    get("find-form").addEventListener("submit", event => {
      event.preventDefault();
      get("find-link").hidden = true;
      try {
        get("find-link").href = searchUrl(value("repository"), value("find-handle"), value("find-week"));
        get("find-link").hidden = false;
        setMessage("find-message", "Ready. Open the link to search GitHub.");
      } catch (error) { setMessage("find-message", error.message, true); }
    });

    const statusHelp = {
      done: "One session counts once. Optional training details may follow the command.",
      fallback: "Counts as completed only if this session already has a declared fallback in the fifth plan column. Do not create a second session ID.",
      partial: "Keeps an honest record; earns no execution points. The latest valid session status replaces the previous status.",
      skip: "Keeps an honest record; earns no execution points. Missing a session creates no debt.",
      meal: "Optional, with no extra points. Add food, portions, and estimate sources if known. Add a photo on GitHub if you wish; do not treat estimates as a health score.",
    };
    get("log-status").addEventListener("change", () => {
      const status = value("log-status");
      get("log-session").disabled = status === "meal";
      get("status-help").textContent = statusHelp[status];
      get("log-result").hidden = true;
      setMessage("log-message", "");
    });
    get("log-form").addEventListener("submit", event => {
      event.preventDefault();
      get("log-result").hidden = true;
      try {
        const url = issueUrl(value("repository"), value("log-issue"));
        get("log-output").value = buildComment({status: value("log-status"), session: value("log-session"), date: value("log-date"), notes: value("log-notes")});
        get("log-link").href = url;
        get("log-result").hidden = false;
        setMessage("log-message", "Prepared locally. Check the date, session ID, and your plan before posting.");
      } catch (error) { setMessage("log-message", error.message, true); }
    });

    get("carry-form").addEventListener("submit", event => {
      event.preventDefault();
      get("carry-result").hidden = true;
      try {
        get("carry-output").value = carryPlan(value("carry-source"), value("carry-week"));
        get("carry-result").hidden = false;
        setMessage("carry-message", "Draft ready. Leaderboard consent is No. Review every field before using the new plan.");
      } catch (error) { setMessage("carry-message", error.message, true); }
    });

    async function copy(output, message) {
      const element = get(output);
      try {
        if (!globalThis.navigator.clipboard) throw new Error("Clipboard unavailable");
        await globalThis.navigator.clipboard.writeText(element.value);
        setMessage(message, "Copied. Paste it into GitHub and review before submitting.");
      } catch (_) {
        element.focus();
        element.select();
        setMessage(message, "Clipboard unavailable here. Text selected; copy it manually.");
      }
    }
    get("copy-log").addEventListener("click", () => copy("log-output", "log-message"));
    get("copy-carry").addEventListener("click", () => copy("carry-output", "carry-message"));

    let rows = [];
    function renderReports() {
      const matching = filterRows(rows, {handle: value("filter-handle"), sport: value("filter-sport"), goal: value("filter-goal")});
      get("history-body").replaceChildren();
      get("history-table").hidden = !matching.length;
      for (const row of matching.slice(0, 100)) {
        const tr = doc.createElement("tr");
        for (const content of [row.week, "@" + row.handle, row.goal, row.sports.join(", ") || "—", row.completed + " / " + row.planned, String(row.points)]) {
          const td = doc.createElement("td");
          td.textContent = content;
          tr.append(td);
        }
        const td = doc.createElement("td");
        const a = doc.createElement("a");
        a.textContent = "Plan ↗";
        a.href = row.issue_url;
        a.target = "_blank";
        a.rel = "noopener noreferrer";
        td.append(a);
        tr.append(td);
        get("history-body").append(tr);
      }
      setMessage("report-message", matching.length ? matching.length + " matching weekly record(s), newest first." + (matching.length > 100 ? " Showing 100; refine your filters to see others." : "") : "No matching public records yet. You can still find your issue using the plan-search tool above.");
    }
    for (const id of ["filter-handle", "filter-sport", "filter-goal"]) get(id).addEventListener(id === "filter-handle" ? "input" : "change", renderReports);

    async function loadReports() {
      if (globalThis.location && globalThis.location.protocol === "file:") {
        setMessage("report-message", "Open this page on GitHub Pages or a local web server to load reports. Search links and text helpers still work locally.");
        return;
      }
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);
      try {
        const response = await fetch("../reports/index.json", {signal: controller.signal, credentials: "omit"});
        if (!response.ok) throw new Error("No published index");
        const index = await response.json();
        rows = publicRows(index);
        const timestamps = index.weeks.map(week => week.generated_at).filter(value => typeof value === "string" && /^\d{4}-\d{2}-\d{2}T/.test(value) && Number.isFinite(Date.parse(value))).sort();
        if (timestamps.length) get("report-snapshot").textContent = "Latest report refresh: " + timestamps[timestamps.length - 1] + ". This is a deployed snapshot; maintainers must republish Pages after reports change. 网页数据以最近一次发布为准。";
        renderReports();
      } catch (_) {
        setMessage("report-message", "Public reports are not available yet. Run the report workflow and deploy this repository's Pages site. The tools above work without reports.");
      } finally { clearTimeout(timeout); }
    }
    loadReports();
  }

  return {DEFAULT_REPOSITORY, SPORTS, GOALS, repository, handle, isoDate, issueNumber, sessionId, searchUrl, issueUrl, safeIssueUrl, buildComment, parsePlan, carryPlan, publicRows, filterRows, localDate, weekDates, mount};
});
