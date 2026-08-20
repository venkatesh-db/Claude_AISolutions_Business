# Practice Exercise — Same Discipline, Any Simple Python Project
## For participants learning this for the first time

You don't need RxFlow or any big system for this. Use any small Python
project you already have — even a personal script, a small Flask app,
a scraper, anything with a few files. The point is practicing the
*thinking*, not the size of the project.

---

## Step 1 — Pick your project

Open a terminal in any small Python folder you have. If you don't have
one, ask Claude to create a tiny 3-4 file example first:

```
Create a small Python project for me to practice on — a simple
to-do list app with a few files: adding tasks, marking them done,
saving to a file. Nothing fancy, just enough files to be realistic.
```

---

## Step 2 — Run the practice prompt

```
I want to practice deciding what kind of help I actually need for
this project, instead of just asking you to "build an agent" for
everything.

Here's how I want to work:

1. I'll tell you something I find annoying or repetitive about
   working on this project.

2. You test it against these four options, IN THIS ORDER, and stop
   at the first one that honestly fits:

   a) A FACT — something true about this project that doesn't
      change. If true, just tell me the one sentence I should write
      down somewhere so I never have to explain it to you again.

   b) A SHORTCUT — something I do the same way, often. If true,
      write me a simple template I can reuse.

   c) A CHECKLIST WITH JUDGEMENT — something with multiple steps
      where I have to actually think at each step, not just fill in
      blanks. If true, write out the steps and tell me where the
      thinking happens.

   d) SOMETHING BIGGER — needs its own tool, needs to run without me,
      or needs to reach outside this project entirely. If it's this,
      just tell me that plainly and explain why — don't build it.

3. For each thing I tell you, show me your reasoning for why it's
   NOT each earlier option before you land on the right one. I want
   to see the "no, because..." not just the final answer.

My first annoying thing is: <describe something real — e.g. "I keep
forgetting to check if a task ID actually exists before I try to mark
it done">
```

---

## What a participant should expect to see

**Most answers will land on (a) or (b).** That's not a disappointing
result — it's the correct one. Most of what feels annoying in a small
project is actually a fact you forgot to write down, or a thing you
keep retyping.

**Example run, worked through:**

> "I keep forgetting to check if a task ID exists before marking it
> done."
>
> Is this a FACT? No — it's not a truth about the project, it's a
> thing that needs to happen every time.
>
> Is this a SHORTCUT? Not quite — the action itself (checking, then
> deciding what to do if it's missing) has a small decision in it,
> even if it's simple.
>
> Is this a CHECKLIST WITH JUDGEMENT? Yes, barely — "check if the ID
> exists, if not say so clearly, if yes proceed." That's real, if
> small, judgement.
>
> **Landed on: checklist.** Here it is: [steps written out]

**A second example that should land differently:**

> "I always have to explain what this project even does before
> asking for help."
>
> Is this a FACT? Yes — what the project does doesn't change every
> time you ask something. **Landed on: fact.** Write this sentence
> down: "This is a to-do list app: tasks have an ID, a description,
> and a done/not-done status, saved to tasks.json."

---

## Step 3 — Try to trick yourself into over-building

This is the important second half of the exercise. Ask for something
that FEELS like it needs a big answer, and watch it get correctly
rejected:

```
I think I need an agent that runs by itself every morning and checks
my to-do list for overdue tasks.

Test this the same way as before. Be honest — does this actually need
to run with nobody watching, or could I just ask for this myself
whenever I open the project?
```

**Expected honest answer:** for a small personal project, this almost
always resolves to "you could just ask me this each morning — it
doesn't need to run unattended." Seeing a plausible-sounding "I need
an agent" request get correctly turned down is the most valuable
five minutes of this whole exercise.

---

## The one habit to walk away with

Every time something feels annoying, ask the four questions in order,
out loud, before building anything:

1. Is this just a fact I forgot to write down?
2. Is this just a thing I keep retyping?
3. Does this genuinely need me to think at more than one step?
4. Does this actually need to run without me — or am I just excited
   about the idea of automation?

Most of the time, the honest answer is 1 or 2. That's not a smaller
result — that's the discipline working correctly.

---

*Coderrange · corporate training and engineering capability*
