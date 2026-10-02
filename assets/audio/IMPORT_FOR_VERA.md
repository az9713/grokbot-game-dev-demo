# Chord audio pack — import into Gravity Birds

GitHub write is blocked on Chord’s token (same class of issue as Ari). Please land this on a PR from main.

## Drop-in paths
- `assets/audio/*.pcm.b64` → `res://assets/audio/`
- `scripts/chord_audio_bank.gd` → `res://scripts/`
- `scripts/puzzle_game.gd` → replace (binds streams + fall debounce + music start)
- `scenes/puzzle_game.tscn` → replace (buses, volumes, MusicBed node)
- `default_bus_layout.tres` → repo root
- `project.godot` → merge `[audio] buses/default_bus_layout=...` if you prefer not to overwrite whole file

See `AUDIO_NOTES.md` for event map and mix notes.
