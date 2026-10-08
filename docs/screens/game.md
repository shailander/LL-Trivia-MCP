# Screen: Game (questions)

Shows one question at a time from `questions[currentIndex]` (see `data-merge` for the state shape).

## Layout

- Header: "Question {n} of {total}", and the timer if `timeInterval > 0`.
- The question text.
- Options from `displayChoices` (single or multi select). For multi select, show "Pick {totalCorrectChoices} options".
- Feedback banner and points label (conditional, see below).
- Footer: submit/next button when `nextBtn.enabled` is true, or in review mode.

## On show

- Not in review mode: `POST impressionUrl` (`apis/widget-impression`).
- Question already answered (`isAlreadyAnswered`) or review mode: preselect `selected`, lock the input, and show the result state.
- Otherwise: clear the selection and start the timer from `timeInterval` (live trivia starts from `timeLeft`).

## Selecting options

- `SINGLE_SELECT`: the selection is `[option]`.
- `MULTI_SELECT`: append in click order. Ignore re-clicks. When the selection is full (`totalCorrectChoices`), drop the oldest selection.
- Ignore clicks once the question is answered, the timer has ended, or a submit is in flight.
- **No timer and no button** (`timeInterval === 0 && !nextBtn.enabled`): submit as soon as the selection is complete.

## Submitting (`apis/submit-interaction`)

Triggered by:
1. the submit button (enabled only when `selected.length === totalCorrectChoices`),
2. the timer reaching 0 (auto-submit whatever is selected; an incomplete selection submits `NO_ATTEMPT`), or
3. the no-timer/no-button auto-submit above.

After submitting, set `isAnswered`, `isCorrect` and `selected`. The first-ever answer also triggers `apis/trivia-credit`.

## Feedback and points after the answer (`feedbackEnabled`)

Show these once the question has ended (submitted, or the timer ran out) and it has been answered:
- **Banner:** "Correct answer!" or "Incorrect answer!", based on `isCorrect`.
- **Options:** mark the correct options green and the user's wrong picks red. Use `displayChoices[].isCorrect`.
- **Points label:** `+{isCorrect ? points : incorrectPoints}`, only if `points > 0 || incorrectPoints > 0`.

When `feedbackEnabled` is false, show none of these during play. The user only sees results at the end.

In **review mode**, always show the banner and option marks. Show the points label only if `setting.results.show_points` is true.

## Advancing

| Config | Behaviour |
|---|---|
| `showNextQuestion` true | Wait `resultDuration` seconds after submit, then go to the next question automatically |
| Timer ended and `showNextQuestion` false | Wait `resultDuration` seconds, then go next |
| No timer and `showNextQuestion` false | Button label changes to "Next". Tapping it goes next. |
| Timer still running after submit | Button shows `nextBtn.submittedLabel` (disabled) until the timer ends |

**Next** means the next question after `currentIndex` that is not answered. If there is none, go to RESULT
(this may send `apis/game-completed`).

## Button label

| State | Label |
|---|---|
| Review mode | "Back" (returns to RESULT) |
| Already answered, or answered with no timer | "Next" |
| Answered, timer still running | `nextBtn.submittedLabel` |
| Not answered | `nextBtn.label` (show a spinner while submitting) |

## Timer

- `timerType: 'COUNTDOWN'`: show the seconds remaining.
- `timerType: 'PROGRESS_BAR'`: show a bar that shrinks over `timeInterval`.
- Hide or stop the timer once the question is answered, or in review mode.
- Clear every interval and timeout when the screen unmounts.
