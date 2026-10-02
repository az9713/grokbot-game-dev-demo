# Gravity Birds — Art Brief (**Moss Ledger**)

**Scope lock:** polish visuals/UI only. Same rules, same 5 levels. Original art — no ripped sprites, no Snakebird names/levels/shapes.

**Style name:** **Moss Ledger** — cozy painted puzzle tiles. Soft edge shading, light texture grain, rounded soft corners (not perfect cubes). Chubby readable silhouettes at 64px. **Not** flat vectors, cyber neon, or any copyrighted puzzle-bird look.

**Grid:** `TILE_SIZE = 64`. Keep existing `TileType` enum: `EMPTY=0`, `SOLID=1`, `VOID=2`, `SPIKE=3`. Fruit, exit (locked/unlocked), and bird head/body/tail are separate sprites, not TileType values.

---

## Palette (named hex)

| Name | Hex | Use |
|------|-----|-----|
| Sky parchment | `#E8DFC8` | ClearColor / sky wash |
| Fog green | `#C5D4B8` | Soft mid-ground mist, empty filler tint |
| Moss solid | `#5F7A4A` | Solid tile body |
| Moss highlight | `#7A9A5E` | Tile top light |
| Moss shadow | `#3E5232` | Tile bottom / rims |
| Bird body | `#4A8FA8` | Head / segments / tail |
| Bird belly | `#D9E8EE` | Underside soft |
| Beak | `#E0A04A` | Head beak (faces **right**) |
| Eye | `#1A1A1A` | Pupil |
| Fruit | `#E07A2A` | Collectible |
| Leaf | `#5F7A4A` | Fruit leaf |
| Exit locked | `#8A8A7A` | Locked portal + padlock cue |
| Exit open | `#6FBF6A` | Unlocked portal + soft glow |
| Spike iron | `#6B3A3A` | Spike base |
| Spike tip | `#C45A4A` | Tip gleam |
| Void | `#2A2E38` | Abyss tiles (faint stars OK) |
| UI plaque | `#F3EAD6` | Button / panel fill |
| UI border | `#6B5A3E` | Warm wood/felt edge |
| UI text | `#2C2418` | Labels |

---

## Tile language

| Asset | Role |
|-------|------|
| `tile_solid.png` | Walkable / support ground. Rounded moss block, top highlight, bottom shadow, speckled grain. |
| `tile_empty.png` | Optional subtle parchment/fog filler with tiny grass tufts. **May be skipped in draw** (leave transparent air); documented for Devin if a soft grid wash is wanted. |
| `tile_void.png` | Soft deadly abyss — dark `#2A2E38`, vignette, faint stars, still readable as a tile. |
| `tile_spike.png` | Three iron spikes pointing up from a base; tip `#C45A4A`. Transparent outside silhouette. |

---

## Actors / props

| Asset | Notes |
|-------|------|
| `bird_head.png` | Chubby head facing **right**; beak + one clear eye. Flip with `flip_h` for left. |
| `bird_body.png` | Round segment with belly; chains read as one creature. |
| `bird_tail.png` | Preferred end segment; feathers taper left (behind when facing right). |
| `fruit.png` | Orange orb + leaf; collectible. |
| `exit_locked.png` | Gray stone arch + padlock. |
| `exit_open.png` | Green arch + soft glow core. |
| `fruit_icon.png` | 28×28 HUD counter icon. |
| `ui_button.png` | 96×48 soft plaque; 9-slice friendly (corner radius ~12). |
| `ui_panel.png` | 256×48 top HUD bar panel. |
| `atlas.png` + `atlas.json` | Optional sheet of 64×64 gameplay tiles (see JSON `frames`). |

All gameplay tiles/actors are **64×64** PNG with transparency where needed. UI sizes as above. Godot may import at native size; downsample only if you author 128×128 later.

---

## Background / sky

- Set puzzle `ClearColor` / ColorRect backdrop to **Sky parchment `#E8DFC8`**, optionally blend toward **Fog green `#C5D4B8`** at the bottom for a soft horizon wash.
- Do not draw a busy parallax; keep focus on the 64px grid.

---

## HUD / menu direction

Warm wooden/felt plaques — **not** gray engine-debug buttons.

- Top: level title (left), fruit count + `fruit_icon` (right), on `ui_panel`.
- Bottom or corners: **Undo**, **Restart**, **Menu** using `ui_button` as TextureButton / NinePatchRect; text `#2C2418`.
- See `HUD_MOCK.md` for layout.

---

## Godot wiring notes (for Devin — do not change rules)

**Keep** `TileType` enum and simulation logic. Only replace procedural `_draw` shapes with textures.

Suggested approach in `puzzle_game.gd` `_draw()` (or child `Sprite2D` / `TextureRect` grid):

```gdscript
# Suggested preloads (example names — adjust to your Autoload/resource layout)
const TEX_SOLID := preload("res://assets/art/tile_solid.png")
const TEX_EMPTY := preload("res://assets/art/tile_empty.png")  # optional
const TEX_VOID := preload("res://assets/art/tile_void.png")
const TEX_SPIKE := preload("res://assets/art/tile_spike.png")
const TEX_FRUIT := preload("res://assets/art/fruit.png")
const TEX_EXIT_L := preload("res://assets/art/exit_locked.png")
const TEX_EXIT_O := preload("res://assets/art/exit_open.png")
const TEX_HEAD := preload("res://assets/art/bird_head.png")
const TEX_BODY := preload("res://assets/art/bird_body.png")
const TEX_TAIL := preload("res://assets/art/bird_tail.png")

# In _draw, for each cell:
#   draw_texture(TEX_SOLID, Vector2(x, y) * TILE_SIZE)
# Head: draw_texture(TEX_HEAD, pos); use draw_set_transform / flip if moving left
# Body mid segments: TEX_BODY; last segment: TEX_TAIL if len > 1
# Exit: TEX_EXIT_O if all fruit collected else TEX_EXIT_L
```

Suggested HUD node names:

- `HudRoot` → `TopBar` (`NinePatchRect` / `TextureRect` ← `ui_panel.png`)
  - `LevelTitle` (`Label`)
  - `FruitCounter` (`HBox`: `FruitIcon` TextureRect ← `fruit_icon.png`, `FruitLabel`)
- `ButtonBar` → `BtnUndo`, `BtnRestart`, `BtnMenu` (`TextureButton` ← `ui_button.png`, 9-slice margins ~12)

Import settings: Filter **on** (soft painted), Mipmaps optional; 2D pixel snap **off** (not crisp pixel art).

**Out of scope for this art drop:** changing gravity, fruit growth, undo stack, level `.tres` data, or TileType values.

---

## Regeneration

Sprites were authored with a deterministic Python/Pillow paint script (soft blobs + grain). Re-run only if intentionally revising the look; keep filenames stable for Devin’s paths.

---

## v1.5 delta — Moss Ledger visual elevation (Ari Art)

**Date:** 2026-09-18 (PT)  
**Goal:** Richer soft-painted tiles/actors + VFX frames for Vera Play juice hooks. Same filenames / 64px gameplay grid so Godot preloads stay valid. Original Moss Ledger only (no Snakebird/IP copies). Silhouette/readability over decoration.

### Regenerated gameplay / UI sprites (Pillow soft blobs + grain)

| File | Size | Notes |
|------|------|-------|
| `assets/art/tile_solid.png` | 64×64 | Moss block, top highlight, bottom shadow, lichen grain |
| `assets/art/tile_empty.png` | 64×64 | Soft parchment/fog wash + tiny grass tufts |
| `assets/art/tile_void.png` | 64×64 | Abyss vignette + faint stars |
| `assets/art/tile_spike.png` | 64×64 | Three iron spikes up; tip gleam `#C45A4A` |
| `assets/art/bird_head.png` | 64×64 | Chubby head faces **RIGHT**; beak + eye |
| `assets/art/bird_body.png` | 64×64 | Round segment + belly |
| `assets/art/bird_tail.png` | 64×64 | Feathers taper left |
| `assets/art/fruit.png` | 64×64 | Orange orb + leaf |
| `assets/art/exit_locked.png` | 64×64 | Gray stone arch + padlock |
| `assets/art/exit_open.png` | 64×64 | Green arch + soft glow core |
| `assets/art/ui_panel.png` | 256×48 | Warm plaque HUD bar |
| `assets/art/ui_button.png` | 96×48 | 9-slice friendly (~12 radius) |
| `assets/art/fruit_icon.png` | 28×28 | HUD counter icon |
| `assets/art/atlas.png` | 320×128 | Sheet rebuilt to match `atlas.json` frames |
| `assets/art/atlas.json` | — | Unchanged frame layout (tile_size 64) |

### New VFX frames (`assets/art/vfx/`) — Vera Play juice hooks

| VFX file | Hook / event | Intent |
|----------|--------------|--------|
| `vfx_move_dust.png` | `move_settled` | Soft dust puff at feet when a move settles |
| `vfx_fall_dust.png` | `fall_impact` | Ground impact dust on fall land |
| `vfx_fruit_burst.png` | `fruit_collected` | Orange burst shards (readable, short) |
| `vfx_grow_glow.png` | `creature_grew` | Soft cyan/blue grow ring around body |
| `vfx_exit_unlock.png` | `exit_unlocked` | Green unlock sparkles + soft glow |
| `vfx_death_spike.png` | `death_triggered` (spike) | Red iron flash shards |
| `vfx_death_void.png` | `death_triggered` (void) | Dark swirl sink |
| `vfx_undo_ghost.png` | `undo_restored` | Translucent bird ghost silhouette |
| `vfx_win_flourish.png` | `win_triggered` | Soft glow rays only — **no confetti spam** |

All VFX are 64×64 RGBA PNG with transparency. Keep playback short and silhouette-clear at gameplay scale.

### Out of scope (unchanged)

Rules, gravity, fruit growth logic, undo stack, level `.tres` data, `TileType` enum values.
