# E2A Narration Standard v1 (permanent default narrator)

**Status:** ACTIVE from 2026-11-27 21:38Z. Owner directive: "EVERY E2A Sports video must use this exact narrator voice and this expressive narration methodology unless we explicitly instruct you otherwise."
**Approved reference:** `e2a-basketball-iq-01-v3-master-hookA.mp4`. Published on IG (https://www.instagram.com/reel/DgQrZH3BkyX/) and TikTok (https://www.tiktok.com/@e2a.basketball/video/7712970697273920789).
**Machine-readable config:** `config/e2a-narrator-default.json` · **Module:** `tools/narrator.py` · **Tests:** `tools/tests/test_narrator.py`

## 1. Voice identity (verified, not guessed)
| Field | Value | Source |
|---|---|---|
| Voice | **Nathaniel - Live Football Commentator** (ElevenLabs Voice Library, professional, en-british) | `creative_list_voices` result plus the generation records |
| Voice ID | **`9rR45HW0vcBmpCbkc4m9`** | the V3 generation call (flow `6GOo3uZ0cfVXdKo1XftG`) |
| Model | **`eleven_v4`** | same call |
| Takes per call | 1 (`generations_count: 1`) | same call |
| Voice settings | **Not set.** The approved take used the connector defaults: stability 0.5 per the eleven_v4 schema; similarity default not published. | schema read 2026-11-27 |
| Style, speed, speaker boost | Not exposed by the connector for eleven_v4. Not used. | — |
| Pronunciation | None used. If a name is misread, use IPA between slashes in the prompt. | — |

**Uncertainty that cannot be removed:** the connector does not return the numeric similarity default, so "default" is the recorded value. Keep leaving voice settings unset. That reproduces the approved configuration exactly.

## 2. Performance method (what makes it work)
Natural delivery + high energy + emotional variation + dynamic pacing + credible enthusiasm.
- Write the script in short phrases, one delivery per phrase. Put an inline audio tag before a phrase **only when the delivery changes** (a tag holds until the next one).
- The default arc (adapt it to each script; never copy the same emphasis pattern):

| Phase | Tag used in V3 | Purpose |
|---|---|---|
| hook | `[urgent]` / `[intriguing, confident]` | Attention-grabbing first line, close to the action |
| setup | `[fast]` / `[quick, direct]` | Faster, conversational |
| suspense | `[building suspense]` | Short pauses (ellipses), rising tension |
| explanation | `[measured, confident]` / `[controlled emphasis]` | Slower for the concept, one key word stressed |
| pre-reveal | `[building intensity]` | Intensity rises just before the reveal |
| reveal | `[excited]` / `[energetic reveal]` | The peak: energetic, not shouting |
| payoff | `[fast]` | Quick consequence |
| lesson | `[calm, authoritative]` / `[slower, confident teaching]` | Credible coaching tone |
| close | `[punchy]` | Controlled ending: a question or a call to rewatch |

- Use a `[low ...]` tag for at most one line per script. The 2026-11-27 consistency test showed that takes with more low/suspense lines sit 2–4 semitones lower than the approved master. Keep the hook and the reveal on high-energy tags.
- Punctuation is direction: ellipses for suspense, commas for short beats, CAPS on at most one word per line.
- Avoid: monotone, robotic cadence, long pauses inside the take, fake enthusiasm, constant shouting. Honest silences, such as a decision window, are inserted in the edit, not in the take.
- **One take per script, never regenerated once it is in an edit.** Re-edits reuse the take. A *new* video, or a version the owner asks to be performed differently, gets a new take with the same narrator.

## 3. Audio processing (same chain as the approved master)
`template/scripts/voice-dynamics.py --preserve --mix-lufs -16` (or `python3 tools/narrator.py process ... --run`):
- **Tone:** highpass 85 Hz · -2 dB @ 300 Hz · +3 dB @ 2.8 kHz (Q 1.4) · -1.5 dB @ 7 kHz · de-esser 0.45.
- **Compression (preserve):** threshold -18 dB, 1.6:1, attack 8 ms, release 140 ms.
- **Emotional curve:** per-line offsets of 0 to +1 dB, changed only inside pauses. A line is never turned down.
- **Output:** voice stem at -16 LUFS. Music is ducked under the voice. Final mix -16 LUFS integrated, true peak ≤ -1 dBTP.
- **Measured on the approved master:** -16.0 LUFS / -1.5 dBTP / LRA 4 · voice 12 LU over the music, ~16 LU in the phone band.
- No ball-bounce or dribble sounds, no fake crowd, no gratuitous whooshes.

## 4. How every pipeline uses it
1. Write the script as `{"lines": [[phase, text], ...]}`.
2. `python3 tools/narrator.py params script.json` gives the exact `creative_generate_speech` arguments (voice, model, 1 take, tagged prompt).
3. After generating, `python3 tools/narrator.py check --voice-id <id> --model-id <model>` must print OK before the take is used.
4. Process with the chain above. Then Scribe words → edit → render → QC as usual.

Applies to: Basketball IQ, tactical analysis, pick-and-roll, defensive concepts, basketball psychology, educational content, Film Room lessons, IG Reels, TikTok, YouTube Shorts, and all future E2A Sports videos.

## 5. Override (only by explicit owner instruction)
Put `"narrator_override": true` **and** `"override_owner_message": "<date, thread, owner's words>"` in that episode's own config. Never put it in the global config. `tools/narrator.py check` fails without both fields. Automatic model selection, scheduled tasks and other agents must never change the narrator on their own.

## 6. Reference assets
- `assets/audio/narrator-reference-v3.mp3`: the unprocessed eleven_v4 take used in the approved master.
- `assets/audio/narrator-reference-v3-voice-processed.flac`: the processed voice stem of the approved master.
- Consistency test, 2026-11-27: see `produccion/narrator-consistency-2026-11-27.md`.

## 7. Licence
Voice Library professional voice used under the E2A account's paid ElevenLabs plan. See `config/asset_licences.json` → `voice/elevenlabs-nathaniel/*`.
