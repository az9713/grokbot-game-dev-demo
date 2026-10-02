extends Node2D
class_name PuzzleGame

# ============================================================================
# GRAVITY BIRDS - v1.5 Feel & Juice Hooks
# ============================================================================
# This script contains hookable juice events for VFX and audio.
# 
# Juice event order (as triggered during gameplay):
# 1. move_settled - After head moves and settles
# 2. fall_impact - When segments land after gravity
# 3. fruit_collected + creature_grew - When fruit eaten and body grows
# 4. exit_unlocked - When all fruit collected (exit becomes available)
# 5. death_triggered + undo_restored - On hazard death → auto-undo
# 6. win_triggered - When player enters unlocked exit
#
# Audio: AudioStreamPlayer nodes are stubbed in scene. Chord can assign streams.
# VFX: Signals can be connected to particle systems, tweens, shaders (Ari/Moss Ledger).
# ============================================================================

const TILE_SIZE = 64
const MOVE_DELAY = 0.15
const FALL_DELAY = 0.08

enum TileType { EMPTY = 0, SOLID = 1, VOID = 2, SPIKE = 3 }

const TEX_SOLID := preload("res://assets/art/tile_solid.png")
const TEX_EMPTY := preload("res://assets/art/tile_empty.png")
const TEX_VOID := preload("res://assets/art/tile_void.png")
const TEX_SPIKE := preload("res://assets/art/tile_spike.png")
const TEX_FRUIT := preload("res://assets/art/fruit.png")
const TEX_EXIT_LOCKED := preload("res://assets/art/exit_locked.png")
const TEX_EXIT_OPEN := preload("res://assets/art/exit_open.png")
const TEX_BIRD_HEAD := preload("res://assets/art/bird_head.png")
const TEX_BIRD_BODY := preload("res://assets/art/bird_body.png")
const TEX_BIRD_TAIL := preload("res://assets/art/bird_tail.png")

var level_data: LevelData
var creature_segments: Array[Vector2i] = []
var fruits_remaining: Array[Vector2i] = []
var exit_pos: Vector2i
var state_stack: Array[Dictionary] = []
var is_animating: bool = false
var is_won: bool = false
var is_dead: bool = false

@onready var camera = $Camera2D
@onready var hud = $HUD

# Audio stub nodes - Chord can fill these with actual audio later
@onready var sfx_move_settle = $AudioPlayers/SfxMoveSettle
@onready var sfx_fall_impact = $AudioPlayers/SfxFallImpact
@onready var sfx_fruit_collect = $AudioPlayers/SfxFruitCollect
@onready var sfx_grow = $AudioPlayers/SfxGrow
@onready var sfx_exit_unlock = $AudioPlayers/SfxExitUnlock
@onready var sfx_death = $AudioPlayers/SfxDeath
@onready var sfx_undo_restore = $AudioPlayers/SfxUndoRestore
@onready var sfx_win = $AudioPlayers/SfxWin
@onready var sfx_ui_undo = $AudioPlayers/SfxUiUndo
@onready var sfx_ui_restart = $AudioPlayers/SfxUiRestart
@onready var music_bed = $AudioPlayers/MusicBed

# Fall SFX debounce — multiple segments can emit fall_impact in one settle
var _fall_sfx_cooldown_until_ms: int = 0

# Juice/feedback signals - connect these to VFX and audio later
signal move_settled(head_pos: Vector2i, direction: Vector2i)
signal segment_fell(segment_index: int, from_pos: Vector2i, to_pos: Vector2i)
signal fall_impact(segment_index: int, landed_pos: Vector2i)
signal fruit_collected(fruit_pos: Vector2i, new_fruit_count: int)
signal creature_grew(new_segment_pos: Vector2i, total_length: int)
signal exit_unlocked(exit_pos: Vector2i)
signal death_triggered(death_pos: Vector2i, death_type: String)
signal undo_restored(restored_length: int)
signal win_triggered(exit_pos: Vector2i)
signal ui_undo_input
signal ui_restart_input

signal level_won
signal level_failed

func _ready():
	# Wire up juice/audio hooks
	move_settled.connect(_on_move_settled)
	fall_impact.connect(_on_fall_impact)
	fruit_collected.connect(_on_fruit_collected)
	creature_grew.connect(_on_creature_grew)
	exit_unlocked.connect(_on_exit_unlocked)
	death_triggered.connect(_on_death_triggered)
	undo_restored.connect(_on_undo_restored)
	win_triggered.connect(_on_win_triggered)
	ui_undo_input.connect(_on_ui_undo_input)
	ui_restart_input.connect(_on_ui_restart_input)
	_bind_chord_audio()

func _bind_chord_audio() -> void:
	# Chord v1.5: bind original procedural streams onto Vera's stub players
	if sfx_move_settle:
		sfx_move_settle.stream = ChordAudioBank.move_settle()
	if sfx_fall_impact:
		sfx_fall_impact.stream = ChordAudioBank.fall_impact()
	if sfx_fruit_collect:
		sfx_fruit_collect.stream = ChordAudioBank.fruit_collect()
	if sfx_grow:
		sfx_grow.stream = ChordAudioBank.grow()
	if sfx_exit_unlock:
		sfx_exit_unlock.stream = ChordAudioBank.exit_unlock()
	if sfx_death:
		sfx_death.stream = ChordAudioBank.death()
	if sfx_undo_restore:
		sfx_undo_restore.stream = ChordAudioBank.undo_restore()
	if sfx_win:
		sfx_win.stream = ChordAudioBank.win()
	if sfx_ui_undo:
		sfx_ui_undo.stream = ChordAudioBank.ui_undo()
	if sfx_ui_restart:
		sfx_ui_restart.stream = ChordAudioBank.ui_restart()
	if music_bed:
		music_bed.stream = ChordAudioBank.music_bed()

func load_level(level: LevelData):
	level_data = level
	creature_segments = level.creature_start.duplicate(true)
	fruits_remaining = level.fruits.duplicate(true)
	exit_pos = level.exit_pos
	state_stack.clear()
	is_won = false
	is_dead = false
	
	save_state()
	queue_redraw()
	
	if hud:
		hud.set_level_name(level.level_name)
		hud.update_fruit_count(fruits_remaining.size())
	if music_bed and music_bed.stream and not music_bed.playing:
		music_bed.play()

func _input(event):
	if is_animating or is_won or is_dead:
		return
	
	if event.is_action_pressed("ui_left"):
		attempt_move(Vector2i.LEFT)
	elif event.is_action_pressed("ui_right"):
		attempt_move(Vector2i.RIGHT)
	elif event.is_action_pressed("ui_up"):
		attempt_move(Vector2i.UP)
	elif event.is_action_pressed("ui_down"):
		attempt_move(Vector2i.DOWN)
	elif event.is_action_pressed("undo"):
		ui_undo_input.emit()  # Juice hook: undo key pressed
		undo_move()
	elif event.is_action_pressed("restart"):
		ui_restart_input.emit()  # Juice hook: restart key pressed
		restart_level()

func attempt_move(direction: Vector2i):
	if creature_segments.is_empty():
		return
	
	var head_pos = creature_segments[0]
	var new_head_pos = head_pos + direction
	
	# Check if reversing into neck
	if creature_segments.size() > 1 and new_head_pos == creature_segments[1]:
		return
	
	# Check if moving into solid wall
	var tile = level_data.get_tile(new_head_pos.x, new_head_pos.y)
	if tile == TileType.SOLID:
		return
	
	# Valid move - execute simulation
	is_animating = true
	execute_move(direction)

func execute_move(direction: Vector2i):
	# Simulation order: move → pushes → grow → gravity loop → hazards
	
	# 1. Move
	var head_pos = creature_segments[0]
	var new_head_pos = head_pos + direction
	
	var new_segments: Array[Vector2i] = [new_head_pos]
	for i in range(creature_segments.size() - 1):
		new_segments.append(creature_segments[i])
	creature_segments = new_segments
	
	# 2. Pushes (not implemented in v1)
	
	# 3. Grow (check if ate fruit)
	var ate_fruit = false
	var fruit_pos_collected: Vector2i
	for i in range(fruits_remaining.size()):
		if fruits_remaining[i] == new_head_pos:
			fruit_pos_collected = fruits_remaining[i]
			fruits_remaining.remove_at(i)
			ate_fruit = true
			if hud:
				hud.update_fruit_count(fruits_remaining.size())
			break
	
	if ate_fruit:
		# Add segment at old tail position after this step
		pass  # Will add after gravity
	
	queue_redraw()
	await get_tree().create_timer(MOVE_DELAY).timeout
	
	# JUICE HOOK 1: Move settled + head emphasis
	move_settled.emit(new_head_pos, direction)
	
	# 4. Gravity loop
	var gravity_steps = 0
	var max_gravity_steps = 20
	var segments_that_fell_this_move: Dictionary = {}  # Track unique segments that fell
	
	while gravity_steps < max_gravity_steps:
		var segments_that_fell_this_step = apply_gravity()
		if segments_that_fell_this_step.is_empty():
			break
		
		# Accumulate segments that fell (use dict for uniqueness)
		for seg_idx in segments_that_fell_this_step:
			segments_that_fell_this_move[seg_idx] = true
		
		queue_redraw()
		await get_tree().create_timer(FALL_DELAY).timeout
		gravity_steps += 1
	
	# JUICE HOOK 2: Fall impact (after gravity settles)
	# Emit impact signal for segments that actually fell and came to rest
	for seg_idx in segments_that_fell_this_move.keys():
		if seg_idx < creature_segments.size():
			fall_impact.emit(seg_idx, creature_segments[seg_idx])
	
	# JUICE HOOK 3: Fruit collected + grow reveal
	if ate_fruit:
		# Emit fruit collection signal
		fruit_collected.emit(fruit_pos_collected, fruits_remaining.size())
		
		# In a real implementation, track where tail should grow
		# For now, just duplicate last segment
		if creature_segments.size() > 0:
			var new_tail_pos = creature_segments[creature_segments.size() - 1]
			creature_segments.append(new_tail_pos)
			# Emit grow signal
			creature_grew.emit(new_tail_pos, creature_segments.size())
		
		# Check if exit should unlock (all fruit collected)
		if fruits_remaining.is_empty():
			# JUICE HOOK 4: Exit unlock beat
			exit_unlocked.emit(exit_pos)
	
	# 5. Hazards
	check_hazards()
	
	queue_redraw()
	
	if not is_dead:
		save_state()
		check_win_condition()
	
	is_animating = false

func apply_gravity() -> Array[int]:
	var segments_that_fell: Array[int] = []
	
	# Check each segment from tail to head
	for i in range(creature_segments.size() - 1, -1, -1):
		var seg = creature_segments[i]
		var below = seg + Vector2i.DOWN
		
		# Check if segment has support
		var has_support = false
		
		# Check if standing on solid tile
		var tile_below = level_data.get_tile(below.x, below.y)
		if tile_below == TileType.SOLID:
			has_support = true
		
		# Check if standing on another segment
		for j in range(creature_segments.size()):
			if i != j and creature_segments[j] == below:
				has_support = true
				break
		
		# If no support, fall
		if not has_support:
			var tile_at_below = level_data.get_tile(below.x, below.y)
			if tile_at_below != TileType.SOLID:
				var old_pos = creature_segments[i]
				creature_segments[i] = below
				segments_that_fell.append(i)
				# JUICE HOOK 2a: Individual segment fall event (for VFX trails)
				segment_fell.emit(i, old_pos, below)
	
	return segments_that_fell

func check_hazards():
	for seg in creature_segments:
		var tile = level_data.get_tile(seg.x, seg.y)
		if tile == TileType.VOID or tile == TileType.SPIKE:
			is_dead = true
			var death_type = "void" if tile == TileType.VOID else "spike"
			
			# JUICE HOOK 5: Death sting
			death_triggered.emit(seg, death_type)
			
			# Soft rewind: undo one step
			await get_tree().create_timer(0.3).timeout
			undo_move()
			is_dead = false
			return

func check_win_condition():
	# Win: all fruit eaten AND head at exit
	if fruits_remaining.is_empty():
		var head = creature_segments[0]
		if head == exit_pos:
			is_won = true
			
			# JUICE HOOK 6: Win flourish
			win_triggered.emit(exit_pos)
			
			level_won.emit()

func save_state():
	var state = {
		"creature": creature_segments.duplicate(true),
		"fruits": fruits_remaining.duplicate(true)
	}
	state_stack.append(state)

func undo_move():
	if state_stack.size() <= 1:
		return
	
	state_stack.pop_back()
	var prev_state = state_stack[state_stack.size() - 1]
	
	var restored_creature: Array = prev_state["creature"].duplicate(true)
	creature_segments.assign(restored_creature)
	var restored_fruits: Array = prev_state["fruits"].duplicate(true)
	fruits_remaining.assign(restored_fruits)
	
	if hud:
		hud.update_fruit_count(fruits_remaining.size())
	
	queue_redraw()
	
	# JUICE HOOK 5b: Undo restored (after death or manual undo)
	undo_restored.emit(creature_segments.size())

func restart_level():
	if state_stack.is_empty():
		return
	
	var initial_state = state_stack[0]
	state_stack.clear()
	state_stack.append(initial_state)
	
	var restored_creature: Array = initial_state["creature"].duplicate(true)
	creature_segments.assign(restored_creature)
	var restored_fruits: Array = initial_state["fruits"].duplicate(true)
	fruits_remaining.assign(restored_fruits)
	is_won = false
	is_dead = false
	
	if hud:
		hud.update_fruit_count(fruits_remaining.size())
	
	queue_redraw()

func _draw():
	if not level_data:
		return
	
	# Draw tiles
	for y in range(level_data.grid_height):
		for x in range(level_data.grid_width):
			var tile = level_data.get_tile(x, y)
			var pos = Vector2(x * TILE_SIZE, y * TILE_SIZE)
			
			match tile:
				TileType.SOLID:
					draw_texture(TEX_SOLID, pos)
				TileType.VOID:
					draw_texture(TEX_VOID, pos)
				TileType.SPIKE:
					draw_texture(TEX_SPIKE, pos)
				TileType.EMPTY:
					pass
	
	# Draw exit
	var exit_draw_pos = Vector2(exit_pos.x * TILE_SIZE, exit_pos.y * TILE_SIZE)
	var exit_tex = TEX_EXIT_OPEN if fruits_remaining.is_empty() else TEX_EXIT_LOCKED
	draw_texture(exit_tex, exit_draw_pos)
	
	# Draw fruits
	for fruit_pos in fruits_remaining:
		var draw_pos = Vector2(fruit_pos.x * TILE_SIZE, fruit_pos.y * TILE_SIZE)
		draw_texture(TEX_FRUIT, draw_pos)
	
	# Draw creature
	for i in range(creature_segments.size()):
		var seg = creature_segments[i]
		var draw_pos = Vector2(seg.x * TILE_SIZE, seg.y * TILE_SIZE)
		
		var is_head = (i == 0)
		var is_tail = (i == creature_segments.size() - 1)
		
		var texture: Texture2D
		if is_head:
			texture = TEX_BIRD_HEAD
		elif is_tail and creature_segments.size() > 1:
			texture = TEX_BIRD_TAIL
		else:
			texture = TEX_BIRD_BODY
		
		# Determine facing direction (check if moving left)
		var flip_h = false
		if is_head and creature_segments.size() > 1:
			var neck_pos = creature_segments[1]
			if seg.x < neck_pos.x:
				flip_h = true
		
		if flip_h:
			draw_set_transform(draw_pos + Vector2(TILE_SIZE, 0), 0, Vector2(-1, 1))
			draw_texture(texture, Vector2.ZERO)
			draw_set_transform(Vector2.ZERO, 0, Vector2.ONE)
		else:
			draw_texture(texture, draw_pos)

# ============================================================================
# JUICE/FEEL CALLBACKS
# These functions are called when juice events fire.
# VFX artists (Ari) and audio designer (Chord) can hook into these.
# ============================================================================

func _on_move_settled(head_pos: Vector2i, direction: Vector2i):
	# JUICE 1: Move settle + head emphasis
	# TODO VFX: head squash/stretch, dust puff, directional emphasis
	# TODO Audio: movement sound (varies by surface?)
	if sfx_move_settle and sfx_move_settle.stream:
		sfx_move_settle.play()

func _on_fall_impact(segment_index: int, landed_pos: Vector2i):
	# JUICE 2: Fall impact
	# TODO VFX: impact rings, dust, screen shake (proportional to fall distance)
	# Audio: debounced thud so multi-segment landings don't stack into noise
	var now := Time.get_ticks_msec()
	if now < _fall_sfx_cooldown_until_ms:
		return
	_fall_sfx_cooldown_until_ms = now + 50
	if sfx_fall_impact and sfx_fall_impact.stream:
		sfx_fall_impact.play()

func _on_fruit_collected(fruit_pos: Vector2i, new_fruit_count: int):
	# JUICE 3a: Fruit pop
	# TODO VFX: fruit burst, sparkles, juice splash
	# TODO Audio: satisfying pop/crunch
	if sfx_fruit_collect and sfx_fruit_collect.stream:
		sfx_fruit_collect.play()

func _on_creature_grew(new_segment_pos: Vector2i, total_length: int):
	# JUICE 3b: Grow reveal
	# TODO VFX: segment pop-in, scale bounce, glow pulse
	# TODO Audio: growth sound (pitch up with length?)
	if sfx_grow and sfx_grow.stream:
		sfx_grow.play()

func _on_exit_unlocked(exit_position: Vector2i):
	# JUICE 4: Exit unlock beat
	# TODO VFX: lock shatter/fade, exit glow/pulse, rays, particle burst
	# TODO Camera: slight zoom to exit, then back
	# TODO Audio: unlock chime, door creak
	if sfx_exit_unlock and sfx_exit_unlock.stream:
		sfx_exit_unlock.play()

func _on_death_triggered(death_pos: Vector2i, death_type: String):
	# JUICE 5a: Death sting
	# TODO VFX: flash red, death particle (spikes vs void different?), fade out
	# TODO Camera: shake, zoom to death point
	# TODO Audio: death sound (spike stab vs void fall)
	if sfx_death and sfx_death.stream:
		sfx_death.play()

func _on_undo_restored(restored_length: int):
	# JUICE 5b: Undo restore
	# TODO VFX: rewind particle trail, ghost fade-in, time-reverse effect
	# TODO Camera: brief zoom out
	# TODO Audio: reverse whoosh, restore chime
	if sfx_undo_restore and sfx_undo_restore.stream:
		sfx_undo_restore.play()

func _on_win_triggered(exit_position: Vector2i):
	# JUICE 6: Win flourish
	# TODO VFX: fireworks, confetti, creature celebration animation, exit glow intensifies
	# TODO Camera: zoom to exit, victory pose
	# Audio: short warm triad (readable, not carnival)
	if sfx_win and sfx_win.stream:
		sfx_win.play()

func _on_ui_undo_input():
	# UI feedback for undo key press (Z)
	# TODO Audio: UI button sound
	if sfx_ui_undo and sfx_ui_undo.stream:
		sfx_ui_undo.play()

func _on_ui_restart_input():
	# UI feedback for restart key press (R)
	# TODO Audio: UI button sound (slightly different from undo?)
	if sfx_ui_restart and sfx_ui_restart.stream:
		sfx_ui_restart.play()
