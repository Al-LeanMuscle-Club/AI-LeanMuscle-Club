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

test("invalid or injected repository, username, date and issue inputs are rejected", () => {
  for (const value of ["https://github.com/a/b", "a/b?x=1", "../b", "a/..", "a/b/extra", "a/b\n&token=x"]) assert.throws(() => tools.repository(value));
  for (const value of ["a author:someone", "-invalid", "someone/else", "a\nlabel:x"]) assert.throws(() => tools.handle(value));
  for (const value of ["2026-02-30", "0000-01-03", "2026-2-1", "today", "2026-10-26\ncommand"]) assert.throws(() => tools.isoDate(value));
  assert.throws(() => tools.isoDate("2026-10-27", true));
  assert.equal(tools.isoDate("2028-02-29"), "2028-02-29");
  for (const value of ["0", "-1", "1?comment=2", "Infinity", "9007199254740993"]) assert.throws(() => tools.issueNumber(value));
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
  constructor() { this.children=[]; this.listeners={}; this.value=""; this.hidden=false; this.disabled=false; this.attributes={}; this.text=""; this.classes=new Set(); this.classList={toggle:(name,on)=>on ? this.classes.add(name) : this.classes.delete(name)}; }
  set textContent(text) { this.text=String(text); this.children=[]; }
  get textContent() { return this.text + this.children.map(child=>child.textContent).join(""); }
  setAttribute(name,value) { this.attributes[name]=String(value); }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.text=""; this.children=[...children]; }
  addEventListener(name,listener) { (this.listeners[name] ||= []).push(listener); }
  async fire(name) { for (const listener of this.listeners[name] || []) await listener({preventDefault(){}}); }
  focus() {}
  select() {}
}
function pageDocument() {
  const html=fs.readFileSync(path.join(__dirname,"../tools/index.html"),"utf8");
  const elements=new Map();
  for (const match of html.matchAll(/<[^>]+\bid="([^"]+)"[^>]*>/g)) {
    assert(!elements.has(match[1]), "duplicate page ID " + match[1]);
    const element=new Element();
    element.hidden=/\bhidden(?:\s|>)/.test(match[0]);
    element.value=/\bvalue="([^"]*)"/.exec(match[0])?.[1] || "";
    element.href=/\bhref="([^"]*)"/.exec(match[0])?.[1] || "";
    elements.set(match[1],element);
  }
  elements.get("log-status").value="done";
  return {getElementById:id=>elements.get(id),createElement:()=>new Element()};
}
async function mountedPage(index, archives={}) {
  const originalFetch=globalThis.fetch;
  const originalLocation=globalThis.location;
  const calls=[];
  globalThis.location={protocol:"https:"};
  globalThis.fetch=async url=>{
    calls.push(url);
    const body=url==="../reports/index.json" ? index : archives[url];
    return {ok:body!==undefined,json:async()=>body};
  };
  const doc=pageDocument();
  tools.mount(doc);
  await new Promise(resolve=>setImmediate(resolve));
  return {doc,calls,restore(){globalThis.fetch=originalFetch;if(originalLocation===undefined)delete globalThis.location;else globalThis.location=originalLocation;}};
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
