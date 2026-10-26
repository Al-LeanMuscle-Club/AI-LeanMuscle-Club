"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const tools = require("../tools/app.js");

test("find plan search includes author, week and both open/closed issues", () => {
  const url = new URL(tools.searchUrl("example/club", "@Researcher-1", "2026-10-26"));
  assert.equal(url.origin, "https://github.com");
  assert.equal(url.pathname, "/example/club/issues");
  assert.equal(url.searchParams.get("q"), 'is:issue label:weekly-plan author:Researcher-1 in:body "2026-10-26"');
  assert(!url.searchParams.get("q").includes("is:open"));
});

test("free record search targets an author's activity or meal issues, including closed records", () => {
  for (const label of ["activity-record", "meal-record"]) {
    const url = new URL(tools.freeRecordSearchUrl("example/club", "@Researcher-1", label));
    assert.equal(url.origin, "https://github.com");
    assert.equal(url.pathname, "/example/club/issues");
    assert.equal(url.searchParams.get("q"), "is:issue label:" + label + " author:Researcher-1 sort:created-desc");
    assert(!/is:(?:open|closed)|state:/.test(url.searchParams.get("q")));
  }
  assert.throws(() => tools.freeRecordSearchUrl("example/club", "Alice", "weekly-plan"));
  assert.throws(() => tools.freeRecordSearchUrl("example/club", "Alice author:Bob", "meal-record"));
  assert.throws(() => tools.freeRecordSearchUrl("example/club?token=x", "Alice", "activity-record"));
});

test("community searches include unlabelled real posts and exclude labelled and titled examples", () => {
  for (const topic of ["all", "activity", "experience", "meal", "buddies", "research", "hello"]) {
    const url = new URL(tools.communitySearchUrl("example/club", topic));
    const query = url.searchParams.get("q");
    assert.equal(url.pathname, "/example/club/issues");
    assert.match(query, /is:issue in:title -label:example/);
    for (const marker of ['-"Fictional example"', '-虚构']) assert(query.includes(marker));
    assert(!query.includes("is:open"));
    assert(!/(?:^| )label:/.test(query), "new posts must be discoverable before label repair");
  }
  assert.match(new URL(tools.communitySearchUrl("example/club", "activity")).searchParams.get("q"), /"\[Activity\]"/);
  assert.match(new URL(tools.communitySearchUrl("example/club", "experience")).searchParams.get("q"), /"\[Experience\]"/);
  assert.throws(() => tools.communitySearchUrl("example/club", "all author:other"));
});

test("quick activity drafts preserve actual inputs in the existing GitHub form without privileged parameters", () => {
  const input = {date:"2026-10-21",timeZone:"Asia/Shanghai",sport:"basketball",text:"今天打球，想问个问题：A&B?\n之后再补照片。"};
  const draft = tools.activityDraft("example/club", input);
  const url = new URL(draft.url);
  assert.equal(url.origin, "https://github.com");
  assert.equal(url.pathname, "/example/club/issues/new");
  assert.equal(url.searchParams.get("template"), "activity-record.yml");
  assert.equal(url.searchParams.get("activity-date"), input.date);
  assert.equal(url.searchParams.get("time-zone"), input.timeZone);
  assert(!url.searchParams.has("sport"), "GitHub documents prefills for text fields, not dropdowns");
  assert.equal(url.searchParams.get("activity"), input.text);
  assert.equal(url.searchParams.get("title"), "[Activity] 2026-10-21 · 篮球");
  assert(!url.searchParams.has("labels"));
  assert(!url.searchParams.has("assignees"));
  assert.match(draft.body, /### Sport\n\nbasketball/);
  assert(draft.body.endsWith(input.text + "\n"));
  assert(!draft.body.includes("Public leaderboard"));
  for (const changed of [{date:"2026-02-30"},{timeZone:"Asia/Fake"},{timeZone:""},{sport:"basketball&labels=points-approved"},{text:""},{text:"x".repeat(501)}]) assert.throws(() => tools.activityDraft("example/club", {...input,...changed}));
  const template = fs.readFileSync(path.join(__dirname,"../.github/ISSUE_TEMPLATE/activity-record.yml"),"utf8");
  for (const id of ["activity-date","time-zone","sport","activity"]) assert(template.includes("id: " + id));
});

test("casual experience sharing does not require a scoring week", () => {
  const template = fs.readFileSync(path.join(__dirname,"../.github/ISSUE_TEMPLATE/experience.yml"),"utf8");
  const week = template.split("id: week-starting")[1].split("  - type:")[0];
  assert.match(week, /required: false/);
  assert.match(week, /周一/);
  assert.match(template.split("id: context")[1].split("  - type:")[0], /required: true/);
});

test("invalid or injected repository, username, date and issue inputs are rejected", () => {
  for (const value of ["https://github.com/a/b", "a/b?x=1", "../b", "a/..", "a/b/extra", "a/b\n&token=x"]) assert.throws(() => tools.repository(value));
  for (const value of ["a author:someone", "-invalid", "someone/else", "a\nlabel:x"]) assert.throws(() => tools.handle(value));
  for (const value of ["2026-02-30", "0000-01-03", "2026-2-1", "today", "2026-10-26\ncommand"]) assert.throws(() => tools.isoDate(value));
  assert.throws(() => tools.isoDate("2026-10-27", true));
  assert.equal(tools.isoDate("2028-02-29"), "2028-02-29");
  for (const value of ["0", "-1", "1?comment=2", "Infinity", "9007199254740993"]) assert.throws(() => tools.issueNumber(value));
});

test("mobile check-in accepts safe GitHub issue links and rejects wrong repositories", () => {
  assert.equal(tools.issueUrl("example/club", "https://github.com/example/club/issues/123"), "https://github.com/example/club/issues/123");
  assert.equal(tools.issueUrl("example/club", "123"), "https://github.com/example/club/issues/123");
  for (const value of ["https://github.com/other/club/issues/123", "https://github.com/example/club/issues/123?x=1",
    "https://github.com/example/club/issues/123#comment", "http://github.com/example/club/issues/123",
    "https://github.com.evil.test/example/club/issues/123"]) {
    assert.throws(() => tools.issueUrl("example/club", value));
  }
});

test("comment generation preserves notes, validates sessions and cannot embed extra commands", () => {
  assert.equal(tools.buildComment({status:"done",session:"s2",date:"2026-10-27",notes:"Strength, 30 min.\r\nFelt good."}), "/done S2 2026-10-27\nStrength, 30 min.\nFelt good.");
  for (const status of ["fallback", "partial", "skip"]) assert.equal(tools.buildComment({status,session:"S1",date:"2026-10-27"}), "/" + status + " S1 2026-10-27");
  assert.equal(tools.buildComment({status:"meal",session:"ignored",date:"2026-10-27",notes:"Lunch, portions estimated."}), "/meal 2026-10-27\nLunch, portions estimated.");
  for (const notes of ["/pause", "Notes.\n  /DONE S3 2026-10-27", "/meal 2026-10-27"]) assert.throws(() => tools.buildComment({status:"done",session:"S1",date:"2026-10-27",notes}));
  assert.throws(() => tools.buildComment({status:"done",session:"S0",date:"2026-10-27"}));
  assert.throws(() => tools.buildComment({status:"review",session:"S1",date:"2026-10-27"}));
});

test("carry-over resets consent, removes completed check marks, preserves schedule and context", () => {
  const plan = "### Week starting\n\n2026-10-26\n\n### Time zone\n\nAsia/Shanghai\n\n### Participation mode\n\nActive\n\n### Public leaderboard\n\nYes\n\n### Primary goal\n\nmuscle-gain\n\n### Planned sessions\n\n- [x] S1 | Monday | strength | 30 min | 10 min at home\n- [ ] S2 | Friday | basketball | Skills\n\n### Notes\n\nReview my old context.";
  const draft = tools.carryPlan(plan.replace(/\n/g, "\r\n"), "2026-11-02");
  assert.match(draft, /### Week starting\n\n2026-11-02/);
  assert.match(draft, /### Public leaderboard\n\nNo/);
  assert(!draft.includes("[x]"));
  assert(!draft.includes("[ ]"));
  assert.match(draft, /S1 \| Monday \| strength \| 30 min \| 10 min at home/);
  assert.match(draft, /muscle-gain/);
  assert.match(draft, /Review my old context/);
  assert.throws(() => tools.carryPlan(plan + "\n### Public leaderboard\n\nYes", "2026-11-02"));
  assert.throws(() => tools.carryPlan("Missing issue form fields", "2026-11-02"));
});

test("report handling only selects safe known fields, validates links, sorts and filters history", () => {
  const alice = {handle:"Alice",issue_url:"https://github.com/example/club/issues/1",goal:"muscle-gain",sports:["strength","basketball","unknown"],completed:2,planned:3,total_points:7,notes:"NEVER_COPY_THIS",meals:[{calories:500}]};
  const older = {...alice,issue_url:"https://github.com/example/club/issues/2",goal:"habit",sports:["walking"]};
  const data = {schema_version:2,weeks:[{week_start:"2026-10-19",leaderboard:[older]},{week_start:"2026-10-26",leaderboard:[alice,{...alice,issue_url:"javascript:alert(1)"},{...alice,issue_url:"https://github.com.evil.example/a/b/issues/1"},{...alice,total_points:100},{...alice,completed:4}]}]};
  const rows = tools.publicRows(data);
  assert.equal(rows.length, 2);
  assert.equal(rows[0].week, "2026-10-26");
  assert(!JSON.stringify(rows).includes("NEVER_COPY_THIS"));
  assert(!JSON.stringify(rows).includes("calories"));
  assert.equal(tools.filterRows(rows,{handle:"@ali",sport:"basketball",goal:"muscle-gain"}).length, 1);
  assert.equal(tools.filterRows(rows,{handle:"someone-else"}).length, 0);
  for (const url of ["http://github.com/a/b/issues/1", "https://evil.example/a/b/issues/1", "https://github.com/a/b/issues/1?x=1", "https://user@github.com/a/b/issues/1", "https://github.com/a/b/issues/1#x"]) assert.equal(tools.safeIssueUrl(url), null);
  assert.throws(() => tools.publicRows({weeks:[]}));
});

test("Monday defaults work across Sunday, Monday and year boundaries", () => {
  assert.deepEqual(tools.weekDates(new Date(2026,9,25,12)), {current:"2026-10-19",next:"2026-10-26"});
  assert.deepEqual(tools.weekDates(new Date(2026,9,26,12)), {current:"2026-10-26",next:"2026-11-02"});
  assert.deepEqual(tools.weekDates(new Date(2027,0,1,12)), {current:"2026-12-28",next:"2027-01-04"});
});

function publicPlan(handle, rank, points, extra = {}) {
  return {handle, rank, total_points:points, issue_url:"https://github.com/example/club/issues/1", planned:4, completed:2,
    confirmed_planned:4, current_planned:4, plan_changed:false, completion_rate:0.5, execution_rate:0.625,
    partial:1, skipped:0, plan_points:1, execution_points:3.75, review_points:2, contribution_points:0,
    goal:"habit", sports:["running"], recorded_training_days:3, meal_days:2,
    sessions:[{id:"S1", day:"Monday", sport:"running", status:"completed", date:"2026-10-26", used_fallback:false, confirmed:true}],
    ...extra};
}

test("weekly leaderboard preserves backend ties, score breakdown and confirmed-plan fields", () => {
  const data = {schema_version:2, weeks:[{week_start:"2026-10-26", generated_at:"2026-11-01T12:00:00Z", leaderboard:[
    publicPlan("Aaron", 3, 3),
    publicPlan("Zulu", 1, 6.75, {plan_changed:true, current_planned:3}),
    publicPlan("Bella", 1, 6.75),
  ]}]};
  const rows = tools.publicRows(data);
  assert.deepEqual(rows.map(row => [row.handle,row.rank,row.points]), [["Bella",1,6.75],["Zulu",1,6.75],["Aaron",3,3]]);
  const zulu = rows.find(row => row.handle === "Zulu");
  assert.equal(zulu.plan_points,1);
  assert.equal(zulu.execution_points,3.75);
  assert.equal(zulu.review_points,2);
  assert.equal(zulu.contribution_points,0);
  assert.equal(zulu.confirmed_planned,4);
  assert.equal(zulu.current_planned,3);
  assert.equal(zulu.plan_changed,true);
  assert.equal(zulu.execution_rate,0.625);
  assert.equal(zulu.sessions[0].confirmed,true);
  assert.equal(zulu.generated_at,"2026-11-01T12:00:00Z");
  const filtered = tools.filterRows(rows,{week:"2026-10-26",handle:"Zulu",sport:"running"});
  assert.equal(filtered[0].rank,1);
  assert.equal(filtered[0].points,6.75);
});

test("week and sport filters retain original whole-week scores and ranks", () => {
  const old = {week_start:"2026-10-19", leaderboard:[publicPlan("Alice",1,9)]};
  const current = {week_start:"2026-10-26", leaderboard:[publicPlan("Alice",7,6,{sports:["strength","running"]}),publicPlan("Bob",1,9)]};
  const rows = tools.publicRows({schema_version:2,weeks:[old,current]});
  const matching = tools.filterRows(rows,{week:"2026-10-26",sport:"strength"});
  assert.equal(matching.length,1);
  assert.equal(matching[0].week,"2026-10-26");
  assert.equal(matching[0].rank,7);
  assert.equal(matching[0].points,6);
  assert.deepEqual(tools.filterRows(rows,{week:"2026-11-02"}),[]);
});

test("personal summaries use exact public handles, distinct weeks and recorded day counts", () => {
  const rows = tools.publicRows({schema_version:2,weeks:[
    {week_start:"2026-10-26",leaderboard:[publicPlan("Alice",1,7,{recorded_training_days:3,meal_days:2}),publicPlan("Alice-2",2,6,{recorded_training_days:7,meal_days:7})]},
    {week_start:"2026-10-19",leaderboard:[publicPlan("ALICE",2,6,{recorded_training_days:2,meal_days:0})]},
  ]});
  const summary = tools.memberSummary([...rows,rows[0]],"@aLiCe");
  assert.equal(summary.weeks,2);
  assert.equal(summary.training_days,5);
  assert.equal(summary.meal_days,2);
  assert.equal(summary.training_weeks_known,2);
  assert.equal(summary.meal_weeks_known,2);
  assert.deepEqual(summary.rows.map(row => row.week),["2026-10-26","2026-10-19"]);
  assert.equal(tools.memberSummary(rows,"Ali").weeks,0);
  assert.equal(tools.memberSummary(rows,"").training_days,null);
});

test("legacy and missing report fields stay unknown instead of inventing counts or ranks", () => {
  const legacy = {handle:"Alice",issue_url:"https://github.com/example/club/issues/1",planned:3,completed:2,total_points:7};
  const rows = tools.publicRows({schema_version:2,weeks:[
    {week_start:"2026-10-26",leaderboard:[publicPlan("Alice",1,7,{recorded_training_days:0,meal_days:0})]},
    {week_start:"2026-10-19",leaderboard:[legacy]},
  ]});
  assert.equal(rows[1].rank,null);
  assert.equal(rows[1].confirmed_planned,3);
  assert.equal(rows[1].has_confirmed_plan,false);
  assert.equal(rows[1].execution_rate,null);
  assert.equal(rows[1].recorded_training_days,null);
  assert.equal(rows[1].meal_days,null);
  assert.equal(rows[1].execution_points,null);
  const summary = tools.memberSummary(rows,"alice");
  assert.equal(summary.weeks,2);
  assert.equal(summary.training_days,0);
  assert.equal(summary.meal_days,0);
  assert.equal(summary.training_weeks_known,1);
  assert.equal(summary.meal_weeks_known,1);
  assert.equal(tools.memberSummary([rows[1]],"Alice").meal_days,null);
});

test("scoring versions follow each report without guessing legacy rules or relabeling future rules", () => {
  const rows = tools.publicRows({schema_version:2,scoring_version:2,weeks:[
    {week_start:"2026-10-26",scoring_version:2,leaderboard:[publicPlan("Alice",1,6.75)]},
    {week_start:"2026-10-19",leaderboard:[publicPlan("Alice",1,6)]},
    {week_start:"2026-10-12",scoring_version:3,leaderboard:[publicPlan("Alice",1,6)]},
    {week_start:"2026-10-05",scoring_version:"2",leaderboard:[publicPlan("Alice",1,6)]},
  ]});
  assert.deepEqual(rows.map(row=>row.scoring_version),[2,null,3,null]);
  assert.equal(tools.memberSummary(rows,"Alice").rows[1].scoring_version,null);
  assert.match(tools.scoringLabel(2),/评分规则 v2/);
  assert.match(tools.scoringExplanation(2),/0\.5 × 部分完成/);
  assert.match(tools.scoringLabel(null),/规则版本未记录.*保留原分数/);
  assert.match(tools.scoringExplanation(undefined),/未按当前公式重算/);
  assert.match(tools.scoringLabel(3),/评分规则 v3/);
  assert.match(tools.scoringExplanation(3),/尚无该版本的公式说明/);
  for (const value of [true,0,-1,2.5,"2",{},null]) assert.equal(tools.scoringVersion(value),null);
});

test("invalid archive weeks and injected details cannot enter the public record view", () => {
  const row = publicPlan("Alice",1,7,{notes:"PRIVATE_NOTES",meal_days:99,recorded_training_days:-1,
    sessions:[{id:"S1",day:"Monday",sport:"running",status:"completed",date:"2026-10-26",confirmed:false,notes:"PRIVATE_SESSION",calories:1234}]});
  const data = {schema_version:2,weeks:[null,{week_start:"../../private",leaderboard:[row]},
    {week_start:"2026-10-26",generated_at:"bad-time",leaderboard:[row,row]},
    {week_start:"2026-10-26",leaderboard:[publicPlan("Someone",2,6)]}]};
  const weeks = tools.reportWeeks(data);
  assert.equal(weeks.length,1);
  const rows = tools.publicRows(data);
  assert.equal(rows.length,1);
  assert.equal(rows[0].meal_days,null);
  assert.equal(rows[0].recorded_training_days,null);
  assert.equal(rows[0].generated_at,null);
  assert.equal(rows[0].sessions[0].confirmed,false);
  assert(!JSON.stringify(rows).includes("PRIVATE"));
  assert(!JSON.stringify(rows).includes("calories"));
});

// Minimal DOM at the page boundary: verifies the real mount handlers without a
// browser dependency or requiring network access to community data.
class Element {
  constructor() { this.children=[]; this.listeners={}; this.value=""; this.hidden=false; this.disabled=false; this.open=false; this.parentElement=null; this.tagName=""; this.attributes={}; this.text=""; this.classes=new Set(); this.classList={toggle:(name,on)=>on ? this.classes.add(name) : this.classes.delete(name)}; }
  set textContent(text) { this.text=String(text); this.children=[]; }
  get textContent() { return this.text + this.children.map(child=>child.textContent).join(""); }
  setAttribute(name,value) { this.attributes[name]=String(value); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.text=""; this.children=[...children]; }
  addEventListener(name,listener) { (this.listeners[name] ||= []).push(listener); }
  async fire(name) { for (const listener of this.listeners[name] || []) await listener({preventDefault(){}}); }
  focus() {}
  select() {}
  closest(tag) { return this.tagName === tag.toUpperCase() ? this : this.parentElement?.closest(tag) || null; }
  scrollIntoView() { this.scrolled=true; }
}
function pageDocument() {
  const html=fs.readFileSync(path.join(__dirname,"../tools/index.html"),"utf8");
  const elements=new Map();
  const stack=[];
  const voidTags=new Set(["META","LINK","INPUT","BR","IMG","HR"]);
  for (const match of html.matchAll(/<\/?([a-z][a-z0-9-]*)\b[^>]*>/gi)) {
    const tag=match[1].toUpperCase();
    if (match[0].startsWith("</")) {
      assert.equal(stack.pop()?.tagName,tag,"page tags must nest correctly");
      continue;
    }
    const element=new Element();
    element.tagName=tag;
    element.parentElement=stack.at(-1) || null;
    element.hidden=/\bhidden(?:\s|>)/.test(match[0]);
    element.open=/\bopen(?:\s|>)/.test(match[0]);
    element.value=/\bvalue="([^"]*)"/.exec(match[0])?.[1] || "";
    element.href=/\bhref="([^"]*)"/.exec(match[0])?.[1] || "";
    const id=/\bid="([^"]+)"/.exec(match[0])?.[1];
    if (id) {
      assert(!elements.has(id), "duplicate page ID " + id);
      elements.set(id,element);
    }
    if (!voidTags.has(tag)) stack.push(element);
  }
  assert.equal(stack.length,0);
  elements.get("log-status").value="done";
  return {getElementById:id=>elements.get(id),createElement:()=>new Element()};
}
async function mountedPage(index, archives={}, {openAdvanced=true, hash=""}={}) {
  const originalFetch=globalThis.fetch;
  const originalLocation=globalThis.location;
  const calls=[];
  globalThis.location={protocol:"https:",hash};
  globalThis.fetch=async url=>{
    calls.push(url);
    const body=url==="../reports/index.json" ? index : archives[url];
    return {ok:body!==undefined,json:async()=>body};
  };
  const doc=pageDocument();
  const windowListeners={};
  doc.defaultView={location:globalThis.location,addEventListener(name,listener){(windowListeners[name] ||= []).push(listener);}};
  tools.mount(doc);
  if (openAdvanced) {
    doc.getElementById("advanced-tools").open=true;
    await doc.getElementById("advanced-tools").fire("toggle");
  }
  await new Promise(resolve=>setImmediate(resolve));
  return {doc,calls,async navigate(hash){doc.defaultView.location.hash=hash;for(const listener of windowListeners.hashchange || [])listener();await new Promise(resolve=>setImmediate(resolve));},restore(){globalThis.fetch=originalFetch;if(originalLocation===undefined)delete globalThis.location;else globalThis.location=originalLocation;}};
}

test("free-record entry links need no weekly plan and deployed helper links point to GitHub", () => {
  const doc=pageDocument();
  const repo="https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club";
  assert.equal(doc.getElementById("start-workout").href,repo + "/issues/new?template=activity-record.yml");
  assert.equal(doc.getElementById("start-meal").href,repo + "/issues/new?template=meal-record.yml");
  const html=fs.readFileSync(path.join(__dirname,"../tools/index.html"),"utf8");
  assert.match(html,/自由记录不会自动进入周榜/);
  assert.match(html,/不计入下方榜单的饮食日统计/);
  assert(html.includes('class="brand" href="'+repo+'"'));
  assert(html.includes('href="'+repo+'/blob/main/docs/SCORING.md"'));
  assert(html.includes('href="'+repo+'/tree/main/examples"'));
  assert(!html.includes('href="../docs/'));
  assert(!html.includes('href="../examples/'));
  assert(!html.includes('href="../"'));
});

test("page renders backend ranking and selected-week timestamp, then prepares a weekly-plan meal comment locally", async () => {
  const page=await mountedPage({schema_version:2,weeks:[
    {week_start:"2026-10-19",generated_at:"2026-10-25T12:00:00Z",leaderboard:[publicPlan("Alice",3,6)]},
    {week_start:"2026-10-26",generated_at:"2026-11-01T12:00:00Z",leaderboard:[publicPlan("Aaron",3,3),publicPlan("Zulu",1,6.75)]},
  ]});
  try {
    const get=page.doc.getElementById;
    assert.equal(get("start-workout").listeners.click,undefined);
    assert.equal(get("start-meal").listeners.click,undefined);
    assert.equal(get("filter-week").value,"2026-10-26");
    assert.match(get("ranking-body").children[0].textContent,/#1@Zulu/);
    assert.match(get("ranking-body").textContent,/执行 3.75/);
    assert.match(get("ranking-body").textContent,/2 整次 \+ 1 部分 \/ 4 已确认/);
    get("filter-week").value="2026-10-19";
    await get("filter-week").fire("change");
    assert.match(get("ranking-body").textContent,/#3@Alice/);
    assert.match(get("report-snapshot").textContent,/2026-10-19/);
    assert.match(get("report-snapshot").textContent,/2026\/10\/25/);
    assert(!get("report-snapshot").textContent.includes("2026/11/1"));
    await get("plan-meal").fire("click");
    assert.equal(get("log-status").value,"meal");
    assert.equal(get("log-session").disabled,true);
    assert.match(get("status-help").textContent,/不增加参与分/);
    get("log-issue").value="123";
    get("log-date").value="2026-10-26";
    get("log-notes").value="午餐：米饭、鸡肉和青菜。";
    await get("log-form").fire("submit");
    assert.equal(get("log-output").value,"/meal 2026-10-26\n午餐：米饭、鸡肉和青菜。");
    assert.equal(get("log-result").hidden,false);
    assert.equal(page.calls.length,1,"preparing a comment must not write to GitHub");
    await get("plan-workout").fire("click");
    assert.equal(get("log-status").value,"done");
    assert.equal(get("log-session").disabled,false);
  } finally {page.restore();}
});

test("mobile form accepts a pasted plan link, resets the date and keeps publishing manual", async () => {
  const page=await mountedPage({schema_version:2,weeks:[]});
  try {
    const get=page.doc.getElementById;
    const today=get("log-date").value;
    get("log-date").value="2026-10-21";
    await get("log-today").fire("click");
    assert.equal(get("log-date").value,today);
    get("log-date").value="2026-10-21";
    get("log-issue").value="https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/123";
    get("log-session").value="S2";
    get("log-notes").value="周三晚上打了篮球。";
    await get("log-form").fire("submit");
    assert.equal(get("log-result").hidden,false);
    assert.equal(get("log-link").href,get("log-issue").value);
    assert.equal(get("log-output").value,"/done S2 2026-10-21\n周三晚上打了篮球。");
    get("log-issue").value="https://github.com/other/club/issues/123";
    await get("log-form").fire("submit");
    assert.equal(get("log-result").hidden,true);
    assert.match(get("log-message").textContent,/当前仓库/);
    assert.deepEqual(page.calls,["../reports/index.json"],"drafting must not post or fetch member records");
  } finally {page.restore();}
});

test("free-record review works without leaderboard data and follows repository and author changes", async () => {
  const page=await mountedPage(undefined);
  try {
    const get=page.doc.getElementById;
    assert.equal(get("free-record-links").hidden,true);
    get("history-handle").value="@ALICE";
    await get("history-handle").fire("input");
    assert.equal(get("free-record-links").hidden,false);
    assert.equal(get("member-stats").hidden,true,"free records do not create scored participation");
    for (const [id,label] of [["free-activity-link","activity-record"],["free-meal-link","meal-record"]]) {
      const url=new URL(get(id).href);
      assert.equal(url.pathname,"/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues");
      assert.equal(url.searchParams.get("q"),"is:issue label:"+label+" author:ALICE sort:created-desc");
    }
    get("repository").value="my-org/my-club";
    await get("repository").fire("input");
    assert.equal(new URL(get("free-meal-link").href).pathname,"/my-org/my-club/issues");
    get("history-handle").value="Alice author:Bob";
    await get("history-handle").fire("input");
    assert.equal(get("free-record-links").hidden,true);
    assert.match(get("free-record-message").textContent,/有效的 GitHub 用户名/);
    get("history-handle").value="Bob";
    get("repository").value="../private";
    await get("repository").fire("change");
    assert.equal(get("free-record-links").hidden,true);
    get("repository").value="example/club";
    await get("repository").fire("change");
    assert.equal(get("free-record-links").hidden,false);
    assert.match(new URL(get("free-activity-link").href).searchParams.get("q"),/author:Bob/);
    get("history-handle").value="";
    await get("history-handle").fire("input");
    assert.equal(get("free-record-links").hidden,true);
    assert.equal(page.calls.length,1,"preparing links must not fetch member records or write to GitHub");
  } finally {page.restore();}
});

test("page explains only the selected report's declared scoring version and preserves historical points", async () => {
  const page=await mountedPage({schema_version:2,weeks:[
    {week_start:"2026-10-26",scoring_version:2,leaderboard:[publicPlan("Alice",1,6.75)]},
    {week_start:"2026-10-19",leaderboard:[publicPlan("Alice",1,6,{execution_points:3,execution_rate:null})]},
    {week_start:"2026-10-12",scoring_version:3,leaderboard:[publicPlan("Alice",1,6)]},
  ]});
  try {
    const get=page.doc.getElementById;
    assert.match(get("report-rules").textContent,/评分规则 v2：执行分 =/);
    assert.equal(get("score-guide").hidden,false);
    get("filter-week").value="2026-10-19";
    await get("filter-week").fire("change");
    assert.match(get("report-rules").textContent,/规则版本未记录/);
    assert(!get("report-rules").textContent.includes("执行分 ="));
    assert.equal(get("score-guide").hidden,true);
    assert.match(get("ranking-body").textContent,/6 分/);
    assert.match(get("ranking-body").textContent,/执行 3 ·/);
    get("filter-week").value="2026-10-12";
    await get("filter-week").fire("change");
    assert.match(get("report-rules").textContent,/评分规则 v3/);
    assert.match(get("report-rules").textContent,/尚无该版本的公式说明/);
    assert.equal(get("score-guide").hidden,true);
    get("history-handle").value="Alice";
    await get("history-handle").fire("input");
    const history=get("history-body").children;
    assert.match(history[0].textContent,/评分规则 v2/);
    assert.match(history[1].textContent,/规则版本未记录.*保留原分数/);
    assert.equal(history[1].children[3].textContent,"6");
    assert.match(history[2].textContent,/评分规则 v3/);
  } finally {page.restore();}
});

test("personal history can load older public archives without losing the selected ranking week", async () => {
  const older={schema_version:2,week_start:"2026-10-19",generated_at:"2026-10-25T12:00:00Z",leaderboard:[publicPlan("Alice",1,7,{recorded_training_days:2,meal_days:0})]};
  const page=await mountedPage({schema_version:2,available_weeks:["2026-10-26","2026-10-19","../../invalid"],weeks:[
    {week_start:"2026-10-26",generated_at:"2026-11-01T12:00:00Z",leaderboard:[publicPlan("Alice",1,7)]},
  ]},{"../reports/2026-10-19.json":older});
  try {
    const get=page.doc.getElementById;
    get("history-handle").value="@ALICE";
    await get("history-handle").fire("input");
    assert.equal(get("member-stats").children[0].children[0].textContent,"1");
    assert.equal(get("load-older").hidden,false);
    await get("load-older").fire("click");
    assert.equal(get("filter-week").value,"2026-10-26");
    assert.equal(get("load-older").hidden,true);
    assert.equal(get("member-stats").children[0].children[0].textContent,"2");
    assert.equal(get("member-stats").children[1].children[0].textContent,"5");
    assert.equal(get("member-stats").children[2].children[0].textContent,"2");
    assert.equal(get("history-body").children.length,2);
    assert.deepEqual(page.calls,["../reports/index.json","../reports/2026-10-19.json"]);
  } finally {page.restore();}
});

test("empty or unavailable public reports show honest empty states while local tools remain usable", async () => {
  for (const [index,message] of [[{schema_version:2,weeks:[],available_weeks:[]},/还没有可展示的公开周报/],[undefined,/暂时无法读取公开报告/]]) {
    const page=await mountedPage(index);
    try {
      const get=page.doc.getElementById;
      assert.match(get("report-message").textContent,message);
      assert.equal(get("ranking-table").hidden,true);
      assert.equal(get("member-stats").hidden,true);
      await get("plan-meal").fire("click");
      assert.equal(get("log-status").value,"meal");
    } finally {page.restore();}
  }
});

test("quick activity form defaults to the local date and timezone, invalidates edited drafts and leaves publishing manual", async () => {
  const page=await mountedPage(undefined);
  try {
    const get=page.doc.getElementById;
    assert.equal(get("activity-date").value,tools.localDate());
    assert.equal(get("activity-zone").value,Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC");
    assert.equal(get("activity-sport").value,"walking");
    get("activity-date").value="2026-10-21";
    get("activity-zone").value="Asia/Shanghai";
    get("activity-sport").value="basketball";
    get("activity-text").value="今天打了篮球。";
    await get("activity-form").fire("submit");
    assert.equal(get("activity-result").hidden,false);
    assert.equal(new URL(get("activity-link").href).searchParams.get("activity-date"),"2026-10-21");
    assert.match(get("activity-output").value,/### What I did\n\n今天打了篮球。/);
    assert.match(get("activity-message").textContent,/Sport.*篮球（basketball）/);
    get("activity-text").value="修改后的真实记录。";
    await get("activity-text").fire("input");
    assert.equal(get("activity-result").hidden,true,"never leave an older publish link after editing");
    await get("activity-today").fire("click");
    assert.equal(get("activity-date").value,tools.localDate());
    get("repository").value="other/club";
    await get("repository").fire("change");
    assert.equal(new URL(get("browse-community").href).pathname,"/other/club/issues");
    assert.match(new URL(get("topic-experience").href).searchParams.get("q"),/Experience/);
    await get("activity-form").fire("submit");
    assert.equal(new URL(get("activity-link").href).pathname,"/other/club/issues/new");
    get("activity-zone").value="not a timezone";
    await get("activity-form").fire("submit");
    assert.equal(get("activity-result").hidden,true);
    assert.match(get("activity-message").textContent,/时区/);
    assert.deepEqual(page.calls,["../reports/index.json"],"local drafting and browsing must not fetch or post member records");
  } finally {page.restore();}
});

test("community aggregate view follows the selected report and leaves legacy or malformed counts unknown", async () => {
  const activity={schema_version:1,timezone:"UTC",participants_count:2,posts_count:2,replies_count:1,responded_posts_count:1,activity_records:1,meal_records:0,experiences:1,conversations:0,weekly_plan_posts:0};
  const page=await mountedPage({schema_version:2,weeks:[
    {week_start:"2026-10-26",activity_updated_at:"2026-11-03T12:00:00Z",generated_at:"2026-11-01T12:00:00Z",community_activity:{...activity,private_note:"DO_NOT_RENDER"},leaderboard:[]},
    {week_start:"2026-10-19",leaderboard:[]},
    {week_start:"2026-10-12",community_activity:{...activity,participants_count:-1},leaderboard:[]},
  ]});
  try {
    const get=page.doc.getElementById;
    assert.equal(get("community-overview").hidden,false);
    assert.equal(get("community-stats").children[0].children[0].textContent,"2");
    assert.match(get("community-breakdown").textContent,/自由运动 1.*经验分享 1/);
    assert.match(get("community-breakdown").textContent,/1 个新帖已得到其他成员回复/);
    assert.match(get("community-week").textContent,/2026-10-26.*UTC/);
    assert.match(get("community-week").textContent,/社区统计更新于.*2026\/11\/3/);
    assert.match(get("report-snapshot").textContent,/2026\/11\/1/);
    assert(!get("report-snapshot").textContent.includes("2026/11/3"));
    assert(!get("community-breakdown").textContent.includes("DO_NOT_RENDER"));
    assert.equal(get("ranking-table").hidden,true,"community posting never creates ranking rows");
    for (const week of ["2026-10-19","2026-10-12"]) {
      get("filter-week").value=week;
      await get("filter-week").fire("change");
      assert.equal(get("community-overview").hidden,true);
      assert.equal(get("community-stats").children.length,0);
    }
    assert.equal(tools.communityActivity({...activity,timezone:"Asia/Shanghai"}),null);
    assert.equal(tools.communityActivity({...activity,schema_version:2}),null);
    assert.equal(tools.communityActivity({...activity,replies_count:"1"}),null);
  } finally {page.restore();}
});

test("first visit offers two community actions and an existing topic without loading optional reports", async () => {
  const page=await mountedPage(undefined,{}, {openAdvanced:false});
  try {
    const get=page.doc.getElementById;
    const repo="https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club";
    const html=fs.readFileSync(path.join(__dirname,"../tools/index.html"),"utf8");
    const hero=html.match(/<nav class="entry-grid community-entry"[^>]*>([\s\S]*?)<\/nav>/)[1];
    assert.equal((hero.match(/<a\b/g) || []).length,2);
    assert.equal(get("join-community").href,repo + "/issues/new?template=community-chat.yml");
    const chatForm=fs.readFileSync(path.join(__dirname,"../.github/ISSUE_TEMPLATE/community-chat.yml"),"utf8");
    assert.equal((chatForm.match(/type: textarea/g) || []).length,1);
    assert.equal((chatForm.match(/required: true/g) || []).length,1);
    assert(!/type: (?:input|dropdown|checkboxes)/.test(chatForm),"joining only requires the message, not dates, goals or plan choices");
    assert.equal(get("reply-featured").href,repo + "/issues/35");
    assert.equal(get("read-featured").href,repo + "/blob/main/docs/experiences/2026-10-24-rentainhe.md");
    assert.equal(get("featured-topic").closest("details"),null,"a real member topic stays visible");
    assert.equal(get("community-heading").closest("details"),null,"community conversation stays visible");
    assert.equal(get("advanced-tools").open,false);
    assert.equal(get("quick-record").open,false,"the dated activity form is optional");
    for (const id of ["find-heading","log-heading","ranking-heading","history-heading","carry-heading"]) assert.equal(get(id).closest("details"),get("advanced-tools"),id + " is inside the advanced disclosure");
    assert.deepEqual(page.calls,[],"reading community links needs no reports or member API requests");
    get("repository").value="example/club";
    await get("repository").fire("input");
    assert.equal(get("join-community").href,"https://github.com/example/club/issues/new?template=community-chat.yml");
    assert.equal(get("join-community-topic").href,get("join-community").href,"both community post links follow the selected repository");
    assert.equal(new URL(get("browse-buddies").href).pathname,"/example/club/issues");
    assert.equal(get("reply-featured").href,repo + "/issues/35","the curated source remains attributed to the original community");
  } finally {page.restore();}
});

test("advanced reports load only on opening and successful snapshots are reused", async () => {
  const page=await mountedPage({schema_version:2,weeks:[{week_start:"2026-10-26",leaderboard:[publicPlan("Alice",1,7)]}]},{},{openAdvanced:false});
  try {
    const get=page.doc.getElementById;
    assert.deepEqual(page.calls,[]);
    get("quick-record").open=true;
    await get("quick-record").fire("toggle");
    assert.deepEqual(page.calls,[],"quick free records do not need the weekly-plan data");
    get("activity-text").value="今天出去走了一会。";
    await get("activity-form").fire("submit");
    assert.equal(get("activity-result").hidden,false);
    assert.deepEqual(page.calls,[],"preparing a free record stays local");
    get("advanced-tools").open=true;
    await get("advanced-tools").fire("toggle");
    assert.deepEqual(page.calls,["../reports/index.json"]);
    assert.match(get("ranking-body").textContent,/@Alice/);
    get("advanced-tools").open=false;
    await get("advanced-tools").fire("toggle");
    get("advanced-tools").open=true;
    await get("advanced-tools").fire("toggle");
    assert.equal(page.calls.length,1,"reopening does not refetch a successful snapshot");
  } finally {page.restore();}
});

test("old deep links reveal the right optional section on arrival and subsequent navigation", async () => {
  const page=await mountedPage({schema_version:2,weeks:[]},{},{openAdvanced:false,hash:"#activity-heading"});
  try {
    const get=page.doc.getElementById;
    assert.equal(get("quick-record").open,true);
    assert.equal(get("advanced-tools").open,false);
    assert.equal(get("activity-heading").scrolled,true);
    assert.deepEqual(page.calls,[]);
    await page.navigate("#ranking-heading");
    assert.equal(get("advanced-tools").open,true);
    assert.equal(get("ranking-heading").scrolled,true);
    assert.deepEqual(page.calls,["../reports/index.json"]);
    get("advanced-tools").open=false;
    await page.navigate("#log-heading");
    assert.equal(get("advanced-tools").open,true);
    assert.equal(get("log-heading").scrolled,true);
    assert.equal(page.calls.length,1);
    await page.navigate("#%invalid");
    await page.navigate("#missing-section");
    assert.equal(page.calls.length,1);
  } finally {page.restore();}
  const direct=await mountedPage({schema_version:2,weeks:[]},{},{openAdvanced:false,hash:"#history-heading"});
  try {
    assert.equal(direct.doc.getElementById("advanced-tools").open,true);
    assert.deepEqual(direct.calls,["../reports/index.json"]);
  } finally {direct.restore();}
});
