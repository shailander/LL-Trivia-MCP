# API: Game completed

**Purpose:** Tell the arcade backend that the user finished this instance.
**When:** When moving **from GAME to RESULT**, and only if **every** question is answered
(`isAnswered || isAlreadyAnswered`). Send it at most once per session.

Do **not** send it when:
- the user lands on RESULT straight from load because everything was answered in an earlier session, or
- a live trivia ended before the user answered everything.

The backend dedupes per user per instance, so a repeat is harmless, but don't rely on that.

| | |
|---|---|
| Method | `POST` |
| URL | `{ARCADE}/v1/minigames/game-completed/` |
| Auth | `Authorization: <authToken>` (raw token, **no** `Bearer`) |
| Body | `{ "game_id": "<gameId>", "instance_id": "<instanceId>" }` |

```ts
function goToResult(state) {
  if (state.step === 'GAME' && !state.isReview && !state.gameCompletedSent
      && state.questions.every(q => q.isAnswered || q.isAlreadyAnswered)) {
    state.gameCompletedSent = true
    fetch(`${ARCADE}/v1/minigames/game-completed/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: authToken },
      body: JSON.stringify({ game_id: gameId, instance_id: instanceId }),
    })
  }
  state.isReview = true
  state.step = 'RESULT'
}
```

## Errors
Fire and forget. Log failures.
