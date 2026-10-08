# Screen: Result

This screen is computed from `questions[]` state. It needs no extra API call.

## CMS fields (`instance.setting.results`)

| Field | Behaviour |
|---|---|
| `title_type` | `STATIC_MSG` shows `title_txt`. `SCORE_MSG` picks a title by score. |
| `title_txt` | Static title |
| `gte_90` / `gte_50` / `lt_50` | Score titles |
| `show_points` | Show the total points line (and points in review mode) |
| `review_questions` | Tapping a question number opens it in review mode |
| `share.enabled` / `share.msg` / `share.deep_link` | Share button, message template and link |
| `animation` | Optional celebration (e.g. confetti when ≥60% correct). Purely cosmetic. |

## Scoring

```ts
const total = questions.length
const correct = questions.filter(q => q.isCorrect).length
const pct = Math.ceil((correct / total) * 100)

const title = r.title_type === 'STATIC_MSG' ? r.title_txt
  : pct >= 90 ? r.gte_90
  : pct >= 50 ? r.gte_50
  : r.lt_50

const totalPoints = questions.reduce((sum, q) => sum + (q.isCorrect ? q.points : q.incorrectPoints), 0)
```

## Layout

1. **Title** (above).
2. **Score:** "You got {correct} out of {total} correct". Always shown.
3. **Question strip:** one numbered chip per question, green when correct and red when wrong.
   If `review_questions` is on, tapping chip *i* sets `currentIndex = i`, `step = 'GAME'` with `isReview = true`.
   Review is read-only. The "Back" button returns here.
4. **Footer** (only if `show_points` or `share.enabled`):
   - Points: `{totalPoints}` when `show_points` is on.
   - **Share** button when `share.enabled` is on.
5. **Next trivia** label, when a later instance exists (see `instance-resolution`).

## Share

```ts
const text = r.share.msg.replace(/\{\{(score|totalQuestions)\}\}/g, (_, k) => String(k === 'score' ? correct : total))
if (navigator.share) navigator.share({ text, url: r.share.deep_link })
else navigator.clipboard.writeText(`${text}\nPlay the game and prove your skills: ${r.share.deep_link}`)
```
On mobile, use the platform share sheet.

## Entering RESULT

- From GAME with every question answered: send `apis/game-completed` once.
- On load, when everything was already answered: go straight here and do **not** send game-completed.
- Once the user reaches RESULT, every later visit to GAME is review mode.
