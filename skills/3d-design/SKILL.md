---
name: 3d-design
description: >-
  Choose and use a 3D design workflow for UI illustrations, modeled objects, character animation,
  interactive scenes and web delivery. Use for "3D design", "3D animation", "model this",
  "Blender or Three.js", "make the movement natural", "seamless loop", "continuous pan", or selecting and switching 3D tools.
  Covers authoring, runtime, export and visual verification; not ordinary page layout,
  2D architecture diagrams or unrelated Blender installation troubleshooting.
---

# 3D design

Choose the workflow from the visual and interaction needs. Do not default to constructing every
object from browser primitives. Blender authors assets; Three.js displays and controls scenes.
A project may need both.

## 1. Establish the target

Inspect the existing scene, consuming page, design rules and reusable library before editing.
Infer what is already clear; ask only about decisions that would change the work substantially.
Identify:

- The subject, intended camera, visual style and smallest display size.
- The motion beats: anticipation, action/contact, follow-through and resting or looping pose.
- Whether users need rotation, selection, live data, configurable parts or only a fixed shot.
- Required delivery: editable model, interactive web scene, still image or rendered animation.
- Existing engine, authoring tools, source assets, licenses and performance constraints.

Check the actual environment. An option in the table is not evidence that its application,
account, plugin or runtime is available. Prefer installed tools and repository dependencies.
Use a local scripted/headless workflow when suitable. Verify current export support and APIs
from the selected tool's official docs before relying on them.

## 2. Choose authoring and delivery separately

Read [options.md](options.md) for tradeoffs and official documentation. Start here:

| Situation | Default route | Choose differently when |
|---|---|---|
| Character, articulated motion, sculpted form or complex page deformation | Blender authoring, GLB export, existing web renderer | A fixed rendered shot satisfies the UI without interaction |
| Data-driven chart, packets, procedural geometry or configurable assembly | Three.js in the existing renderer | Geometry or movement becomes hard to author and review in code |
| React application already using React Three Fiber | Keep React Three Fiber as the Three.js integration | The repository already has a direct Three.js player that works |
| Simple depth, card tilt or decorative extrusion | CSS/SVG | Real occlusion, geometry or camera movement is essential |
| Polished fixed camera illustration or animation | Blender to an image or video | Users need actual 3D interaction or runtime changes |
| A model viewer with limited custom behavior | Evaluate model-viewer | Existing player controls or complex scene logic make Three.js a better fit |
| Designer-owned visual editing and handoff | Evaluate Spline or PlayCanvas Editor | Account, export, runtime or ownership constraints prevent a portable result |
| Game-like scene with extensive interaction or physics | Evaluate the existing engine, Babylon.js or PlayCanvas | A smaller Three.js scene already meets the needs |

State the chosen authoring tool, delivery method, reason and one switching condition in a short
paragraph. Compare only credible alternatives for this task. Do not ask the user to select a
framework when their requirements already decide it. Do not migrate an engine merely to add a model.
For a recommendation or audit, lead with four explicit fields: **Route**, **First proof**,
**Fallback**, and **Release checks**. Keep proposed work separate from results actually rendered or
measured; never imply that an asset, browser path, or device budget passed when it was not run.

When Blender is selected, read [blender-authoring](../blender-authoring/SKILL.md). For any
loop, coordinated character action or continuous pan, read [animation.md](animation.md) before
implementation. It defines contact, timeline, loop-boundary and player checks. Keep tool selection
here; use the companion for Blender execution details.

## 3. Prove the hardest visual beat first

Create a small reviewable study in the intended camera. For a tennis return, prove foot placement,
weight transfer, racket contact and recovery before polishing clothing or court decorations.
For a book, prove the hinge and page silhouette before texturing it.

Inspect silhouettes and intermediate poses at the actual UI size. If they fail, change the pose,
geometry or timing and review again. A successful export or passing test does not pass this step.

Switch when the cause warrants it:

- Primitive limbs or hand-coded deformation limit pose quality: move asset authoring to Blender.
- A modeled animation must respond to live data: retain the modeled asset and move that behavior
  into the runtime. Do not regenerate a GLB for each data update.
- Real-time rendering adds cost with no useful interaction: compare a rendered image/video.
- The export loses required materials, constraints or motion: bake supported results, simplify,
  or choose rendered media. Do not promise arbitrary Blender scenes will export unchanged.

Before switching, record which source asset, public component interface, camera, timing,
controls and fallback must survive. Reuse the player and preserve the previous working version
until the replacement passes review. Tool changes must not silently change the requested design.

## 4. Build reusable assets and playback

Follow the host's component ownership rules. In a UI Pack workflow, author/register significant
visuals in UI Pack before the homepage consumes them. Keep source models or reproducible scripts,
exports, metadata and fallbacks with the owning library. Consumers supply content and theme.

For Blender:

- Use a separate output directory per asset; inspect any starter runner before executing it.
  Do not overwrite a previous design with a demo script.
- Retain an editable `.blend` or a complete reproducible generation script. Deliver a camera
  preview alongside the web export. Use deliberate scale, origins and named animation clips.
- Bake constraints/simulations only as supported by the target format. Check deformation,
  materials, transparency and lighting in the exported asset, not just Blender's render.
- Load the GLB in the actual runtime early. Keep network loading lazy and provide an explicit
  asset-load failure fallback. Dispose resources and handle unmounts during loading.

For code-authored scenes, separate geometry, motion and player controls. Use elapsed time,
not frame counts, for motion. Preserve pause, resume, replay, hidden-tab suspension and a stable
reduced-motion pose. Avoid introducing a second renderer for an expanded canvas.

For every route, record model/media provenance and redistribution rights. Set practical download,
geometry, texture and frame-time budgets from the target page and devices; measure the result.
Optimize only after checking what is expensive. For rendered media, provide a poster/static
alternative and verify alpha, codecs, looping and reduced motion in the target browsers. Decorative
motion that continues beyond five seconds also needs a visible pause/stop control; if the design
cannot support one, stop the animation within five seconds and leave the poster visible. Under
`prefers-reduced-motion`, do not autoplay or preload the moving asset.

## 5. Verify, revise, integrate

1. Inspect the actual exported/runtime result at desktop and narrow width, in applicable themes.
   Capture the action's key poses as well as the final frame. Check framing, contact, clipping,
   readable detail and motion continuity; check the loop seam if it loops.
2. Test the chosen route's failure states and controls. For WebGL: unavailable/lost context,
   model-load failure, pause/replay, reduced motion and cleanup. For media: load failure and
   static fallback. Include keyboard/touch access and the existing expanded-canvas behavior.
3. Measure cold-load size and runtime behavior on a representative mobile viewport/device.
   A desktop screenshot does not prove smooth mobile animation; say what was actually measured.
4. Run repository checks and verify the built library in its consumer. Returning to step 3 is
   required when the movement still looks wrong even if automated checks pass.
5. Report the chosen route, editable source, delivered output, visual evidence, checks and any
   remaining limitation. Keep implemented, proposed and published status distinct.

## Decision examples

| Avoid | Do |
|---|---|
| Build another capsule person because Three.js is already installed | Test the return silhouette; use a Blender rig when articulation is the weak point |
| Replace Three.js with Blender | Author in Blender and play the exported asset through the existing renderer |
| Add React Three Fiber to every React page | Keep the established scene/player unless its limitations justify a migration |
| Call a PNG or video an interactive 3D model | State the delivery type and provide the editable source separately |
| Choose an editor before checking export and ownership | Check the needed export, runtime, account and licensing conditions first |
| Claim quality because unit tests pass | Review the moving scene at UI size, then report tests separately |
