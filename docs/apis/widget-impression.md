# API: Widget impression

**Purpose:** Tell LiveLike that a question was shown (for analytics and engagement stats).
**When:** Each time a question is displayed in normal play. **Not** in review mode.

| | |
|---|---|
| Method | `POST` |
| URL | `widget.impression_url` (full URL from the widget, use it as-is) |
| Auth | `Authorization: Bearer <authToken>` |
| Body | none (`Content-Type: application/json`) |

```ts
fetch(q.impressionUrl, { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${authToken}` } })
```

## Errors
Fire and forget. Ignore failures.
