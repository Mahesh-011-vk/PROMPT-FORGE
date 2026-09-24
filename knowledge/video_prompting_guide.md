# Video Prompting Architecture: Temporal Continuity & Motion

## 1. Temporal Deconstruction
Temporal diffusion models require continuous movement descriptions:
- State the initial frame setting clearly.
- Describe the directional trajectory: "A camera tracking forward as the car accelerates into a bend".

## 2. Motion Speed and Frame Rate
- Specify motion pacing: smooth slow-motion 60fps, naturalistic 24fps film cadence, or high-speed hyperlapse.
- Avoid erratic multiple camera cuts within a single prompt; specify continuous takes.

## 3. Negative Temporal Constraints
- Explicitly exclude temporal anomalies: flickering, morphing limbs, sudden jitter, geometric warping.
