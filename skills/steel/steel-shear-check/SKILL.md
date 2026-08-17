---
name: steel-shear-check
description: Check web shear strength of unstiffened I/W-shape webs under AISC 360-16 Chapter G with Cv1 calculated from web slenderness.
---
# Steel Shear Check

## Scope
Unstiffened webs of I/W shapes. Computes `Cv1` rather than blocking immediately when `Cv1 < 1`.

## Guardrails
- Uses clear web depth `h` and web thickness `tw`.
- Current release uses `kv = 5.34` for unstiffened webs.
- Tension-field action and transverse-stiffener design remain out of scope.
