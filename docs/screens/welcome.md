# Screen: Welcome

The intro screen shown before the quiz. Style it with the app's own design system. No theme data is used.

## CMS fields (`instance.setting.welcome`)

| Field | Behaviour |
|---|---|
| `skip` | `true` means don't render this screen and go straight to GAME |
| `how_to_play.enabled` | Show the how-to-play block |
| `how_to_play.title` | How-to-play heading (default "How to play") |
| `how_to_play.body` | How-to-play body. **HTML**, so sanitize before rendering |
| `start_btn_label` | Start button text (default "Start") |
| `instance.display_name` | Optional title |

## Behaviour

- Show this screen only when `skip` is false and not every question is already answered (otherwise go to RESULT).
- **Start** sets `step = 'GAME'` at the first unanswered question.
- **Live trivia before start time:** replace the start button with a countdown to `publish_time`, and move to GAME automatically when it reaches 0. See `live-trivia`.

## Sketch

```ts
function renderWelcome(instance, onStart) {
  const w = instance.setting.welcome
  return `
    <h1>${instance.display_name ?? ''}</h1>
    ${w.how_to_play.enabled ? `<h2>${w.how_to_play.title}</h2><div>${sanitize(w.how_to_play.body)}</div>` : ''}
    <button onclick="onStart()">${w.start_btn_label || 'Start'}</button>`
}
```
