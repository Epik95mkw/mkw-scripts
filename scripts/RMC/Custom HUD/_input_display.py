from dolphin import event, gui, memory # type: ignore
from Modules import mkw_classes as mkw, mkw_utils
from Modules.custom_hud import *

SCALE = 12

def draw_LR_button(x, y, filled):
    width = 8 * SCALE
    height = 2 * SCALE
    border_radius = 4
    gap = 4
    gui.draw_rect((x, y), (x + width, y + height), color=WHITE, thickness=2, rounding=border_radius)
    if filled:
        gui.draw_rect_filled((x + gap, y + gap), (x + width - gap, y + height - gap), color=WHITE, rounding=border_radius)

def draw_A_button(x, y, filled):
    radius = 2.5 * SCALE
    gap = 4
    gui.draw_circle((x + radius, y + radius), radius, color=WHITE, thickness=2, num_segments=32)
    if filled:
        gui.draw_circle_filled((x + radius, y + radius), radius - gap, color=WHITE, num_segments=32)

def draw_dpad(x, y, input):
    side = 2 * SCALE
    gap = 4
    gui.draw_polyline([
        (x + 1*side, y),
        (x + 2*side, y),
        (x + 2*side, y + 1*side),
        (x + 3*side, y + 1*side),
        (x + 3*side, y + 2*side),
        (x + 2*side, y + 2*side),
        (x + 2*side, y + 3*side),
        (x + 1*side, y + 3*side),
        (x + 1*side, y + 2*side),
        (x, y + 2*side),
        (x, y + 1*side),
        (x + 1*side, y + 1*side),
    ], color=WHITE, closed=True, thickness=2)

    if input == 1: # Up
        gui.draw_rect_filled((x + side + gap, y + gap), (x + 2*side - gap, y + side), color=WHITE)
    if input == 2: # Down
        gui.draw_rect_filled((x + side + gap, y + 2*side), (x + 2*side - gap, y + 3*side - gap), color=WHITE)
    if input == 3: # Left
        gui.draw_rect_filled((x + gap, y + side + gap), (x + side, y + 2*side - gap), color=WHITE)
    if input == 4: # Right
        gui.draw_rect_filled((x + 2*side, y + side + gap), (x + 3*side - gap, y + 2*side - gap), color=WHITE)
    
def draw_stick(x, y, stick_x, stick_y):
    radius = 4 * SCALE
    gui.draw_circle((x + radius, y + radius), radius, color=WHITE, thickness=2, num_segments=8)
    gui.draw_rect((x, y), (x + 2*radius, y + 2*radius), color=T_WHITE, thickness=2,)
    
    stick_pos = (
        x + radius + (radius * stick_x / 7),
        y + radius - (radius * stick_y / 7),
    )
    gui.draw_circle_filled(stick_pos, em(1), color=WHITE, num_segments=32)


def render():
    race_mgr = mkw.RaceManager()
    if race_mgr.state().value < mkw.RaceState.COUNTDOWN.value:
        return

    race_mgr_player_addr = race_mgr.race_manager_player()
    race_mgr_player = mkw.RaceManagerPlayer(addr=race_mgr_player_addr)
    kart_input = mkw.KartInput(addr=race_mgr_player.kart_input())
    current_input_state = mkw.RaceInputState(addr=kart_input.current_input_state())

    ablr = current_input_state.buttons()
    dpad = current_input_state.trick()
    xstick = current_input_state.raw_stick_x() - 7
    ystick = current_input_state.raw_stick_y() - 7

    x_offset = 2*SCALE
    y_offset = vh(1.0) - 12*SCALE

    draw_LR_button(x_offset, y_offset, ablr.value & mkw.ButtonActions.L)
    draw_dpad(x_offset + 1*SCALE, y_offset + 3*SCALE, dpad)

    draw_stick(x_offset + 10*SCALE, y_offset + 0.5*SCALE, xstick, ystick)

    draw_LR_button(x_offset + 20*SCALE, y_offset, ablr.value & mkw.ButtonActions.B)
    draw_A_button(x_offset + 21.5*SCALE, y_offset + 3.5*SCALE, ablr.value & mkw.ButtonActions.A)

    csv_row = '   '.join([
        f'{1 if ablr.value & mkw.ButtonActions.A else 0}',
        f'{1 if ablr.value & mkw.ButtonActions.B else 0}',
        f'{1 if ablr.value & mkw.ButtonActions.L else 0}',
        f'{xstick:+}',
        f'{ystick:+}',
        f'{dpad}',
        '-'
    ])
    gui.draw_text((x_offset + 2*SCALE, vh(1.0) - em(1.5)), color=WHITE, text=csv_row)


@event.on_frameadvance
def on_frame_advance():
    if mkw_utils.extended_race_state() >= 0:
        render()

@event.on_savestateload
def on_state_load(fromSlot: bool, slot: int):
    if memory.is_memory_accessible() and mkw_utils.extended_race_state() >= 0:
        render()

@event.on_savestatesave
def on_state_save(fromSlot: bool, slot: int):
    if NO_DELAY and memory.is_memory_accessible() and mkw_utils.extended_race_state() >= 0:
        render()
