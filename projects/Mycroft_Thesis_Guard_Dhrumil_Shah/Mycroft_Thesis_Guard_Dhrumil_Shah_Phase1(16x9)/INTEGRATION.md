# Remotion integration contract

The supplied workspace already includes the required registration in
`runtime/remotion/src/Root.tsx`. If this video folder is copied into a fresh
compatible Brutalist.art workspace, add the following import and composition
to that file before running `scripts/sync-to-remotion.ps1`.

```tsx
import {
  MycroftThesisGuardBrief,
  MYCROFT_BRIEF_TOTAL_FRAMES,
} from './mycroft-brief/MycroftThesisGuardBrief';
```

```tsx
<Folder name="Mycroft-ThesisGuard-Brief">
  <Composition
    id="MycroftThesisGuardBrief"
    component={MycroftThesisGuardBrief}
    durationInFrames={MYCROFT_BRIEF_TOTAL_FRAMES}
    fps={24}
    width={3840}
    height={2160}
  />
</Folder>
```

The `scripts/sync-to-remotion.ps1` script validates that this registration is
present before rendering. That protects a clean clone from silently attempting
to render the wrong composition.

