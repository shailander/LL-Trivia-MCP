# Merging widgets and interactions into question state

The questions come from `GET programs/{programId}/widgets/` and the user's past answers come from
`GET profiles/{profileId}/widget-interactions/`. Merge them like this.

## 1. Parse and sort

```ts
const questions = widgets
  .map(w => ({ ...w, custom_data: JSON.parse(w.custom_data) }))   // custom_data is a JSON STRING
  .sort((a, b) => a.custom_data.sort_id - b.custom_data.sort_id)
```

## 2. The two choice lists (important)

Each widget carries **two** choice lists:

| List | Contents | Use it for |
|---|---|---|
| `custom_data.choices[]` | `{ description, is_correct }`: the options **to display** | Rendering the options and marking them right or wrong in feedback |
| `widget.choices[]` | `{ id, description, is_correct, answer_url }`: the **submittable answers** | Finding the `answer_url` to POST |

For `SINGLE_SELECT`, the two lists line up: one display option is one submittable answer.

For `MULTI_SELECT`, `widget.choices[]` lists every **combination** of options, joined by `#`
(e.g. `"Paris#Rome"`). There is also a `NO_ATTEMPT` choice for an incomplete answer.

```ts
const EMPTY_CHOICE = 'NO_ATTEMPT'
const totalCorrect = q.custom_data.choices.filter(c => c.is_correct).length

function findSubmitChoice(q, selected: string[]) {
  const answer = selected.length === totalCorrect ? selected.join('#') : EMPTY_CHOICE
  return q.choices.find(c => c.description.trim() === answer)   // -> { answer_url, is_correct, id }
}
```

Keep the user's selection in **click order**, because the reference app joins in click order.
`MULTI_SELECT` requires exactly `totalCorrect` selections. When the user picks one more, drop the
oldest selection.

## 3. Index the interactions

```ts
const byWidgetId: Record<string, Interaction> = {}
for (const i of interactionsRes?.interactions?.['text-quiz'] ?? []) byWidgetId[i.widget_id] = i
```

## 4. Build question state

```ts
interface QuestionState {
  widgetId: string
  impressionUrl: string
  question: string
  questionType: 'SINGLE_SELECT' | 'MULTI_SELECT'
  displayChoices: { description: string; isCorrect: boolean }[]   // custom_data.choices
  submitChoices: { id: string; description: string; isCorrect: boolean; answerUrl: string }[] // widget.choices
  totalCorrectChoices: number
  timeInterval: number        // seconds, 0 = no timer
  timerType: 'COUNTDOWN' | 'PROGRESS_BAR'
  feedbackEnabled: boolean
  showNextQuestion: boolean   // auto-advance after submit
  nextBtn: { enabled: boolean; label: string; submittedLabel: string }
  resultDuration: number      // seconds to show feedback before auto-advance, default 4
  points: number
  incorrectPoints: number     // default 0
  // submission
  selected: string[]
  isCorrect: boolean
  isAnswered: boolean         // answered in this session
  isAlreadyAnswered: boolean  // answered in a previous session (from interactions)
}

const state: QuestionState[] = questions.map(q => {
  const past = byWidgetId[q.id]
  const pastChoice = past && q.choices.find(c => c.id === past.choice_id)
  const selected = pastChoice && pastChoice.description !== 'NO_ATTEMPT' ? pastChoice.description.split('#') : []
  return {
    widgetId: q.id,
    impressionUrl: q.impression_url,
    question: q.question,
    questionType: q.custom_data.question_type,
    displayChoices: q.custom_data.choices.map(c => ({ description: c.description.trim(), isCorrect: c.is_correct })),
    submitChoices: q.choices.map(c => ({ id: c.id, description: c.description.trim(), isCorrect: c.is_correct, answerUrl: c.answer_url })),
    totalCorrectChoices: q.custom_data.choices.filter(c => c.is_correct).length,
    timeInterval: q.custom_data.time_interval,
    timerType: q.custom_data.timer_type,
    feedbackEnabled: q.custom_data.feedback_enabled,
    showNextQuestion: q.custom_data.show_next_question,
    nextBtn: {
      enabled: q.custom_data.next_btn.enabled,
      label: q.custom_data.next_btn.label,
      submittedLabel: q.custom_data.next_btn.submitted_label ?? 'Submitted',
    },
    resultDuration: q.custom_data.result_duration ?? 4,
    points: q.custom_data.points,
    incorrectPoints: q.custom_data.incorrect_points ?? 0,
    selected,
    isCorrect: past?.is_correct ?? false,
    isAnswered: false,
    isAlreadyAnswered: !!past?.choice_id,
  }
})
```

## 5. Resume

```ts
const firstOpen = state.findIndex(q => !q.isAlreadyAnswered)
if (firstOpen === -1) step = 'RESULT'      // everything answered before: jump to result
else currentIndex = firstOpen
```

When moving forward, skip questions that are already answered. If no unanswered question is
left after the current one, go to RESULT.
