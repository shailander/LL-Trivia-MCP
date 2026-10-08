# LiveLike Trivia: Overview

LiveLike Trivia is a quiz game configured in the LiveLike CMS and played inside the client's own app.
The CMS publishes a **trivia instance** (one quiz). The instance points to a LiveLike **program**,
and the program holds the questions as **text-quiz widgets**. The game reads the questions, merges
in the answers this user already gave, shows the questions one by one, submits each answer to
LiveLike, and finally shows a result screen.

You are building this game natively in the user's app. **Theming is out of scope.** Ignore any
`whitelabel` / `theme` data and style every screen with the app's own design system.

## Inputs you need from the user

| Input | Required | What it is |
|---|---|---|
| `clientId` | yes | LiveLike application client ID. |
| `gameId` | yes | Arcade game ID of the trivia game (from the CMS). |
| `instanceId` | no | A specific quiz to play. If it's missing, resolve it from the instance list (see `instance-resolution`). |
| `accessToken` | no | An existing LiveLike profile token, for signed-in users. If it's missing, the SDK creates an anonymous profile (see `sdk-init`). |

## Glossary

| Term | Meaning |
|---|---|
| profile | A LiveLike user. `LiveLike.init` returns it as `{ id, access_token }`. |
| profileId | `profile.id`. Used in the widget-interactions URL. |
| authToken | `profile.access_token`. It goes in every authenticated call. |
| instance | One trivia quiz, with its CMS config (`setting`) and `program_id`. |
| program | A LiveLike program holding the question widgets. |
| widget | One question (`kind: "text-quiz"`). Its `custom_data` is a JSON **string** with the game config. |
| interaction | An answer this profile already submitted to a widget. |

## Environments

| Env | ARCADE base | LIVELIKE base (also the SDK `endpoint`) |
|---|---|---|
| production | `https://arcade-backend.livelikecdn.com` | `https://cf-blast.livelikecdn.com/api/v1/` |
| staging | `https://arcade-staging-backend.livelikecdn.com` | `https://cf-blast-staging.livelikecdn.com/api/v1/` |

Note the trailing slash on the LIVELIKE base. Paths are appended directly, e.g. `${LIVELIKE}programs/...`.

## Auth header rules (easy to get wrong)

| Host | Header |
|---|---|
| ARCADE (`/v1/minigames/...`, `/v2/minigames/instances/...`) | `Authorization: <authToken>` (**raw token, no `Bearer`**) |
| LIVELIKE (`profiles/...`, `answer_url`, `impression_url`) | `Authorization: Bearer <authToken>` |
| Instance details, program widgets | no auth |

## The three screens

1. **Welcome**: title, how-to-play and a start button. The CMS can skip it.
2. **Game**: one question at a time, with an optional timer, submission, and optional correct/incorrect feedback and points.
3. **Result**: score, a title message, optional points, optional per-question review, optional share.

## Tools on this server

- `start_trivia_integration()` returns this page, the questions to ask, and the flow.
- `get_doc(topic)` returns any page listed below.
- `list_instances`, `get_instance_details` and `get_questions` are live, read-only tools. Use them to inspect the user's real CMS data while building, so you see the real field values.

## Doc topics

- `sdk-init`: install and initialise `@livelike/engagementsdk` and get the profile.
- `flow`: end-to-end call order and the screen state machine.
- `instance-resolution`: which instance to play when no `instanceId` is given.
- `data-merge`: how to turn widgets and interactions into question state. **Read this one.**
- `live-trivia`: (advanced) time-synced live trivia.
- `apis/instance-list`, `apis/instance-details`, `apis/program-widgets`, `apis/widget-interactions`,
  `apis/widget-impression`, `apis/submit-interaction`, `apis/trivia-credit`, `apis/game-completed`
- `screens/welcome`, `screens/game`, `screens/result`

## Out of scope

Theme and whitelabel styling, localization and translations, analytics, leaderboards and rewards.
