# API: Submit answer (widget interaction)

**Purpose:** Submit the user's answer. LiveLike records it and returns whether it is correct.
**When:** On the submit button, or automatically when the timer ends, or right on option click when
there's no timer and no submit button. Submit once per question.

| | |
|---|---|
| Method | `POST` |
| URL | `answer_url` of the chosen **submittable** choice (`widget.choices[]`) |
| Auth | `Authorization: Bearer <authToken>` |
| Body | none (`Content-Type: application/json`) |

## Picking the answer_url
```ts
const answer = selected.length === q.totalCorrectChoices ? selected.join('#') : 'NO_ATTEMPT'
const choice = q.submitChoices.find(c => c.description === answer)
```
Single select: `answer` is just the option text. Multi select: the options joined by `#` in click order. See `data-merge`.

## Sample response
```json
{
  "id": "i-1",
  "widget_id": "w-111",
  "widget_kind": "text-quiz",
  "choice_id": "c-1",
  "is_correct": true,
  "profile_id": "p-1",
  "created_at": "2026-10-01T18:02:11Z",
  "url": "https://..."
}
```

## Using the result
```ts
const isFirstAnswer = questions.every(q => !q.isAnswered && !q.isAlreadyAnswered)
let isCorrect: boolean
if (choice) {
  const res = await post(choice.answerUrl)          // may fail
  isCorrect = res ? res.is_correct : choice.isCorrect
  if (res && isFirstAnswer) creditFirstAnswer()   // apis/trivia-credit
} else {
  isCorrect = false
}
q.selected = selected.length === q.totalCorrectChoices ? selected : []
q.isCorrect = isCorrect
q.isAnswered = true
```
`is_correct` drives the **true/false feedback** on the game screen and the result screen's score.

## Errors
On failure, fall back to the choice's local `is_correct` so the game can continue.
