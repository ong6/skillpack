# Animation that survives the export and the loop

Use this checklist for rallies, moving charts, walk cycles, camera pans, repeating backgrounds and
any animation the user expects to keep playing. Review the moving export, not only a hero frame.

## Pick the right kind of motion

- Character poses and attached props: author in Blender, then bake compatible clips. Use the
  companion [blender-authoring](../blender-authoring/SKILL.md) for headless construction, materials,
  keyframes and rendering. Its animation and rendering references cover the export preparation.
- Runtime charts and scrolling history: use data-driven code and a stable viewport. Model physical
  objects around the screen; keep the chart itself a coherent flat display.
- Repeated actions need a repeatable authored cycle. Ping-pong reverses time; it is usually wrong
  for a ball flight, a rally or a market timeline.
- A one-shot and a loop are distinct playback modes. Declare the mode per scene and derive player
  behavior from it. Do not bolt modulo time onto an animation while its player still stops after
  five seconds. One-shot scenes must retain their existing finish/replay behavior.

## Author events before interpolation

Write down contact times, contact objects, coordinate system, period and resting pose before
keyframing. For a rally, define both racket strikes, net clearance, bounce and recovery. Compute
ball endpoints from the actual racket transforms. A ball hitting an approximate nearby point is
not enough. Keep grip, racket orientation and foot planting attached to the player throughout.

Bake constraints when needed and inspect both local and world transforms. Duplicated characters
need separate animation state and intentionally shared or cloned materials. A recolor must not
silently recolor the opponent. Verify whether the exported scene has one clip or several object
clips; play the required tracks together instead of assuming the first clip animates everything.

Use a single elapsed-time source. Match source frame zero, FPS, clip duration and runtime seconds.
Avoid incrementing position once per rendered frame. Set interpolation deliberately: easing helps
anticipation and recovery; it must not cause overshoot through a floor or change a constrained
contact. Linear interpolation between sufficiently sampled baked frames is often appropriate.

## Make the boundary invisible

- Compare first and last poses, including joints, props, camera, materials and visibility.
  Match velocity too when continuous movement crosses the seam.
- Sample just before and after the boundary. A perfect match at exactly zero and duration can
  still hide a one-frame snap. Run at least three cycles in the actual player.
- For continuous pans, move the viewport steadily, recycle data or geometry outside the visible
  region, and clip to the display. Never scale candles down to nothing or teleport visible marks.
- Keep a coherent timeline. Repeating synthetic prices can coexist with forward-moving labels;
  label the study as simulated. Do not imply a live feed or real trading results.
- For an OHLC chart: high contains open/close, low contains open/close, body color follows the
  close versus open, wicks use the same price scale, volume has a separate baseline, and each
  candle and its volume share an X position. Do not use arbitrary decorative buy/sell bars.

## Check the player and export

1. Test the exported model's two-way contacts and the loop boundary numerically, then inspect
   those exact moments visually. Tests establish constraints, not aesthetic quality.
2. Check several cycles in the real browser. Pause must freeze the current frame; resume continues
   from it. Returning from a hidden tab must not race forward to catch up.
3. Reduced motion selects an intentional static pose. It must stay still after resize, theme
   changes and opening the canvas. Never require a looping animation to convey essential text.
4. Variants are chosen once on mounting and survive pause/resume, theme changes and expanded
   views. Offer a pinned variant for reproducible review. Test each authored variant.
5. Verify asset failure, context loss and cleanup, including mixers, textures and shadow maps.
   Avoid per-frame geometry construction and texture allocation. Measure canvas texture upload
   cost if the display is repainted every frame.
6. Measure the built consumer at desktop and phone width, and say whether physical mobile hardware
   was tested. Observe frame rate, frame gaps, memory growth and downloaded bytes; average FPS
   alone does not establish smoothness. Record the evidence and fix the limiting layer.

## Reviewed references

These are references, not instructions to execute downloaded code. Verify the installed API
version before adapting examples.

- Installed companion: MartinRapcan/blender-claude-skill, MIT. The local
  [upstream record](../blender-authoring/UPSTREAM.md) pins its reviewed revision and modifications.
- CloudAI-X/threejs-skills, `threejs-animation` and `threejs-lighting`:
  https://github.com/CloudAI-X/threejs-skills . Reviewed for topic coverage; no license was declared
  in the repository metadata during review, so its skill text and code were not vendored.
- Runtime authority: https://threejs.org/docs/pages/AnimationAction.html and
  https://threejs.org/docs/pages/AnimationMixer.html . Check loop modes, time units, clip selection,
  interpolation and mixer lifecycle against these docs rather than copying a generic demo loop.
- Export authority: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html .
  Inspect the installed exporter when online documentation is unavailable. Test the exported result.
