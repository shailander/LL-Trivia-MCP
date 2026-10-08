# Resolving the instance when no instanceId is given

A game can have many instances (e.g. one quiz per week). Without an `instanceId`, pick the one
that is "current" by schedule.

## Steps

1. `GET {ARCADE}/v2/minigames/instances/{gameId}/list/?application_id={clientId}&all=yes`
   with `Authorization: <authToken>` (see `apis/instance-list`).
2. Keep only the instances that have `setting.schedule.publish_time`.
3. Sort them ascending by `publish_time`.
4. Walk the sorted list:

```ts
function pickInstance(list: Instance[], now = Date.now()) {
  for (let i = 0; i < list.length; i++) {
    const cur = list[i]
    const curLive = !!cur.setting.schedule.is_live_trivia
    if (i === list.length - 1) return { instance: cur, live: curLive }   // past the last one: show the last
    const curT = Date.parse(cur.setting.schedule.publish_time)
    const nextT = Date.parse(list[i + 1].setting.schedule.publish_time)

    if (now < curT) return { instance: cur, live: curLive }               // first not started yet
    if (now > curT && now < nextT) {
      if (!curLive) return { instance: cur, live: false, nextPublishTime: nextT }
      const showUntil = cur.setting.schedule.show_until
        ? Date.parse(cur.setting.schedule.show_until)
        : nextT - 60 * 60 * 1000                                         // default: 1h before next
      if (now < showUntil) return { instance: cur, live: true, nextPublishTime: nextT }
    }
  }
  return null
}
```

5. Accept the pick when:
   - it is a live trivia (`live === true`), or
   - `instance.active === 'ACTIVE'`.

   Otherwise there is no game, so show the "No game" screen.
6. Use `instance.instance_id` and continue with `apis/instance-details`.

## "Next trivia on …"

When `nextPublishTime` is known, the result screen can show
`Next trivia on: <Month D, YYYY, at h:mm AM/PM>. See you then!`
