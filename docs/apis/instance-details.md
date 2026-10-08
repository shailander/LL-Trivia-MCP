# API: Instance details

**Purpose:** Get one trivia instance: its program (where the questions live) and the CMS settings for every screen.
**When:** Once at startup, after `instanceId` is known.

| | |
|---|---|
| Method | `GET` |
| URL | `{ARCADE}/v2/minigames/{gameId}/{instanceId}/?application_id={clientId}` |
| Auth | none |

## Sample response (trimmed, `whitelabel` omitted: theming is the client's job)
```json
{
  "instance_id": "inst_week_1",
  "display_name": "Week 1 Trivia",
  "active": "ACTIVE",
  "program_id": "8f1c2b9e-...",
  "external_id": "8f1c2b9e-...",
  "cdn": "https://.../",
  "screens": { "welcome": true, "qna": true, "result": true, "schedule": true },
  "setting": {
    "welcome": {
      "skip": false,
      "start_btn_label": "Start",
      "how_to_play": {
        "enabled": true,
        "title": "How to play",
        "body": "<p>Answer 5 questions.</p><p>Points for every correct answer.</p>"
      }
    },
    "results": {
      "title_type": "SCORE_MSG",
      "title_txt": "Thanks for playing!",
      "gte_90": "Amazing! You're a trivia champion!",
      "gte_50": "Great effort! You're almost there!",
      "lt_50": "Don't give up! Better luck next round!",
      "show_points": true,
      "review_questions": true,
      "animation": true,
      "share": { "enabled": true, "msg": "I scored {{score}}/{{totalQuestions}}!", "deep_link": "https://example.com/trivia" }
    },
    "schedule": {
      "publish_time": "2026-10-01T18:00:00Z",
      "draft": false,
      "is_live_trivia": false,
      "show_until": ""
    }
  }
}
```

## Fields used
| Field | Use |
|---|---|
| `program_id` (fallback `external_id`) | `programId` for `apis/program-widgets` |
| `display_name` | Optional game title |
| `setting.welcome.*` | `screens/welcome` |
| `setting.results.*` | `screens/result` |
| `setting.schedule.is_live_trivia`, `publish_time` | `live-trivia` |

`how_to_play.body` is **HTML**. Sanitize it (e.g. DOMPurify) before rendering.

## Errors
Non-2xx or no `program_id`/`external_id`: show the error screen.

Live tool: `get_instance_details(client_id, game_id, instance_id, env)`.
