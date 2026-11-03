# E2A Pro editing system (template v3)

The `Pro` composition turns one JSON file per video into a finished Reel. It sits next to the
existing `Daily` composition, which keeps working unchanged.

```
Research -> Verification -> Script -> Storyboard (episode JSON) -> Visual selection
-> ElevenLabs narration -> word timings -> Remotion render -> QC -> Metricool
```

## 1. Audit of the previous system (Daily / plans.tsx)

| Area | What it did | Why it looked like a slideshow |
| --- | --- | --- |
| Scenes | A hand-written TSX `planN()` per video; every scene is `Stage` + `Pop` + big Anton text | Same entrance (spring pop) and same centred layout in every scene |
| Background | One navy radial gradient with a faint court for the whole video | No depth, no imagery, nothing changes between scenes |
| Transitions | 0.18 s opacity fade | No cuts, no motion between ideas |
| Camera | None | Text and graphics sit still on a static plate |
| Branding | `E2A │ SERIES NAME` header on screen for the whole video | Series name shown in the first second, which the brief now forbids |
| Subtitles | 4-word chunks, active word turns gold | No emphasis on numbers or key words; numbers spelled out ("EIGHT POINT NINE") |
| Sound | Narration + music at a fixed 0.12 | No sound design; music doesn't duck under the voice |
| Length | 40-58 s | Long for curiosities; retention drops |
| Images | None | No real photos or footage at all |

## 2. What the Pro system adds

- **Episode JSON instead of TSX** (`episodes/<id>.json`, type in `src/pro/types.ts`). Scene timing
  is anchored to phrases in the narration (`"at": "Reggie Miller drains"`), so the automation
  writes data, not code. `"phrase#2"` = second occurrence.
- **Scene types** (`src/pro/graphics.tsx`, `backdrops.tsx`):
  `media` (real photo/clip with credit), `headline` (cinematic mask reveal), `stat` (counter that
  lands with a hit, optional second figure), `scoreboard` (broadcast bug with live score changes and
  a timer), `timeline`, `split` (comparison), `court` (the existing tactical diagram).
  Any scene can add `callouts` (stamped "+3", "TIED"...), `beats` (camera punches on words) and
  `kicker` (small gold context line).
- **Virtual camera** (`camera.tsx`): push-in, pull-out, pans, tilts, drift, plus beat punches.
  Layers sit at different depths, so moves create parallax (crowd far, floor near).
- **Backdrops with depth** when there is no footage: arena (crowd bokeh, stadium beams, floor in
  perspective, haze), spotlight, navy, archive.
- **Transitions**: whip pan with motion blur, punch-in with gold flash, zoom-through, slide-up,
  white flash, hard cut.
- **Finishing**: film grain, vignette, warm light leak (strength set per style).
- **Subtitles** (`subtitles.tsx`): word-by-word reveal from the real timings, max two lines,
  numbers and chosen words highlighted (gold box on the active word), `display` map turns
  "eight point nine" into "8.9". Kept inside the safe area: top 220 px, bottom 420 px and the
  right 150 px are left free for the Instagram/TikTok/Shorts interface.
- **Sound design** (`public/sfx/`, generated with ffmpeg in this repo, so no licensing issues):
  whoosh/whip on transitions, impacts on stats and callouts, ticks on counters and timelines,
  ball bounce on score changes, optional arena bed. Music ducks under the voice and lifts in gaps.
- **Outro**: 1.4 s logo sting (official white E2A logo + "MORE THAN A GAME"). No logo or series
  name at the start.
- **Styles per story type** (`styles.ts`): `record`, `player`, `tactical`, `comparison`,
  `curiosity` each set their own transition rhythm, camera moves, grain, caption size and music
  level, so videos don't all cut the same way.

## 3. Storyboard recipes (20-25 s)

| Time | Beat | record | player | tactical | comparison | curiosity |
| --- | --- | --- | --- | --- | --- | --- |
| 0-2 s | Hook | `stat` with the shocking number | `media` (best photo) + headline | `court` at the key moment | `split` teaser | `headline` with the claim |
| 2-7 s | Context | `scoreboard` / `media` | `timeline` start | `court` setup | `media` x2 | `media` / `headline` |
| 7-17 s | Reveal | `scoreboard` changes, `callouts`, `court` | `media` + `timeline` | `court` + steps | `split` stats | fast `media` cuts, `stat` |
| 17-23 s | Payoff | `stat` second figure | `stat` / quote | `court` result | `split` winner | `stat` / reveal |
| 23-25 s | Brand | outro | outro | outro | outro | outro |

Rules the validator enforces or warns about (`scripts/validate-episode.mjs`): every anchor must be
in the narration, sources are required, a new visual every 2-4 s, no static camera over 2.5 s,
no three identical scene types in a row, 20-25 s for non-tactical stories, media must carry
credit + licence, AI imagery must be `kind: "recreation"` (labelled "Recreation" on screen).

## 4. Real images and footage

Priority: (1) public domain / CC images of the actual people and events, (2) E2A's own footage,
(3) licensed agency images (needs a paid licence, e.g. Getty/AP/NBA Photos, record the licence id),
(4) graphics-only scenes, (5) labelled recreations. Never a random image that isn't the story, never a
realistic AI image of a real player.

`scripts/fetch-commons.mjs "File:<name>" public/media/<date>/<file>` downloads from Wikimedia
Commons, refuses NC/ND or unknown licences and prints the `media` block with credit and licence.
Most NBA game photos after 1960 are copyrighted and are not on Commons; for those stories use
graphics, or buy a licence.

Network access needed: `commons.wikimedia.org`, `upload.wikimedia.org` (and
`elevenlabsusercontent.com` to download narration).

## 5. Higgsfield (optional, off by default)

Use only when real material doesn't exist and a scene needs atmosphere (an empty 1890s gym, a
crowd from behind, a ball through a net). Never for real players or for "evidence" of a historical
fact.

1. Write the shot list in the episode as `media` scenes with `kind: "recreation"` and
   `src: "media/<date>/<shot>.mp4"`.
2. Check Higgsfield credits first and get approval for the spend (no automatic generation; the
   daily automation must stop and report instead).
3. Generate 9:16, 5 s or less per shot; save into `public/media/<date>/`.
4. The credit chip shows "Recreation · Higgsfield AI" on screen.

There is no Higgsfield connector or API key in this project yet; adding one is a settings task for
the account owner.

## 6. Render and QC

```bash
cd template && npm ci
# narration in public/audio/<id>.mp3, timings in the episode's "words"
scripts/render-pro.sh episodes/<id>.json out/<id>.mp4          # validate -> render -> encode -> QC
```

`render-pro.sh` renders 1080x1920 (30 fps, or 60 with `"fps": 60`), re-encodes H.264 High,
yuv420p, CRF 19, normalises to -14 LUFS / -1.5 dBTP, then `qc-pro.mjs` checks resolution, fps,
codec, duration, loudness, true peak, black frames, frozen stretches over 2.5 s and size, and
writes `<out>_qc/contact.jpg` plus five full frames. A pass is only technical: open the contact
sheet and check subtitles, framing, legibility, image-to-narration match and the facts before
scheduling. If anything fails, fix the episode and render again.

## 7. Pilot

`episodes/pilot.json`: Reggie Miller, 8 points in 8.9 seconds (record style), 25 s, re-cut from the
narration of the 2026-11-02 video so the old and new edits can be compared on the same story.
