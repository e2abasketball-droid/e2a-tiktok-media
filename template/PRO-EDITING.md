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

## 8. Music (v3)

`render-pro.sh` now builds the music for each episode with `../music/e2a_music.py` (see
`music/README.md`). It picks a library track from the episode style and rotates through the library.
The bed is arranged to the episode length, the drops land on the scene cuts nearest 30% and 75% of
the narration, and the level is set from `public/<voice>`. It plays at volume 1 (`music.premixed`).

To steer the music, set any of these in the episode's `music` field:
- `story`: one of curiosity, record, highlight, tactical, surprise, psychology;
- `dropAt` and `payoffAt`: anchors for the two drops;
- `track`: a library id;
- `engine: "file"` with `src` and `volume`: uses a fixed file instead.

## 9. Visual editing v4: real images first, then graphics

The goal is a Reel that looks edited from real basketball images, with motion graphics on top,
not a sequence of text cards on navy. **This is the standard for every new episode (approved
2026-11-03).** For each video:

1. Look for free-licence images with `scripts/fetch-commons.mjs` before writing the storyboard:
   the player or subject, the arena or city, and 2-3 generic basketball shots (ball, hoop, net,
   crowd, court) as B-roll. Put them in `public/media/<episode-id>/` with credit, licence and year.
2. Open on a real image: scene 0 has `bg` (duotone) or is a `media` scene, and something changes
   before 2 s.
3. Put a photo plate (`bg`) behind most stat, scoreboard, headline and timeline scenes, alternating
   `treatment` and `layout`; use `inset` to keep a face on screen. Only `court` stays on navy.
4. The validator must print no composition, dark-run or hook warnings. Fix the storyboard if it does.
5. If Wikimedia is unreachable or there is no free image, fall back to the dark backdrops: never
   use protected images or invented scenes. Say so in the daily report.

`episodes/miller-v4.json` is the reference episode.

### New scene options (any scene type)

- `bg`: a real photo or clip behind a graphic (stat, scoreboard, headline, timeline, split).
  It needs `credit` and `license` like `media`. Set `treatment`:
  - `duotone` (default): the navy and gold brand grade, for the hook and big numbers;
  - `tint`: the photo's natural colours, slightly darkened, when the place or player should read;
  - `blur`: an out-of-focus plate behind dense graphics such as timelines and long headlines.
- `layout`: `center` (default), `low` (graphic in the lower half, photo visible above), `high`
  (graphic in the upper half, photo visible below), or `compact` (smaller card, more photo around it).
- `inset`: a framed photo card that slides in at `at`, top-left (`tl`) or top-right (`tr`), with an
  optional `caption`. Use it to keep a face on screen during a stat or timeline.
- New sound effects: `bass_hit`, `impact_big`, `swish`, `squeak`, `crowd_cheer`, `reverse_cymbal`.

### Impact, automatically

- **Hook:** frame 1 slams in from 1.3x with motion blur, a white flash, a shake and a big impact.
- **Numbers:** a stat figure slams down from 1.5x with a gold shock ring, a bass hit and a shake.
  Score changes slam in the same way.
- **Music:** `episode-music.mjs` passes the drop and payoff times (`music.hits`), and the picture
  shakes and flashes on them, so the edit hits with the music.

### Scene selection, in this order

1. **Real footage or a real photo of the subject:** a `media` scene, or a `bg` behind the graphic.
   Use only public domain, CC0, CC BY or CC BY-SA images, or licensed material, with credit on screen.
2. **A real photo of the place, era or sport** (the arena, the team, a ball, a hoop, a crowd) as
   `bg` B-roll. Its credit must say what it is; never present it as the event itself.
3. **A motion graphic** (stat, scoreboard, timeline, split) over that plate.
4. **A diagram** (`court`) when the story is a play: it stays on navy, because the court is the image.
5. **A dark backdrop** (`arena`, `spotlight`, `navy`) only when there is no authorised image at all.

Never download from protected sources without permission, and never present a recreation or AI
image as real: those use `kind: "recreation"` and are labelled on screen.

### Variety rules (checked by `validate-episode.mjs`)

- Two consecutive scenes must not share the same composition (scene type + plate + layout).
  Change at least one of them.
- No more than 6 s in a row of text on a dark backdrop when the episode has photos.
- Scene 0 must show a real image when one exists, and something must change before 2 s
  (a second figure, a callout, a beat or a cut).
- Alternate scales: full-bleed photo → graphic on a photo plate (low or high) → compact card → diagram.

The Miller test (`episodes/miller-v4.json`) uses all of these: stat over a duotone photo (hook) →
scoreboard low over the arena → compact headline on a blurred plate → full-bleed photo → court
diagram → scoreboard slam over the crowd → timeline with a photo inset → final stat high over a photo.

## 10. Quality v5: less sound, more story

### Sound design
- Cuts are clean by default: no automatic whoosh, whip or impact on scene changes. Set
  `"sfxTransition": true` on a scene only when the cut really needs a sound.
- Automatic highlights follow a budget (`sfxBudget`, default 3). The renderer ranks candidate moments
  (score changes and figures landing first, then second figures and stamps). It keeps the best ones,
  at least 1.5 s apart and never on top of a music drop. Count-up ticks, timeline ticks and the end
  whoosh are gone, because the music already hits there.
- A scene's own `sfx` (swish on a made shot, crowd on a tie, a sneaker squeak) always plays. Keep
  2-4 highlights per Reel in total; the validator warns above 4 hand-placed effects.
- All effects are 4 dB lower than before, and 6 dB lower again when they land on a spoken word.
  Hierarchy: narration > music > effects.
- The screen shakes only on the hook and the climax (the hit nearest the music payoff). Other hits
  get a soft flash.

### Openings (`hook`), rotate between videos
- `stat-slam`: the figure slams in over a duotone photo (scene 0 = stat with bg).
- `photo-line`: full-bleed photo, slow push, the hook line in subtitles (scene 0 = media).
- `split`: two images or figures whip in side by side (scene 0 = split).
- `clock`: hard cut onto a running game clock (scene 0 = scoreboard with timer, or stat).
The validator warns when the last 2 videos used the same opening (read from `music/history.json`).

### Endings (`ending`) and social texts (`social`)
- `ending`: `debate`, `surprise`, `fact` or `emotion`. About 1 in 3 videos uses `debate`. The
  validator warns if debate repeats within 3 videos, or if the same ending is used 3 times in a row.
- Debate endings are open statements built on real facts: "Some consider this the greatest comeback in
  NBA history." Never end with "comment below", "what do you think", "agree or disagree", "tag a
  friend" or similar. The validator rejects these phrases in the narration and in `social`.
- `social.caption`: short English caption. `social.pinnedComment`: a genuine basketball comparison
  or question to post as the first comment (Metricool `firstCommentText`; pinning stays manual in the
  apps). `social.reply`: a factual follow-up for when people answer. Never invent fan opinions.

### Layout and subtitles
- `layout: "corner"`: the scoreboard becomes a small broadcast bug, top-left, over a full photo.
- `captions: "high"` on a scene moves the subtitles up when a face or the action sits low in the frame.
- Don't give a media scene a title that repeats the narration: the subtitles already say it.
- Something must change at least every ~3 s (cut, beat, callout, second figure, inset or score). The
  validator warns otherwise.

### Real media library (`scripts/media-library.mjs`)
```
node scripts/media-library.mjs search "Reggie Miller" --role subject     # the person: Commons + Openverse only
node scripts/media-library.mjs search "Madison Square Garden" --role place
node scripts/media-library.mjs search "basketball hoop net" --role broll --video   # stock clips allowed
node scripts/media-library.mjs fetch <id>        # downloads once into public/media/library/, returns a media object
node scripts/media-library.mjs list --role broll # reuse what is already in the library
```
- Every result is licence-checked (public domain, CC0, CC BY or CC BY-SA; Pexels and Pixabay
  licences only for generic B-roll). Each one is catalogued in `media-library.json` with source,
  licence, author and year.
- Searches and files are cached, so nothing is fetched twice. Failed searches are not cached.
- `subject` results must name the subject in their title or description. When nothing matches,
  use place or B-roll images: never a lookalike, and never generic footage presented as the event.
- Pexels and Pixabay need free keys (`PEXELS_API_KEY`, `PIXABAY_API_KEY`). Without them, the script
  searches Commons and Openverse only.

`episodes/miller-v5.json` is the reference episode for v5.

## 11. Audio mix v7: voice first (central config)

Every level now lives in `template/audio-mix.json`. Change a number there and all future videos follow it. Do not hard-code levels in an episode.

The order of priority is: 1, the narration; 2, the music as background; 3, effects as occasional details.

- **Voice** (`scripts/episode-music.mjs`):
  - high-pass at 80 Hz, +2 dB presence at 3.2 kHz (for phone speakers), gentle 2.5:1 compression
  - levelled to -16 LUFS with peaks at -2 dB
  - written to `public/audio/<voice>.mix.mp3`; the original file is untouched
- **Music** (`music/e2a_music.py`, also used by `music/e2a_cinematic.py`):
  - about 21 dB under the voice while someone talks, and at least 23 dB under it in the speech band (300–4000 Hz)
  - drops 8 dB (mids and highs) and 6 dB (bass) when the voice comes in, and only comes back up in real pauses (at least 0.45 s)
  - low shelf of -4 dB below 140 Hz
  - 0.6 s of silence just before the payoff cut; the music comes back on the payoff
- **Effects** (`src/pro/Pro.tsx`): 8 dB lower, a further 8 dB lower on a spoken word, at most 2 per video, and a swish (not an impact) for a score change.
- **Master** (`render-pro.sh`): one loudnorm pass on the whole mix, -14 LUFS and -1.5 dBTP. Tracks are never normalised separately.
