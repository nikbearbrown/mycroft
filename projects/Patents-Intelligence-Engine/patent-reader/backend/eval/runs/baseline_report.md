# Classifier eval — run `baseline`

Scored claims: **50**  ·  errors: 0  ·  not yet run: 0

## Headline

| Dimension | Accuracy | Cohen's κ | Majority baseline |
|---|---|---|---|
| breadth | 0.66 | 0.08 | 0.92 (always 'narrow') |
| posture | 0.60 | 0.00 | 1.00 (always 'defensive') |
| joint | 0.56 | | |

## Collapse check

No single label exceeds 80% of predictions while beating its gold share by 20%+.

| Breadth/posture pair | Gold | Predicted |
|---|---|---|
| broad/defensive | 4 | 0 |
| broad/exploratory | 0 | 3 |
| broad/offensive | 0 | 11 |
| narrow/defensive | 46 | 30 |
| narrow/exploratory | 0 | 2 |
| narrow/offensive | 0 | 1 |
| unclear/unclear | 0 | 3 |

## Breadth confusion (rows = gold, cols = predicted)

| gold \ pred | broad | narrow | unclear | recall |
|---|---|---|---|---|
| broad | 2 | 2 | 0 | 0.50 |
| narrow | 12 | 31 | 3 | 0.67 |
| precision | 0.14 | 0.94 |  | |

## Posture confusion (rows = gold, cols = predicted)

| gold \ pred | defensive | offensive | exploratory | unclear | recall |
|---|---|---|---|---|---|
| defensive | 30 | 12 | 5 | 3 | 0.60 |
| offensive | 0 | 0 | 0 | 0 | n/a |
| exploratory | 0 | 0 | 0 | 0 | n/a |
| precision | 1.00 | 0.00 | 0.00 |  | |

## Per patent

| Patent | n | breadth acc | posture acc |
|---|---|---|---|
| US-11000086-B2 | 3 | 1.00 | 1.00 |
| US-11083299-B2 | 3 | 0.67 | 0.33 |
| US-11162350-B2 | 3 | 0.67 | 1.00 |
| US-11229793-B2 | 3 | 0.33 | 0.00 |
| US-11230805-B2 | 3 | 0.00 | 0.00 |
| US-11402190-B2 | 4 | 1.00 | 1.00 |
| US-11481487-B2 | 3 | 0.67 | 0.67 |
| US-11545757-B2 | 4 | 0.75 | 0.50 |
| US-11578034-B2 | 3 | 0.67 | 1.00 |
| US-11674378-B2 | 3 | 1.00 | 0.67 |
| US-11725734-B2 | 3 | 0.33 | 0.00 |
| US-11766760-B2 | 3 | 0.00 | 0.00 |
| US-11776821-B2 | 3 | 0.33 | 0.33 |
| US-11908061-B2 | 3 | 1.00 | 1.00 |
| US-11910707-B2 | 3 | 1.00 | 1.00 |
| US-11981154-B2 | 3 | 1.00 | 1.00 |

## Disagreements (22)

- **US-11229793-B2#1** — gold `narrow/defensive`, predicted `narrow/offensive`
  - model: The claim is limited to a specific pulse width range (10-333 microseconds) and the functional requirement of no paresthesia, but these numerical bounds are still wide enough to cover many sub-perception SCS implementations, suggesting an attempt to capture a broad swath of competitor designs within that paresthesia-free space.
  - labeler: specific pulse width range + no paresthesia constraint = narrow; established product category
- **US-11229793-B2#27** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim uses a wide numerical pulse width range (10-333 microseconds) and only two functional limitations (bi-phasic, no paresthesia) without specifying electrode configuration, amplitude, frequency, or waveform shape details, allowing it to cover many implementations achieving paresthesia-free spinal cord stimulation.
  - labeler: same constraint set as claim 1, near-duplicate
- **US-11229793-B2#30** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim recites only a generic method step (programming a signal generator) plus a wide numerical pulse-width range (10-333 microseconds) and a functional outcome (no paresthesia), without specifying waveform shape, amplitude, frequency, electrode configuration, or device structure, so it likely reads on many competing sub-perception SCS implementations.
  - labeler: same constraint set as claim 1, near-duplicate
- **US-11766760-B2#1** — gold `narrow/defensive`, predicted `unclear/unclear`
  - labeler: near-duplicate claims, same mechanical grinding method with minor variations; posture: this is protecting a specific mechanical grinding process, not blocking a whole space
- **US-11766760-B2#5** — gold `narrow/defensive`, predicted `unclear/unclear`
  - labeler: near-duplicate claims, same mechanical grinding method with minor variations; posture: this is protecting a specific mechanical grinding process, not blocking a whole space
- **US-11766760-B2#7** — gold `narrow/defensive`, predicted `unclear/unclear`
  - labeler: near-duplicate claims, same mechanical grinding method with minor variations; posture: this is protecting a specific mechanical grinding process, not blocking a whole space
- **US-11674378-B2#14** — gold `broad/defensive`, predicted `broad/exploratory`
  - model: The claim recites functional steps (calculating range, obtaining a 3D field, calculating a 3D gradient, correcting range) without specifying sensor types, calculation algorithms, or numerical thresholds, leaving many implementation paths open while combining several novel elements (3D field + gradient correction) that suggest the applicant is probing claim scope rather than locking in a specific build or clearly blocking competitors.
  - labeler: short abstract claim, no specific hardware, covers the general 3D ranging concept
- **US-11481487-B2#1** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim uses generic functional language (outputting file states, determining layer storage, comparing objects, detecting a threat, taking an action) without specifying particular algorithms, data structures, or comparison techniques, making it applicable to many multi-layer file system implementations like container overlay filesystems.
  - labeler: specific container/multi-layer file system threat detection method; protecting existing security product
- **US-11545757-B2#1** — gold `narrow/defensive`, predicted `broad/exploratory`
  - model: The claim recites a functional architecture (PEC reflector feeding one end, PMC reflector feeding opposite end with anti-phase signal) without specifying materials, dimensions, frequency ranges, or structural details of the leaky wave structure itself, making it broad; the dual-reflector anti-phase feeding combination is a distinctive conceptual approach that reads as the applicant staking out a new design space rather than clearly defending a specific build or aggressively blocking known alternatives.
  - labeler: specific reflector types and configurations
- **US-11545757-B2#30** — gold `broad/defensive`, predicted `broad/offensive`
  - model: The claim uses functional language (leaky wave structure, feeding system directing signals in anti-phase) without specifying materials, dimensions, or exact geometry, and the planar lithographic layer limitation is a relatively generic fabrication constraint that still covers many design variants, suggesting an attempt to cover a broad class of implementations.
  - labeler: simpler claim, fewer constraints, covers general dual end-fed planar antenna concept
- **US-11083299-B2#1** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim uses functional language (e.g., 'configured to operatively connect', 'rotatably driven adjustment system') and avoids specifying exact mechanisms, numbers of components beyond 'at least two', or precise geometric arrangements, allowing it to cover many possible implementations of seat tilt mechanisms via length-adjustable support members.
  - labeler: specific mechanical chair components with named parts; protecting existing ergonomic chair product
- **US-11083299-B2#7** — gold `narrow/defensive`, predicted `narrow/exploratory`
  - model: While the claim avoids numerical specifics on components, it layers multiple interdependent functional limitations (flexible movement support members, an actuator, a drive system with rotatable adjustment, rotation about specific perpendicular axes) that collectively narrow the scope to a particular mechanical approach, while the chained functional language suggests the applicant is probing claim boundaries rather than committing to a clearly offensive or defensive stance.
  - labeler: specific mechanical chair components with named parts; protecting existing ergonomic chair product
- **US-11578034-B2#11** — gold `broad/defensive`, predicted `narrow/defensive`
  - model: The claim specifies particular equipment (solid loading conveyor, specific reaction mixture components, solids removal filtration facility, storage tank) and a defined sequence of process steps, which narrows scope to a specific implementation rather than covering the general chemistry of glycerol carbonate synthesis from urea and glycerol.
  - labeler: general reactor setup description, no specific chemical parameters
- **US-11230805-B2#1** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim recites generic steps (acquiring location data, determining treatment chamber data, outputting it) and defines the sensor only by a broad list of alternative parameter types it could detect, without specifying particular sensor hardware, algorithms, or thresholds, making it hard to design around and likely intended to cover many competitor implementations.
  - labeler: IoT appliance positioning method; specific sensor type list; protecting existing smart home product
- **US-11230805-B2#9** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim covers any device (dosing or physical treatment) in any household appliance with liquid/gas, using any sensor from a broad listed set of modalities, without specifying thresholds, algorithms, or precise placement logic, so it reads on many possible implementations and sensor choices.
  - labeler: IoT appliance positioning method; specific sensor type list; protecting existing smart home product
- **US-11230805-B2#10** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim recites generic functional steps (acquiring location data, determining treatment chamber data, outputting it) tied only to signal strength from wireless networks, without specifying particular hardware, algorithms, or network types, so it could cover many implementations of detecting device placement via wireless signal strength.
  - labeler: IoT appliance positioning method; specific sensor type list; protecting existing smart home product
- **US-11162350-B2#15** — gold `broad/defensive`, predicted `narrow/defensive`
  - model: The claim ties the method to a specific structural component (a strain puck with a strain gauge and an edge engaged by a puck wedge interface for removable coupling), which limits the scope to implementations using this particular mounting/sensing mechanism rather than any downhole force-sensing approach.
  - labeler: abstract method claim, no specific hardware, covers general real-time drilling optimization
- **US-11725734-B2#1** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim relies on functional/structural language (asymmetry and/or varying radial distance causing varying contact pressure) rather than specific dimensions, materials, or geometric values, allowing it to cover many physical implementations that achieve variable sealing-lip pressure around the perimeter.
  - labeler: specific mechanical seal geometry with asymmetric support member; varying contact pressure; protecting existing rotating equipment seal product
- **US-11725734-B2#15** — gold `narrow/defensive`, predicted `broad/exploratory`
  - model: The claim recites a general seal assembly structure (support member plus sealing member with a lip) and relies on a functional, non-numerical limitation—'inner edge extending asymmetrically' causing contact pressure to 'vary about a circular perimeter'—without specifying any particular shape, degree of asymmetry, or material, leaving wide latitude for alternative implementations while testing whether this functional asymmetry concept is allowable.
  - labeler: specific mechanical seal geometry with asymmetric support member; varying contact pressure; protecting existing rotating equipment seal product
- **US-11725734-B2#18** — gold `narrow/defensive`, predicted `narrow/exploratory`
  - model: The claim adds a specific structural feature—a support member inner edge with varying radial distance from the centerline causing variable sealing lip contact pressure—which narrows scope beyond a generic seal assembly, but this unconventional non-circular/non-uniform geometry suggests the applicant is testing a novel design concept rather than clearly blocking competitors or protecting a fixed known product.
  - labeler: specific mechanical seal geometry with asymmetric support member; varying contact pressure; protecting existing rotating equipment seal product
- **US-11776821-B2#1** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim recites only generic structural elements (a substrate protrusion, two dice, an encapsulant with relative width/spacing and coverage relationships) without specifying materials, dimensions, process steps, or electrical interconnections, making it applicable to many package designs that use a standoff/protrusion feature between adjacent dies.
  - labeler: specific semiconductor packaging geometry with substrate protrusion; protecting existing advanced chip packaging product
- **US-11776821-B2#9** — gold `narrow/defensive`, predicted `broad/offensive`
  - model: The claim uses functional, generic language (a 'protrusion' with sidewalls and a width, without specifying material, shape, process parameters, or exact structural relationships) to cover a general underfill-flow technique guided by a substrate protrusion, which could read on many die-packaging implementations with similar flow-guiding features.
  - labeler: specific semiconductor packaging geometry with substrate protrusion; protecting existing advanced chip packaging product
