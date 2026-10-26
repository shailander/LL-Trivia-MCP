# Analytics

The game sends analytics events to the arcade backend (`apis/analytics`) so that sessions, starts,
completions and shares show up in the LiveLike arcade dashboards. Events are **buffered and sent in
batches every 2 seconds**, not one request per event.

## Setup: once, right after SDK init

1. Create a `session_id` (`crypto.randomUUID()`) for this page load.
2. Build the **default event properties** and **user properties** (tables below).
3. Track `session_start` and record `sessionStartTime = Date.now()`.

Start the buffer **before** any async work, so events fired during boot aren't lost. `ll_instance_id`
and `ll_instance_name` may be empty at first when the instance is still being resolved. Update them once
instance details arrive, so later events carry them.

## Event catalogue

| Event | When it fires | Extra properties |
|---|---|---|
| `session_start` | Game mounted and analytics set up | none |
| `click_play` | User taps **Start** on the welcome screen, **or** the welcome screen is skipped (`setting.welcome.skip`) and play starts automatically | none |
| `game_completed` | The first transition from GAME to RESULT in this session (not when RESULT is shown on load, and not from review mode). It fires even when not every question was answered, e.g. when a live trivia ends. | `number_of_questions` (int), `win_percentage` (`correct / total * 100`, unrounded float), `is_journey_final_step: true` |
| `click_share` | User taps **Share** on the result screen (after the share sheet or clipboard copy is triggered) | none |
| `session_stop` | Page unload or game unmount, **at most once** | `duration` (int seconds since `session_start`) |

`game_completed` (analytics) is **not** the same as the `apis/game-completed` call. The analytics
event fires on any first GAME→RESULT transition. The API call fires only when every question is answered.

The reference app also tracks `language_switched { language }`. Localization is out of scope here, so skip it.

## Default event properties (merged into every event's `data`)

| Key | Value |
|---|---|
| `event_name` | Same as the event name |
| `event_category` | `"interaction"` |
| `created_at` | `new Date().toISOString()` when the event is tracked (not when it's sent) |
| `session_id` | The UUID from setup |
| `game_code` | `"trivia"` |
| `game_name` | `"trivia"` |
| `source_system` | `"arcade_frontend"` |
| `ll_app_id` | `clientId` |
| `ll_app_name` | Application `name` |
| `ll_org_id` | Application `organization_id` |
| `ll_org_name` | Application `organization_name` |
| `ll_instance_id` | `instanceId` |
| `ll_instance_name` | `instance.display_name`, or `"unknown"` |
| `language` | UI language code, `"en"` if the app is single-language |
| `user_properties` | Object, see below |

Event-specific properties (the "Extra properties" column) are merged on top. The fixed keys above
always win, so integrator-supplied custom properties can't override them.

**App and org names:** `GET {LIVELIKE}applications/{clientId}/` (no auth) returns `name`,
`organization_id` and `organization_name`. Fetch it once at startup; on failure, send empty strings.

## User properties (`data.user_properties`)

| Key | Value |
|---|---|
| `ll_username` | `profile.nickname`, or `"Anonymous"` |
| `ll_user_id` | `profile.id` |
| `user_uid` | `profile.id` |
| `profile_id` | `""` (reserved) |
| `custom_id` | `profile.custom_id`, or `""` |
| `is_new_user` | `null` (reserved) |
| `device_type` | `"Mobile"` \| `"Tablet (iOS)"` \| `"Tablet (Android)"` \| `"Desktop"` |
| `browser` | `"Chrome"` \| `"Safari"` \| `"Firefox"` \| `"Edge"` \| `"Opera"` \| `"Internet Explorer"` \| `"Other"` |
| `platform` | `"Windows"` \| `"Mac"` \| `"Linux"` \| `"Android"` \| `"iOS"` \| `"Unknown"` |
| `country` | Country **name** (e.g. `"United States"`) derived from `Intl.DateTimeFormat().resolvedOptions().timeZone`, or `""` |

Device rules (from `navigator.userAgent`, lowercased):
- iPad, or `MacIntel` with touch points, is `Tablet (iOS)`.
- `android` without `mobile` is `Tablet (Android)`.
- `android`, `iphone` or `ipod` is `Mobile`.
- Anything else is `Desktop`.

Native apps should send the same value sets from their own platform APIs.

## Batching: 2-second buffer

```ts
const FLUSH_MS = 2000      // send at most every 2 s
const MAX_BUFFER = 20      // or immediately once 20 events are queued

let buffer: AnalyticsEvent[] = []
let timer: ReturnType<typeof setTimeout> | null = null

function track(name: string, extra: Record<string, unknown> = {}) {
  buffer.push({ name, data: { ...extra, ...defaultProps, event_name: name, event_category: 'interaction',
                              created_at: new Date().toISOString(), user_properties: userProps } })
  if (buffer.length >= MAX_BUFFER) return flush()
  if (!timer) timer = setTimeout(() => { timer = null; flush() }, FLUSH_MS)
}

function flush(keepalive = false) {
  if (timer) { clearTimeout(timer); timer = null }
  if (!buffer.length) return
  const events = buffer
  buffer = []
  saveAnalytics(events, keepalive)          // apis/analytics, fire and forget
}
```

Rules:
- The **first** event in an empty buffer starts the 2 s timer. Later events join the same batch and don't reset the timer.
- When the buffer reaches **20 events**, flush immediately.
- **Unmount** (leaving the game screen, route change): track `session_stop`, then `flush()`.
- **Page unload:** track `session_stop`, then `flush(true)`. `keepalive` lets the request finish after the page closes. On mobile, `beforeunload` is unreliable, so also listen to `pagehide`.
- `session_stop` fires **once**: whichever of unload or unmount happens first. Guard it with a flag.
- Swap the buffer out before sending, so events tracked during the request go into the next batch.
- Remove the unload and pagehide listeners, and clear the timer, on unmount.
