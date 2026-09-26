# 3D workflow options

These are candidates, not an installed-tool inventory. Verify availability, current compatibility,
license and export requirements for the task. Prefer the existing stack when it meets the design.

| Option | Role and good fit | Main tradeoff / check |
|---|---|---|
| Blender | Editable modeling, rigging, animation, procedural authoring, lighting and offline rendering | Browser delivery requires export or rendered media; test material and animation compatibility |
| Three.js | Custom real-time web scenes, procedural objects, data-driven motion and imported models | The application owns lifecycle, interaction, accessibility and performance |
| React Three Fiber | React integration for Three.js scenes | It is a renderer integration, not a modeling tool; adding it to an established direct player has migration cost |
| Babylon.js | Web engine for substantial scenes and interactive applications | Compare required engine features against bundle size and migration cost before replacing a working engine |
| PlayCanvas | Web engine and optional visual editor for interactive scenes | Verify asset pipeline, editor/account needs and self-hosting/export requirements |
| Spline | Visual authoring for designer-led interactive web compositions | Check current export choices, plan restrictions, runtime dependencies and source handoff |
| model-viewer | Declarative viewing of a model with standard viewer behavior | Prototype whether its controls and loading behavior fit the host; custom choreography may need the existing renderer |
| CSS transforms / SVG | Lightweight depth illusion, cards, icons and simple illustrative motion | No general modeled scene, skeletal animation or physically meaningful 3D interaction |
| Blender-rendered still / video | Fixed camera visuals where final lighting and low runtime cost matter | No true object manipulation; compare transfer size, browser playback, transparency and static fallback |
| CAD authoring, e.g. OpenSCAD | Dimension-driven hard-surface parts or parametric product forms | Poor default for organic characters; tessellation and materials need review for web delivery |

A mixed route is often appropriate: Blender builds the player and racket, a web renderer plays the
clip, and HTML supplies accessible labels and controls. Trading data can remain runtime-generated
beside an imported frame. Choose each layer for its job without duplicating scene ownership.

## Primary documentation

Consult only what the selected route needs. Recheck exact APIs and export limitations at use time.

- Blender glTF: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
- Blender command line: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html
- Three.js: https://threejs.org/docs/ (GLTFLoader, AnimationMixer, WebGLRenderer)
- React Three Fiber: https://r3f.docs.pmnd.rs/getting-started/introduction
- Babylon.js: https://doc.babylonjs.com/
- PlayCanvas: https://developer.playcanvas.com/user-manual/
- Spline: https://docs.spline.design/
- model-viewer: https://modelviewer.dev/
- CSS transforms: https://developer.mozilla.org/en-US/docs/Web/CSS/transform-style
- OpenSCAD: https://openscad.org/documentation.html
