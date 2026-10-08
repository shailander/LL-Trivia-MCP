# LiveLike SDK initialisation

The game needs a LiveLike **profile**: `profileId` and `authToken`. Get one from the LiveLike
Engagement SDK before you call any authenticated API.

## Install

```bash
npm install @livelike/engagementsdk
```

The reference implementation uses `@livelike/engagementsdk@^2.57`.

## Init

```ts
import LiveLike from '@livelike/engagementsdk'

const LIVELIKE_ENDPOINT = 'https://cf-blast.livelikecdn.com/api/v1/' // staging: https://cf-blast-staging.livelikecdn.com/api/v1/

export async function initLiveLike(clientId: string, accessToken?: string) {
  if (accessToken) {
    // The SDK caches the last profile per client in localStorage. Clear it, or the SDK
    // may keep using a cached (e.g. anonymous) profile instead of the token you pass.
    try { localStorage.removeItem(`livelike-user-auth-${clientId}`) } catch {}
  }

  const profile = await LiveLike.init({
    clientId,
    endpoint: LIVELIKE_ENDPOINT,
    ...(accessToken && { accessToken }),
  })

  if (!profile) throw new Error('LiveLike init failed')
  return { profileId: profile.id, authToken: profile.access_token }
}
```

## The two modes

| Mode | When | What happens |
|---|---|---|
| **Anonymous** | No `accessToken` | The SDK creates a new LiveLike profile, or reuses the one cached in localStorage for this `clientId`. Progress survives reloads on the same device. |
| **Existing user** | `accessToken` passed (e.g. from your own login, mapped to a LiveLike profile) | The SDK clears the cached profile, logs in as that profile, and returns it. Progress follows the user across devices. |

The reference app reads `client_id`/`clientId` and `access_token`/`accessToken` from the page URL.
In your app, take them from config or your auth layer instead.

## Profile fields you use

| Field | Used for |
|---|---|
| `profile.id` | `profileId` in `GET profiles/{profileId}/widget-interactions/` |
| `profile.access_token` | `authToken`. Send `Bearer <authToken>` to LIVELIKE APIs and the raw `<authToken>` to ARCADE APIs. |

## Failure handling

If init throws or returns nothing, show a full-screen error ("Sorry, something went wrong. Please
try again later.") and don't render the game.
