# Chapter 2: The Reallocation Principle

## Exercise 1

The recurring workflow I am using is a monthly budget versus actual variance analysis for one department.

The steps, each labeled:
1. Pull the actuals export from the accounting system and the budget file. Preparation.
2. Check that the pull landed cleanly and that the totals tie to the ledger. Preparation and evidence.
3. Normalize both files to the same account structure and the same period. Transformation.
4. Compute the variance for each line, in dollars and in percent. Transformation.
5. Flag every line above a set threshold. Preparation.
6. Decide whether each flagged variance is material. Judgment.
7. Explain what drove each material variance. Judgment.
8. Sign off that the note is ready for the department head. Approval.
9. Send the note to the department head. Release.

The boundary falls between step 5 and step 6. Everything up to the flag is mechanical and checkable, so a model can do it and I can confirm it against the source. A model would probably label steps 1 through 5 correctly. Where I would disagree is if it treated step 7, explaining the driver, as something it can finish from the numbers alone. Naming the cause needs business context the model does not have, so that step is judgment even though it produces text that looks like preparation. I would also push back if the model implied step 6, materiality, is just the threshold from step 5. The threshold flags candidates; deciding what actually matters is a separate judgment.

## Exercise 2

The scenario is the one from the opening of the chapter, a 2.3 million dollar variance that was defended in a meeting but never fully traced to a source.

Prompt with uncertainty markers:
"Here is a variance table and the two source exports it came from. Draft a short summary of the largest variances. For every cause you state, mark it confirmed from source only if the export shows it, otherwise mark it cannot determine from data, needs human. Do not state a driver you cannot tie to a row. List separately every number whose source row you could not find."

Prompt without uncertainty markers:
"Here is a variance table. Write a short summary explaining the largest variances."

The first prompt produces output that points at its own gaps. It separates what the data shows from what it is guessing, so I walk away with a list of exactly what to check before the note moves. The second prompt produces a clean, confident paragraph that reads as finished and hides those same gaps, which is the trap from Chapter 1. The comparison shows that asking for uncertainty markers turns hidden risk into visible review items, at the cost of a less tidy first draft.

## Exercise 3

The step I am putting a gate on is step 7 above, explaining each material variance.

Named approver: the department finance manager, a specific named person, not whoever happens to look.

What the recipe hands them: the variance table with each material line, the source row reference for every number, a draft driver for each line marked as inferred, and the assessment artifact showing the status of each claim.

Stop conditions: the recipe drafts and then stops. It does not send the note. It halts and refuses to hand off if any material line is missing a source reference, or if the control total does not tie to the ledger.

What makes the finding defensible if someone asks the next day: every number ties to a row in the named export, the control total reconciles, and every stated driver has been confirmed by the owner of that line rather than guessed by the model.

Gaps a careful review would still find in this gate: a scope gap, because I have not said which entities and which periods the recipe may touch, so it could drift into adjacent data. And a verification gap, because I named an approver but did not name the line owners who must confirm each driver, and I did not justify why the materiality threshold is set where it is. Closing those two gaps is the difference between a gate that exists on paper and one that actually holds.
