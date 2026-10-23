"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
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
