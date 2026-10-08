# API: Trivia first-answer credit

**Purpose:** Tell the arcade backend that the user started playing this instance (it credits participation).
**When:** After a successful answer submission, **only if no question of this instance had been answered before it** (in this session or any earlier one):

```ts
const isFirstAnswer = questions.every(q => !q.isAnswered && !q.isAlreadyAnswered)   // check BEFORE marking the current one answered
```

| | |
|---|---|
| Method | `POST` |
| URL | `{ARCADE}/v1/minigames/trivia/credit/` |
| Auth | `Authorization: <authToken>` (raw token, **no** `Bearer`) |
| Body | `{ "game_id": "<gameId>", "instance_id": "<instanceId>" }` |

```ts
fetch(`${ARCADE}/v1/minigames/trivia/credit/`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: authToken },
  body: JSON.stringify({ game_id: gameId, instance_id: instanceId }),
})
```

## Errors
Fire and forget. Log failures. They must not block the game.
