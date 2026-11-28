# Shuffle Cut V1: storyboard and shot list

Episode `e2a-shuffle-cut-v1`, 1080x1920, 30 fps, 36.75 s. Edit generator `tactical/episodes/_gen-shuffle.py`.
Every shot reads the same play (`tactical/plays/shuffle-cut-v1.json`) through a time remap (edit time -> play time).
Play time below is ENGINE time (owner time + 0.6 s). Marks: entry release 0.85, O3 catch 1.45, screen set 1.85,
O1 plant/burst 2.15, pass release 2.70, contact X1-O5 2.75, brush 2.80, catch 3.45, layup release 4.10, make 4.55.

Camera convention: the cut side is engine +x; every camera yaw is in [-66, 0] so the basket stays at the top of the
frame in every shot (it never switches sides). Checked with `scripts/frame-fit.mts` (wide shots: all ten players in
the safe band).

| # | Edit time | Brief beat | Voice | Play time | Camera | Graphics |
|---|---|---|---|---|---|---|
| 01 HOOK | 0.00-4.30 | 0-3 s hook freeze on the cut | "One screen. One cut. And the defender never sees it coming!" | 2.20 -> 2.82 (O1 brushing O5), then FREEZE from "cut." | A: close-up on O1 / X1 / O5 (yaw -28 to -34) | title ONE SCREEN. ONE CUT., BACK SCREEN floor stencil, spot on O1, focus on X1, pin NEVER SEES IT (gated: O1 behind X1) |
| 02 FULL | 4.30-7.95 | 3-8 s full play | "This is the Shuffle Cut." + 1.9 s pause | 0.70 -> 4.35 REAL TIME | B: broadcast, all ten | title THE SHUFFLE CUT, REAL TIME stamp, O1 trail during the cut, ball trail |
| 03 SETUP | 7.95-14.85 | 8-15 s setup | "First, the ball swings to the wing. Now watch the big man. He sets the back screen... right behind the defender." | rewind -> 0.55; entry pass on "swings" (0.85) -> catch on "wing." (1.45); screen set on "screen..." (1.87); x0.25 to 1.97 | B wide (wing entry) -> C low on the screener -> C2 | ball path O2->O3, WING / BIG MAN pins, O5 trail, BACK SCREEN stencil (pops at the plant 1.85), title BACK SCREEN (gated: screen set), X1 vision cone + BALL-WATCHING |
| 04 CUT | 14.85-20.50 | 15-23 s critical cut | "The cutter waits for it. Slow... slow... then he explodes off the screener's shoulder!" | rewind -> 1.15; set-up walk and pause 1.35-2.00 (x0.4); plant on "explodes" (2.17); x0.45 to the brush on "shoulder!" (2.80) | D: tracking O1 with O5 and X1 | CUTTER pin, CHANGE OF PACE chip, flash + punch on the plant, title EXPLODE, shuffle-cut arrow (route, consumed as he runs), O1 trail, x0.5 stamp |
| 05 CHASE | 20.50-23.55 | 15-23 s (pursuit) | "The defender gets caught chasing, right into the screen." | rewind -> 2.17; x0.3 to contact on "screen." (2.76) | G: slow-motion replay, low on the screen | REPLAY x0.25 stamp, X1 ghost trail (pursuit), O1-X1 separation (gated: X1 delayed), lock ring on X1 at the contact, title INTO THE SCREEN |
| 06 FINISH | 23.55-27.45 | 23-29 s finish | "The wing hits the cutter in stride... and there's your layup!" | 2.81 -> catch on "stride..." (3.45, x0.55) -> release on "there's" (4.10) -> make on "layup!" (4.55) | F0 pass lane (O3 and O1 in frame) -> F low on the cut side (gather, take-off, glass) | ball path O3->O1, green passing lane, IN STRIDE pin, LAYUP. chip, hoop glow, honesty micro caption VS. THIS COVERAGE: X1 CHASES, NO SWITCH |
| 07 RECAP | 27.45-36.75 | 29-35 s overhead replay + takeaway | "Screen. Cut. Finish. That's why timing matters more than just speed. One screen. Perfect timing. Easy advantage." | rewind -> 1.80; replay x1.15 to the make (4.55), hold | E: overhead tactical | SCREEN. / CUT. / FINISH. kinetic titles on the words, BACK SCREEN stencil, O1 cut arrow (gold), X1 chase arrow (red), hoop glow, TIMING > SPEED, ONE SCREEN. PERFECT TIMING., logo |

Audio: Nathaniel (eleven_v4) one take, 1.9 s pause inserted after "This is the Shuffle Cut." so the full play runs in
real time, 0.45 s before "Screen. Cut. Finish."; licensed E2A cinematic bed `cine-10` (ElevenLabs Music, E2A account)
with accents on "explodes", "screen." and "layup!"; mix at -16 LUFS, voice dominant, no bounce SFX, no whooshes,
no crowd (`autoSfx: false`).
