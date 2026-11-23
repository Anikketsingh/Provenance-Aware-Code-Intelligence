# Introduction

## Background

Source code records what a program does, but almost never why. The reasons sit elsewhere: the incident that motivated a retry, the bug report that justified a null check, the review discussion that settled a timeout. They are written in commit messages, issue trackers and pull-request threads. None of these systems points to the others in a way a tool can query, and the knowledge fades as the people who wrote it move on.

The standard way to ask a repository about a line is `git blame`. It names the last commit that touched the line. In a mature project that commit is often a reformat, a rename or a move: a change to how the code looks, not to what it does. In Django, the clearest example is the type check in `make_password()` (`django/contrib/auth/hashers.py`). Under git's strongest settings (`git blame -w -M -C -C`), its blame answer is a 2022 commit, "Refs #33476 -- Reformatted code with Black." The behaviour actually comes from a 2020 commit, "Fixed #31375 -- Made make_password() accept only bytes or strings", whose ticket explains the risk the check removes.

This gap has become urgent. AI coding agents now write a large share of the changes merged into many repositories. They work from the current state of the code: they can read a check, but not the reason for it. To an agent that sees "Reformatted code with Black", deleting the check looks like harmless clean-up. An agent that sees "accept only bytes or strings, see ticket #31375" can tell that the line is a guard, and keep it or ask first. The quality of that one answer decides whether AI-assisted coding quietly removes the protections a project has accumulated.

## Problem statement

Given a repository with its full version history and the discussions linked to it, can the change that really gave a line its behaviour be recovered automatically? And can the reason behind that change be recovered, and given to developers and AI agents accurately enough to prevent unsafe edits?

Breaking this down, the system must:

1. trace a line to the commit that introduced or last changed its behaviour, across reformatting, renames and moves, rather than to its latest cosmetic edit;
2. attach the discussion behind that commit: a ticket, issue or pull request. Where no link was recorded, it must find candidates by search and label them as such;
3. explain the line from that evidence with citations, and abstain when the evidence does not say why;
4. warn when a proposed change removes or weakens protective code whose history says it matters;
5. serve all of this to any AI agent, whatever its client or model, through a standard interface.

## Objectives

The project was planned in two parts. The first part, the tracer, was frozen and evaluated before any product work began. The objectives of the whole project are:

- **O1. Accurate tracing.** Beat git's strongest settings on a held-out set of real lines, measured with confidence intervals and a paired significance test.
- **O2. Evidence everywhere.** Link commits to tickets, issues and pull requests in Django, Redis and React. When the link is missing, find the discussion by search, and measure how well that works.
- **O3. Trustworthy explanations.** Every claim must cite its evidence. When the evidence does not explain the line, the system abstains. Both properties are measured.
- **O4. Protect code in CI.** A deterministic check that flags removed or weakened guards with a recorded reason, shipped as a GitHub Action, and measured on held-out history against simple baselines.
- **O5. Works with any model.** A Model Context Protocol (MCP) server that any client and any tool-calling model can use, including local models. Shipped as an installable package.
- **O6. Measured difference.** Measure what the system changes: for agents' behaviour (a controlled pilot) and for cost on a laptop.

## Contributions

1. **A three-layer tracer.** It classifies every file change in history as cosmetic, rename, move or logic, using tree-sitter token streams. It lets `git blame` skip each file's cosmetic commits, and steps through mixed commits line by line. On a held-out set it finds the right commit {{rq1.ours}} of the time, against {{rq1.b2}} for git's strongest settings.
2. **An evidence graph** of {{corpus.commits}} commits, {{corpus.discussions}} tickets, issues and pull requests across Django, Redis and React. It is built from explicit references and merged pull requests, with a time-respecting search for missing links.
3. **Cited explanations with abstention.** On {{rq3.questions_total}} questions, the explainer abstained on {{rq3.unanswerable_abstained}} of {{rq3.unanswerable}} questions whose evidence was withheld. {{rq3.claims_supported_pct}} of the claims in its answers are supported by the evidence they cite.
4. **`whyblame check` and its GitHub Action.** It finds removed and weakened guards in Python, C and JavaScript, and scores each guard's history deterministically. It has been tested live on a real pull request.
5. **`whyblame`, a public MCP server and command-line tool.** It works over stdio or HTTP, gives versioned and size-capped replies, and writes agent rules with `whyblame init`.
6. **A reproducible evaluation** of six research questions. One script (`eval/reproduce.py`) rebuilds every number in this report from saved results.

## Organisation of the report

Chapter 2 reviews related work. Chapter 3 presents the system's design and Chapter 4 its implementation. Chapter 5 sets out the evaluation method for the six research questions, and Chapter 6 reports and analyses the results. Chapter 7 discusses limitations and threats to validity. Chapter 8 concludes and lists future work.
