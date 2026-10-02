extends RefCounted
class_name ChordAudioBank
## Original procedural PCM for Gravity Birds v1.5 (Chord Audio).
## Samples live as base64 text under res://assets/audio/ — all synthesized for this game.

const MIX_RATE := 44100
const AUDIO_DIR := "res://assets/audio/"

static func _load_pcm(name: String) -> PackedByteArray:
	var path := AUDIO_DIR + name + ".pcm.b64"
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		push_error("ChordAudioBank: missing " + path)
		return PackedByteArray()
	return Marshalls.base64_to_raw(f.get_as_text().strip_edges())

static func _stream(name: String, loop: bool = false) -> AudioStreamWAV:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_16_BITS
	s.mix_rate = MIX_RATE
	s.stereo = false
	s.data = _load_pcm(name)
	if loop and s.data.size() > 0:
		s.loop_mode = AudioStreamWAV.LOOP_FORWARD
		s.loop_begin = 0
		s.loop_end = int(s.data.size() / 2)
	return s

static func move_settle() -> AudioStreamWAV:
	return _stream("move_settle")
static func fall_impact() -> AudioStreamWAV:
	return _stream("fall_impact")
static func fruit_collect() -> AudioStreamWAV:
	return _stream("fruit_collect")
static func grow() -> AudioStreamWAV:
	return _stream("grow")
static func exit_unlock() -> AudioStreamWAV:
	return _stream("exit_unlock")
static func death() -> AudioStreamWAV:
	return _stream("death")
static func undo_restore() -> AudioStreamWAV:
	return _stream("undo_restore")
static func win() -> AudioStreamWAV:
	return _stream("win")
static func ui_undo() -> AudioStreamWAV:
	return _stream("ui_undo")
static func ui_restart() -> AudioStreamWAV:
	return _stream("ui_restart")
static func music_bed() -> AudioStreamWAV:
	return _stream("music_bed", true)
