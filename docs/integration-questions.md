# Questions to ask the user before building

Ask these **before writing code**. Ask them all in one message, and suggest the default in brackets.

## 1. IDs
- What is your LiveLike **clientId**? (required)
- What is the trivia **gameId**? (required)
- Do you want to pin a specific **instanceId**? (optional. Default: auto-pick the current quiz)
- Are your users signed in with an existing LiveLike **accessToken**? (optional. Default: anonymous profile)
- Production or staging? (default: production)

Once you have them, call `get_instance_details` (or `list_instances`, then `get_instance_details`), then
`get_questions(program_id)`. This shows the real CMS config, and you can tell the user what the CMS already decides.

## 2. Screen and behaviour choices

Each choice has a CMS field that already controls it. Default to **honouring the CMS field**, so that
producers keep control. Only hard-code a behaviour when the user explicitly asks for that.

| Ask the user | CMS field (source of truth) | If the user wants to override |
|---|---|---|
| Show a **welcome screen** before the quiz? | `setting.welcome.skip` (`true` means no welcome screen) | Always or never render the welcome step. |
| Show a **how-to-play** section on the welcome screen? | `setting.welcome.how_to_play.enabled` | Always show or always hide it. |
| Show **correct/incorrect feedback right after each answer**? | per question: `custom_data.feedback_enabled` | Always or never show feedback after submit. |
| Show **points right after each answer**? | per question: `custom_data.feedback_enabled`, and `points` or `incorrect_points` greater than 0 | Show or hide the `+N` points label after submit. |
| Show the **final score at the end** (result screen)? | The result screen always shows "You got X out of Y correct". Total points are shown when `setting.results.show_points` is true. | Hide or show the total-points line. |
| Let players **review their answers** from the result screen? | `setting.results.review_questions` | Enable or disable tapping a question number to review it. |
| Allow **sharing** the result? | `setting.results.share.enabled`, `share.msg`, `share.deep_link` | Show or hide the share button. |
| Auto-advance to the next question after submitting? | per question: `custom_data.show_next_question` | (keep CMS) |
| Use a question timer? | per question: `custom_data.time_interval` (0 means no timer), `timer_type` | (keep CMS) |

## 3. Platform
- Which framework or app is this going into? Follow its conventions for state, routing and styling.
- The examples in these docs are framework-agnostic TypeScript with `fetch`. Adapt them.

After the answers come in, read `sdk-init`, `data-merge`, then `screens/welcome`, `screens/game` and
`screens/result`, plus the `apis/*` page for each call you write.
