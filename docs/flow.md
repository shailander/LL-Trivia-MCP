# End-to-end flow

## Call order

```
1. initLiveLike(clientId, accessToken?)                  -> { profileId, authToken }        [sdk-init]
2. instanceId given?
     no  -> GET instance list, pick instance by time       -> instanceId                     [instance-resolution, apis/instance-list]
            nothing playable -> show "No game" screen, stop
3. GET instance details                                    -> instance                      [apis/instance-details]
   programId = instance.program_id || instance.external_id
4. In parallel (Promise.allSettled):
     a. GET program widgets (questions)                    -> widgets[]   (failure = fatal error screen)  [apis/program-widgets]
     b. GET widget interactions (past answers)             -> interactions (failure = treat as none)      [apis/widget-interactions]
5. Merge widgets + interactions -> questions[] state      [data-merge]
6. Pick the start screen:
     all questions already answered     -> RESULT
     setting.welcome.skip === true       -> GAME (at first unanswered question)
     otherwise                           -> WELCOME
7. GAME, for each question shown:
     POST widget.impression_url                                                              [apis/widget-impression]
     user selects -> submit -> POST choice.answer_url -> { is_correct }                      [apis/submit-interaction]
     first-ever answer of this instance -> POST trivia/credit                               [apis/trivia-credit]
     next -> next unanswered question; none left -> RESULT
8. Entering RESULT from GAME with every question answered -> POST game-completed (once)     [apis/game-completed]
9. RESULT: score, title, points, review, share                                              [screens/result]
```

## Screen state machine

```
          start btn / skip                last question done
WELCOME ───────────────────▶ GAME ─────────────────────────▶ RESULT
                              ▲                                 │
                              └──── tap question N (review) ────┘
                                    (review mode, read-only, "Back" returns to RESULT)
```

Extra screens:
- **Loading**: while steps 1–5 run.
- **Error**: SDK init failed or the questions request failed.
- **No game**: no `instanceId` could be resolved, or the instance has no questions.

## Minimal state

```ts
type Step = 'WELCOME' | 'GAME' | 'RESULT'

interface GameState {
  step: Step
  instance: InstanceDetails      // apis/instance-details
  questions: QuestionState[]     // data-merge
  currentIndex: number
  isReview: boolean              // true once RESULT has been reached; GAME is then read-only review
  gameCompletedSent: boolean
  firstAnswerCreditSent: boolean
}
```

Keep this in whatever state container the app already uses. The result screen is computed from
`questions[]` alone. It needs no extra API call.
