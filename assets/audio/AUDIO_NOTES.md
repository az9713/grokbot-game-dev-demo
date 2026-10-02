# Gravity Birds v1.5 — Audio notes (Chord)

## Before / after
- **Before:** No `assets/audio`, no streams on juice `AudioStreamPlayer` stubs (silent).
- **After:** Original procedural one-shots bound to Vera’s juice hooks + quiet looping music bed.

## License
All samples synthesized for Gravity Birds (procedural PCM). No third-party or commercial-game audio.

## Event → file map
| Juice / UI | Player | Asset |
|---|---|---|
| move_settled | SfxMoveSettle | `move_settle.pcm.b64` |
| fall_impact | SfxFallImpact | `fall_impact.pcm.b64` |
| fruit_collected | SfxFruitCollect | `fruit_collect.pcm.b64` |
| creature_grew | SfxGrow | `grow.pcm.b64` |
| exit_unlocked | SfxExitUnlock | `exit_unlock.pcm.b64` |
| death_triggered | SfxDeath | `death.pcm.b64` |
| undo_restored | SfxUndoRestore | `undo_restore.pcm.b64` |
| win_triggered | SfxWin | `win.pcm.b64` |
| Z undo | SfxUiUndo | `ui_undo.pcm.b64` |
| R restart | SfxUiRestart | `ui_restart.pcm.b64` |
| (loop) | MusicBed | `music_bed.pcm.b64` |

PCM is 16-bit mono 44.1 kHz, loaded at runtime by `ChordAudioBank` (`scripts/chord_audio_bank.gd`).

## Mix / buses
- Buses: Master → `Music`, `SFX`, `UI` (`default_bus_layout.tres`)
- Music ~ −18 dB, loops, starts with level load
- SFX on `SFX` bus; UI ticks on `UI`
- **Fall stack:** `fall_impact` may fire per segment — playback is debounced (~50 ms) so landings juice without noise spam
- Win: warm triad, short — readable, not carnival (Gage)

## Wiring
`PuzzleGame._ready` calls `_bind_chord_audio()` to assign streams from `ChordAudioBank` onto the existing stub players (plus `MusicBed`).
