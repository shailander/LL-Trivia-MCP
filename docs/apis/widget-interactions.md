# API: Widget interactions (past answers)

**Purpose:** Get the answers this profile already submitted, so the game can resume or jump to the result screen.
**When:** Once at startup, in parallel with `apis/program-widgets`.

| | |
|---|---|
| Method | `GET` |
| URL | `{LIVELIKE}profiles/{profileId}/widget-interactions/?widget_kind=text-quiz` |
| Auth | `Authorization: Bearer <authToken>` |

## Sample response
```json
{
  "interactions": {
    "text-quiz": [
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
    ]
  }
}
```

## Fields used
Key the list by `widget_id`. `choice_id` refers back to `widget.choices[].id`, and that choice's
`description` (split on `#`) gives the selected options. `is_correct` gives the result. See `data-merge`.

## Errors
**Non-fatal.** On failure, log it and continue as if the user has no past answers.
