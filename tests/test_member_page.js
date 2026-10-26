"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const tools = require("../tools/app.js");

function row(handle = "ExampleMember", overrides = {}) {
  return {rank:1,handle,issue_number:12,issue_url:"https://github.com/example/club/issues/12",work_days:5,exercise_days:1,checkin_days:5,score:50,time_zone:"Asia/Shanghai",...overrides};
}
function week(weekStart = "2026-10-26", rows = [row()]) {
  const end = new Date(weekStart + "T00:00:00Z"); end.setUTCDate(end.getUTCDate() + 6);
  return {schema_version:3,scoring_version:3,week_start:weekStart,week_end:end.toISOString().slice(0,10),generated_at:"2026-11-02T01:15:00Z",participants_count:rows.length,leaderboard:rows};
}
function index(weeks = []) { return {schema_version:3,scoring_version:3,available_weeks:weeks.map(w=>w.week_start),weeks}; }

test("daily check-ins express all four work/exercise states without extra commands", () => {
  for (const [work, exercise, expected] of [[false,false,"W=0 E=0"],[true,false,"W=1 E=0"],[false,true,"W=0 E=1"],[true,true,"W=1 E=1"]]) {
    assert.equal(tools.buildComment({date:"2026-10-26",work,exercise}),"/checkin 2026-10-26 " + expected);
  }
  for (const input of [{work:1,exercise:true},{work:"0",exercise:false},{work:true,exercise:null},{work:true,exercise:true,date:"2026-10-26\n/checkin 2026-10-27 W=1 E=1"}]) {
    assert.throws(()=>tools.buildComment({date:"2026-10-26",...input}));
  }
});

test("dates use the local calendar, including month/year boundaries and leap days", () => {
  assert.equal(tools.localDate(new Date(2026,11,31,23,59)),"2026-12-31");
  assert.equal(tools.localDate(new Date(2027,0,1,0,1)),"2027-01-01");
  assert.equal(tools.isoDate("2028-02-29"),"2028-02-29");
  for (const value of ["2026-02-29","2026-02-30","2026-13-01","0000-01-01","2026-1-1","tomorrow","2026-10-26\n"]) assert.throws(()=>tools.isoDate(value));
  assert.throws(()=>tools.isoDate("2026-10-27",true));
});

test("journal search finds an author's unlabelled open and closed check-in issues", () => {
  const url = new URL(tools.searchUrl("example/club","@Researcher-1"));
  assert.equal(url.pathname,"/example/club/issues");
  assert.equal(url.searchParams.get("q"),'is:issue author:Researcher-1 "[Check-in]" in:title -label:example -"Fictional example" -虚构 sort:created-desc');
  assert(!/is:(open|closed)|label:daily-checkin|weekly-plan/.test(url.searchParams.get("q")));
  const experience = new URL(tools.experienceSearchUrl("example/club")).searchParams.get("q");
  assert(experience.includes('"[Experience]" in:title'));
  assert(experience.includes('-label:example'));
});

test("repository, username and issue inputs cannot inject queries or redirect to another host", () => {
  for (const value of ["https://github.com/a/b","a/b?x=1","a/b/extra","../b","a/..","a/b\n&labels=admin"]) assert.throws(()=>tools.repository(value));
  for (const value of ["a author:Bob","@a label:admin","a\nb","-abc","<script>"]) assert.throws(()=>tools.handle(value));
  for (const value of ["0","-1","1?x=1","9007199254740993","https://github.com/other/club/issues/12","https://github.com.evil.test/example/club/issues/12","https://user@github.com/example/club/issues/12","javascript:alert(1)","https://github.com/example/club/issues/12?labels=admin"]) assert.throws(()=>tools.issueUrl("example/club",value));
  assert.equal(tools.issueUrl("example/club","https://github.com/example/club/issues/12#new_comment_field"),"https://github.com/example/club/issues/12");
  assert.equal(tools.issueUrl("example/club","12"),"https://github.com/example/club/issues/12");
  for (const value of ["javascript:alert(1)","https://github.com.evil.test/example/club/issues/12","https://github.com/example/club/issues/12?x=1","https://github.com/example/club/issues/12#x"]) assert.equal(tools.safeIssueUrl(value),null);
});

test("v3 reports preserve declared ranks, ties and scores while stripping arbitrary metadata", () => {
  const report = week("2026-10-26",[row("Zulu",{rank:3,score:0,work_days:0,exercise_days:1,checkin_days:1}),row("Bob",{notes:"PRIVATE_NOTES",comments:["RAW_COMMENT"]}),row("Alice")]);
  const reports = tools.reportWeeks(index([week("2026-10-19",[]),report]));
  assert.deepEqual(reports.map(r=>r.week_start),["2026-10-26","2026-10-19"]);
  assert.deepEqual(reports[0].leaderboard.map(r=>[r.handle,r.rank,r.score]),[["Alice",1,50],["Bob",1,50],["Zulu",3,0]]);
  assert(!JSON.stringify(reports).includes("PRIVATE_NOTES"));
  assert(!JSON.stringify(reports).includes("RAW_COMMENT"));
  assert.deepEqual(report.leaderboard.map(r=>r.handle),["Zulu","Bob","Alice"],"reader must not mutate the supplied snapshot");
});

test("old 10-point reports and mixed or malformed weekly snapshots cannot become a 100-point board", () => {
  for (const changed of [{schema_version:2},{scoring_version:2},{scoring_version:"3"},{weeks:null}]) assert.throws(()=>tools.reportWeeks({...index([week()]),...changed}));
  for (const changed of [{scoring_version:2},{schema_version:2},{week_start:"2026-10-27"},{week_end:"2026-11-02"},{generated_at:"not-a-date"},{generated_at:"2026-11-02T01:15:00"},{participants_count:3}]) {
    assert.throws(()=>tools.reportWeeks(index([{...week(),...changed}])));
  }
  assert.throws(()=>tools.reportWeeks(index([week(),week()])));
  assert.deepEqual(tools.reportWeeks(index()),[]);
});

test("malicious or impossible report rows are rejected before DOM rendering", () => {
  for (const changed of [{handle:'<img src=x onerror=alert(1)>'},{rank:0},{score:101},{score:"50"},{score:NaN},{work_days:8},{exercise_days:-1},{checkin_days:0},{work_days:6},{issue_url:"javascript:alert(1)"},{issue_number:13},{time_zone:"Asia/Fake"}]) assert.throws(()=>tools.reportWeeks(index([week("2026-10-26",[row("Alice",changed)])])));
  assert.throws(()=>tools.reportWeeks(index([week("2026-10-26",[row("Alice"),row("alice")])])));
  assert.equal(tools.reportWeeks(index([week("2026-10-26",[row("Capped",{work_days:7,exercise_days:7,checkin_days:7,score:100})])]))[0].leaderboard[0].score,100);
});

// Minimal page-boundary DOM. Test actual event handlers against the real HTML
// without browser or network dependencies. Setting innerHTML is forbidden.
class Element {
  constructor(tag="") { this.tagName=tag.toUpperCase();this.children=[];this.listeners={};this.value="";this.href="";this.hidden=false;this.disabled=false;this.open=false;this.checked=false;this.parentElement=null;this.attributes={};this.text="";this.classes=new Set();this.classList={toggle:(name,on)=>on?this.classes.add(name):this.classes.delete(name)}; }
  set textContent(value) { this.text=String(value);this.children=[]; }
  get textContent() { return this.text+this.children.map(child=>child.textContent).join(""); }
  set innerHTML(_) { throw new Error("Dynamic markup is not permitted"); }
  setAttribute(name,value) { this.attributes[name]=String(value);if(name==="href")this.href=String(value); }
  removeAttribute(name) { delete this.attributes[name];if(name==="href")this.href=""; }
  append(...children) { children.forEach(child=>{child.parentElement=this;this.children.push(child);}); }
  replaceChildren(...children) { this.text="";this.children=[];this.append(...children); }
  addEventListener(name,listener) { (this.listeners[name] ||= []).push(listener); }
  async fire(name) { for(const listener of this.listeners[name]||[])await listener({preventDefault(){}}); }
  focus() { this.focused=true; }
  select() { this.selected=true; }
  closest(tag) { return this.tagName===tag.toUpperCase()?this:this.parentElement?.closest(tag)||null; }
  scrollIntoView() { this.scrolled=true; }
}
function pageDocument() {
  const html=fs.readFileSync(path.join(__dirname,"../tools/index.html"),"utf8");
  const elements=new Map(),stack=[];
  const voidTags=new Set(["META","LINK","INPUT","BR","IMG","HR"]);
  for(const match of html.matchAll(/<\/?([a-z][a-z0-9-]*)\b[^>]*>/gi)) {
    const tag=match[1].toUpperCase();
    if(match[0].startsWith("</")){assert.equal(stack.pop()?.tagName,tag,"valid HTML nesting");continue;}
    const el=new Element(tag);el.parentElement=stack.at(-1)||null;
    el.hidden=/\bhidden(?:\s|>)/.test(match[0]);el.disabled=/\bdisabled(?:\s|>)/.test(match[0]);el.checked=/\bchecked(?:\s|>)/.test(match[0]);
    el.value=/\bvalue="([^"]*)"/.exec(match[0])?.[1]||"";el.href=/\bhref="([^"]*)"/.exec(match[0])?.[1]||"";
    const id=/\bid="([^"]+)"/.exec(match[0])?.[1];
    if(id){assert(!elements.has(id),"unique HTML id: "+id);elements.set(id,el);}
    if(!voidTags.has(tag))stack.push(el);
  }
  assert.equal(stack.length,0);
  return {getElementById:id=>elements.get(id),createElement:tag=>new Element(tag)};
}
async function mountedPage(body=index(), {protocol="https:",hash="",clipboard=null,fetcher=null}={}) {
  const doc=pageDocument(),calls=[],listeners={};
  doc.defaultView={location:{protocol,hash},navigator:{clipboard},addEventListener(name,listener){(listeners[name] ||= []).push(listener);},fetch:async(url,options)=>{calls.push({url,options});return fetcher?fetcher(url,options):{ok:body!==undefined,json:async()=>body};}};
  tools.mount(doc);
  await new Promise(resolve=>setImmediate(resolve));
  return {doc,calls,async navigate(hash){doc.defaultView.location.hash=hash;for(const listener of listeners.hashchange||[])listener();}};
}
function enterDaily(page, {issue="12",date="2026-10-26",work=true,exercise=false}={}) {
  const get=page.doc.getElementById;
  get("log-issue").value=issue;get("log-date").value=date;get("log-work").checked=work;get("log-exercise").checked=exercise;
}

test("page prepares an exact daily comment locally and points at the chosen issue comment field", async()=>{
  const page=await mountedPage(index([week()])),get=page.doc.getElementById;
  enterDaily(page,{issue:"https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/42#issuecomment-123",exercise:true});
  await get("log-form").fire("submit");
  assert.equal(get("log-output").value,"/checkin 2026-10-26 W=1 E=1");
  assert.equal(get("log-link").href,"https://github.com/Al-LeanMuscle-Club/AI-LeanMuscle-Club/issues/42#new_comment_field");
  assert.equal(get("log-result").hidden,false);
  assert.deepEqual(page.calls,[{url:"../reports/daily/index.json",options:undefined}],"drafting never submits or fetches member records");
  get("log-work").checked=false;await get("log-work").fire("change");
  assert.equal(get("log-result").hidden,true,"changed input cannot leave a stale draft ready to copy");
});

test("invalid dates and wrong-repository issue URLs hide a previous valid draft", async()=>{
  const page=await mountedPage(),get=page.doc.getElementById;
  enterDaily(page);await get("log-form").fire("submit");
  get("log-date").value="2026-02-30";await get("log-form").fire("submit");
  assert.equal(get("log-result").hidden,true);assert.match(get("log-message").textContent,/有效的日历日期/);
  enterDaily(page,{issue:"https://github.com/wrong/club/issues/12"});await get("log-form").fire("submit");
  assert.equal(get("log-result").hidden,true);assert.match(get("log-message").textContent,/当前仓库/);
  const today=tools.localDate();get("log-date").value="2026-10-01";await get("log-today").fire("click");assert.equal(get("log-date").value,today);
});

test("copying is explicit, and denied clipboard access selects text for manual copying", async()=>{
  const copied=[];
  const page=await mountedPage(index(),{clipboard:{writeText:async value=>copied.push(value)}}),get=page.doc.getElementById;
  await get("copy-log").fire("click");assert.deepEqual(copied,[]);
  enterDaily(page,{work:false,exercise:false});await get("log-form").fire("submit");await get("copy-log").fire("click");
  assert.deepEqual(copied,["/checkin 2026-10-26 W=0 E=0"]);assert.match(get("log-message").textContent,/已复制/);
  page.doc.defaultView.navigator.clipboard={writeText:async()=>{throw new Error("denied");}};
  await get("copy-log").fire("click");assert.equal(get("log-output").selected,true);assert.match(get("log-message").textContent,/手动复制/);
  assert.equal(page.calls.length,1);
});

test("repository settings update all participation links and safely invalidate drafts and searches", async()=>{
  const page=await mountedPage(),get=page.doc.getElementById;
  get("find-handle").value="@Alice";await get("find-form").fire("submit");assert.equal(get("find-link").hidden,false);
  enterDaily(page);await get("log-form").fire("submit");
  get("repository").value="new-org/new-club";await get("repository").fire("input");
  for(const id of ["create-journal","share-experience","join-community","browse-experiences"])assert.equal(new URL(get(id).href).pathname.startsWith("/new-org/new-club/"),true);
  assert.equal(new URL(get("create-journal").href).searchParams.get("template"),"daily-checkin.yml");
  assert.equal(get("log-result").hidden,true);assert.equal(get("find-link").hidden,true);
  await get("find-form").fire("submit");assert.equal(new URL(get("find-link").href).pathname,"/new-org/new-club/issues");
  get("repository").value="../secret";await get("repository").fire("change");
  assert.equal(get("create-journal").href,"");assert.equal(get("create-journal").attributes["aria-disabled"],"true");
  get("repository").value="example/club";await get("repository").fire("change");
  assert.equal(get("create-journal").attributes["aria-disabled"],undefined);
  get("find-handle").value="Alice author:Bob";await get("find-form").fire("submit");assert.equal(get("find-link").hidden,true);
});

test("the weekly board renders raw day counts, declared tie ranks and source links", async()=>{
  const page=await mountedPage(index([week("2026-10-19",[]),week("2026-10-26",[row("Zulu",{rank:2}),row("Alice",{work_days:7,exercise_days:7,checkin_days:7,score:100})])])),get=page.doc.getElementById;
  assert.equal(get("filter-week").value,"2026-10-26");assert.equal(get("ranking-table").hidden,false);
  assert.equal(get("ranking-body").children.length,2);
  const first=get("ranking-body").children[0];assert.equal(first.children[0].textContent,"#1");assert.equal(first.children[1].textContent,"@Alice");assert.equal(first.children[2].textContent,"7");assert.equal(first.children[4].textContent,"100.00");
  assert.equal(first.children[5].children[0].href,"https://github.com/example/club/issues/12");
  assert.match(get("report-snapshot").textContent,/2026-10-26 至 2026-11-01/);
  get("filter-week").value="2026-10-19";await get("filter-week").fire("change");
  assert.equal(get("ranking-table").hidden,true);assert.match(get("report-message").textContent,/本周还没有公开打卡记录/);
});

test("no-report, missing-report and incompatible-report states stay distinct and drafts still work", async()=>{
  const empty=await mountedPage(index());assert.match(empty.doc.getElementById("report-message").textContent,/首次定时统计/);
  const missing=await mountedPage(index(),{fetcher:async()=>({ok:false})});assert.match(missing.doc.getElementById("report-message").textContent,/尚未生成或暂时无法读取/);assert.equal(missing.doc.getElementById("retry-reports").hidden,false);
  const old=await mountedPage({schema_version:2,weeks:[]});assert.match(old.doc.getElementById("report-message").textContent,/格式不兼容/);assert.equal(old.doc.getElementById("ranking-table").hidden,true);
  enterDaily(old);await old.doc.getElementById("log-form").fire("submit");assert.equal(old.doc.getElementById("log-result").hidden,false);
});

test("a failed report fetch can be retried without reloading or making write requests", async()=>{
  let attempt=0;
  const page=await mountedPage(index(),{fetcher:async()=>{if(!attempt++)throw new Error("offline");return {ok:true,json:async()=>index([week()])};}}),get=page.doc.getElementById;
  assert.equal(get("retry-reports").hidden,false);
  await get("retry-reports").fire("click");assert.equal(get("ranking-table").hidden,false);assert.equal(get("retry-reports").hidden,true);
  assert.deepEqual(page.calls,[{url:"../reports/daily/index.json",options:undefined},{url:"../reports/daily/index.json",options:undefined}]);
});

test("local file mode gives useful guidance and never tries to read reports", async()=>{
  const page=await mountedPage(index(),{protocol:"file:"}),get=page.doc.getElementById;
  assert.deepEqual(page.calls,[]);assert.match(get("report-message").textContent,/本地网页服务器/);
  enterDaily(page);await get("log-form").fire("submit");assert.equal(get("log-result").hidden,false);
});

test("the existing history bookmark opens the journal finder; malformed fragments are harmless", async()=>{
  const page=await mountedPage(index(),{hash:"#history-heading"}),get=page.doc.getElementById;
  assert.equal(get("history-heading").closest("details").open,true);assert.equal(get("history-heading").scrolled,true);
  await page.navigate("#%E0%A4%A");await page.navigate("#missing");
});

test("the page exposes only daily check-in, scoring and conversation features",()=>{
  const doc=pageDocument();
  for(const id of ["log-heading","ranking-heading","experiences-heading","log-work","log-exercise","create-journal"])assert(doc.getElementById(id));
  for(const id of ["carry-form","activity-form","log-session","log-notes","advanced-tools","filter-sport"])assert.equal(doc.getElementById(id),undefined);
  const html=fs.readFileSync(path.join(__dirname,"../tools/index.html"),"utf8");
  for(const number of [35,44,42,41])assert(html.includes('/issues/'+number+'"'));
  assert(!html.includes("weekly-plan.yml"));assert(!html.includes("meal-record.yml"));assert(!html.includes("points-approved"));
  assert(!html.includes("href=\"../docs/"),"deployed links point to documents on GitHub");
});
