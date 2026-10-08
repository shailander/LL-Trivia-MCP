# Live trivia (advanced)

When `instance.setting.schedule.is_live_trivia === true`, every player sees the same question at
the same time. Skip this page for a normal self-paced quiz.

## Rules

- Start time is `T0 = Date.parse(setting.schedule.publish_time)`.
- **Before T0:** show the welcome screen with a countdown to T0. At 0, switch to GAME automatically.
- **After T0:** `elapsed = ceil((now - T0) / 1000)` seconds. Each question takes up
  `time_interval + result_duration` seconds (`result_duration` defaults to 4). Walk the questions
  to find where the clock is:

```ts
let t = elapsed
for (let i = 0; i < qs.length; i++) {
  const q = qs[i], slot = q.timeInterval + q.resultDuration
  if (t > slot) { q.timeLeft = 0; q.resultDuration = 0; t -= slot; continue }   // already over
  const timeOver = t > q.timeInterval
  q.timeLeft = timeOver ? 0 : q.timeInterval - t
  q.resultDuration = timeOver ? q.resultDuration - (t - q.timeInterval) : q.resultDuration
  currentIndex = (q.timeLeft === 0 && q.resultDuration === 0) ? i + 1 : i
  t = -1; break
}
if (t > 0 || currentIndex >= qs.length) step = 'RESULT'   // whole quiz already over
else step = 'GAME'
```

- Start the question timer from `timeLeft`, not from `timeInterval`.
- When the timer hits 0, auto-submit whatever is selected (an incomplete selection submits `NO_ATTEMPT`). Show the result for `resultDuration` seconds, then advance.
- When the tab becomes visible again, rerun the calculation above so the player re-syncs, unless they're on RESULT or in review.
- A player who joins after the end lands on RESULT having answered nothing. Do **not** send game-completed in that case (see `apis/game-completed`).
