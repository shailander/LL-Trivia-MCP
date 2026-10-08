# API: Program widgets (questions)

**Purpose:** Get the trivia questions. Each question is a LiveLike `text-quiz` widget.
**When:** Once at startup, after instance details. Run it in parallel with `apis/widget-interactions`.

| | |
|---|---|
| Method | `GET` |
| URL | `{LIVELIKE}programs/{programId}/widgets/?page_size=100` |
| Auth | none |

## Sample response (trimmed)
```json
{
  "count": 2,
  "next": null,
  "results": [
    {
      "id": "w-111",
      "kind": "text-quiz",
      "question": "Which city hosts the Colosseum?",
      "impression_url": "https://cf-blast.livelikecdn.com/api/v1/.../impressions/",
      "choices": [
        { "id": "c-1", "description": "Rome",  "is_correct": true,  "answer_url": "https://.../c-1/answers/" },
        { "id": "c-2", "description": "Paris", "is_correct": false, "answer_url": "https://.../c-2/answers/" },
        { "id": "c-0", "description": "NO_ATTEMPT", "is_correct": false, "answer_url": "https://.../c-0/answers/" }
      ],
      "custom_data": "{\"sort_id\":1,\"question_type\":\"SINGLE_SELECT\",\"choices\":[{\"description\":\"Rome\",\"is_correct\":true},{\"description\":\"Paris\",\"is_correct\":false}],\"time_interval\":15,\"timer_type\":\"COUNTDOWN\",\"feedback_enabled\":true,\"show_next_question\":false,\"next_btn\":{\"enabled\":true,\"label\":\"Submit\",\"submitted_label\":\"Submitted\"},\"result_duration\":4,\"points\":10,\"incorrect_points\":0,\"game_id\":\"...\",\"instance_id\":\"...\"}"
    }
  ]
}
```

`custom_data` is a **JSON string**. Parse it with `JSON.parse`. Parsed shape:

| Field | Type | Meaning |
|---|---|---|
| `sort_id` | number | Display order (ascending) |
| `question_type` | `SINGLE_SELECT` \| `MULTI_SELECT` | |
| `choices[]` | `{description, is_correct}` | Options to **display** |
| `time_interval` | number (s) | Question timer. `0` means no timer. |
| `timer_type` | `COUNTDOWN` \| `PROGRESS_BAR` | How to render the timer |
| `feedback_enabled` | boolean | Show correct/incorrect and points right after submit |
| `show_next_question` | boolean | Auto-advance `result_duration` seconds after submit |
| `next_btn.enabled` / `label` / `submitted_label` | | Submit button visibility and labels |
| `result_duration` | number (s), default 4 | How long to show the answer result before auto-advance |
| `points` / `incorrect_points` | number | Points for a correct / incorrect answer (`incorrect_points` defaults to 0) |

For `MULTI_SELECT`, `widget.choices[]` contains `#`-joined **combinations**. See `data-merge`.

## Errors
Failure here is **fatal**: show the error screen. Zero questions: show the "No game" screen.

Live tool: `get_questions(program_id, env)` returns the questions already parsed and sorted.
