# API: Save analytics (batched events)

**Purpose:** Send a batch of game analytics events to the arcade backend. These power the LiveLike arcade dashboards.
**When:** Whenever the event buffer flushes: every 2 s while events are queued, at 20 buffered events, on unmount, and on page unload. See `analytics` for the event catalogue and the batching rules.

| | |
|---|---|
| Method | `POST` |
| URL | `{ARCADE}/v1/minigames/analytics/` |
| Auth | `Authorization: <authToken>` (raw token, **no** `Bearer`) |
| Body | JSON payload (below) |
| `keepalive` | `true` **only** for the page-unload flush, so the request outlives the page |

## Payload
```json
{
  "application_id": "<clientId>",
  "user_uid": "<profileId>",
  "game_id": "<gameId>",
  "instance_id": "<instanceId>",
  "game_code": "trivia",
  "events": [
    {
      "name": "click_play",
      "data": {
        "event_name": "click_play",
        "event_category": "interaction",
        "created_at": "2026-10-26T10:15:02.120Z",
        "session_id": "4f6c2a1e-...",
        "game_code": "trivia",
        "game_name": "trivia",
        "source_system": "arcade_frontend",
        "ll_app_id": "<clientId>",
        "ll_app_name": "My App",
        "ll_org_id": "<orgId>",
        "ll_org_name": "My Org",
        "ll_instance_id": "<instanceId>",
        "ll_instance_name": "Week 1 Trivia",
        "language": "en",
        "user_properties": {
          "ll_username": "Anonymous",
          "ll_user_id": "<profileId>",
          "user_uid": "<profileId>",
          "profile_id": "",
          "custom_id": "",
          "is_new_user": null,
          "device_type": "Mobile",
          "browser": "Safari",
          "platform": "iOS",
          "country": "United States"
        }
      }
    }
  ]
}
```

`events[].name` and `events[].data.event_name` carry the same value. Every event repeats the full default properties and `user_properties`, because each event must stand alone in the warehouse.

```ts
function saveAnalytics(events: AnalyticsEvent[], keepalive = false) {
  return fetch(`${ARCADE}/v1/minigames/analytics/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: authToken },
    body: JSON.stringify({
      application_id: clientId, user_uid: profileId, game_id: gameId,
      instance_id: instanceId, game_code: 'trivia', events,
    }),
    keepalive,
  }).catch(() => {})   // fire and forget
}
```

## Errors
Fire and forget. Log failures and drop the batch: don't retry, and never block or break the game.
