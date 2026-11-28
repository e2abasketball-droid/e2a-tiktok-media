# V2 visuals: court, light, cameras, graphics, edit (Parts VIII-X)

## Court, materials, light

- New env `arena` (opt-in, other episodes unchanged): one overhead key light fixed to the court (not to the camera),
  shadows straight under the players and identical in every shot; cool sky / warm floor hemisphere, two soft fills,
  a back rim light. The floor is slightly more matte (roughness 0.68) so the key does not blow out on the wood.
- Same court geometry, line set and E2A colours as V1; the stands and crowd are the existing low-detail set.
- Honest limit: this is stylised real-time 3D (three.js in Remotion), not photoreal. Skin, cloth and hair are simple
  shaded materials; there is no global illumination or motion blur.

## Cameras (all keep the basket at the top or to one side so the viewer never loses orientation)

| Shot | V1 | V2 |
|---|---|---|
| 08 REVEAL | one wide weak-side orbit held, slow push | isolate X4 (close follow, his eyes on the ball) -> X4 steps in with O5 in frame -> camera follows O4 and X4 as the separation opens -> widens to the passing window O5 -> O4 |
| 09 FINISH | follow O4 from the weak-side wing | passing window -> low weak-side camera at the rim for the gather, take-off, release and glass, slowed x0.5 and labelled "x0.5" (honest slow motion), push-in for the make |
| others | unchanged framing (validated in V1) | same, with the arena light |

## Graphics

- Kept: world-space markers under the feet, motion trails, X4's vision cone, ghost of X4's start spot, O4's route on
  the floor, A/B/C badges anchored to the players, the honest 2.0 s decision countdown, every claim gated by the
  tactical validator's truth windows.
- Changed: in the reveal the open passing lane O5 -> O4 appears in green on the floor as the cut opens (a floor ring for
  the X4-O4 distance was tried in Render B and removed: with the vision cone and the route it was too much on screen); the finish replaces the screen chip "LANE: OPEN" with an "OPEN" tag
  pinned to O4.

## Story and pacing

Same 10-shot structure and the same Nathaniel take (no regeneration, so the timeline and the music bed are unchanged:
32.8 s). The pacing change is inside the shots: the reveal spends its slow motion on the moment X4 loses O4, and the
finish spends 1.4 s on 0.7 s of the layup instead of hiding it.
