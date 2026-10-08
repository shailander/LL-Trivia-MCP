# API: Instance list

**Purpose:** List every trivia instance of a game, to pick the current one when no `instanceId` is given.
**When:** Once at startup, only if `instanceId` is missing. See `instance-resolution`.

| | |
|---|---|
| Method | `GET` |
| URL | `{ARCADE}/v2/minigames/instances/{gameId}/list/?application_id={clientId}&all=yes` |
| Auth | `Authorization: <authToken>` (raw token, **no** `Bearer`) |

## Params
| Name | In | Notes |
|---|---|---|
| `gameId` | path | Trivia game ID |
| `application_id` | query | `clientId` |
| `all` | query | `yes` returns all instances, not only active ones |

## Sample response (trimmed, `whitelabel` omitted)
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "instance_id": "inst_week_1",
      "display_name": "Week 1 Trivia",
      "active": "ACTIVE",
      "program_id": "8f1c...",
      "external_id": "8f1c...",
      "setting": {
        "schedule": { "publish_time": "2026-10-01T18:00:00Z", "draft": false, "is_live_trivia": false, "show_until": "" },
        "welcome": { "...": "see apis/instance-details" },
        "results": { "...": "see apis/instance-details" }
      }
    }
  ]
}
```

## Fields used
`results[].instance_id`, `active` (`ACTIVE` / `INACTIVE`), `setting.schedule.publish_time`, `setting.schedule.is_live_trivia`, `setting.schedule.show_until`.

## Errors
Non-2xx: show the error screen. An empty `results`: show the "No game" screen.

Live tool: `list_instances(client_id, game_id, access_token, env)`.
