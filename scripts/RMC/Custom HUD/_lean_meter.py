from dolphin import event, gui, memory # type: ignore
from Modules import mkw_classes as mkw, mkw_utils
from Modules.custom_hud import *


def render():
    if not mkw.KartSettings.is_bike():
        return
    
    y = vh(0.9)
    height = em(2)
    scale = em(7)
    
    lean_rot = mkw.KartMove.lean_rot()

    is_drifting = mkw.KartMove.drift_state() > 0

    ignore_lean = mkw.KartState.Flags().on_bit(
        mkw.KartState.Flags.BeforeRespawn,
        mkw.KartState.Flags.Wheelie,
        mkw.KartState.Flags.RejectRoadTrigger,
        mkw.KartState.Flags.AirtimeOver20,
        mkw.KartState.Flags.SoftWallDrift,
        mkw.KartState.Flags.SomethingWallCollision,
        mkw.KartState.Flags.HWG,
        mkw.KartState.Flags.CannonStart,
        mkw.KartState.Flags.InCannon,
        mkw.KartState.Flags.InAction,
        mkw.KartState.Flags.OverZipper
    )
    
    if is_drifting and not ignore_lean:
        drift_lean_min = mkw.KartMove.TurningParameters.lean_rot_min_drift() * -mkw.KartMove.hop_stick_x()
        drift_lean_max = mkw.KartMove.TurningParameters.lean_rot_max_drift() * -mkw.KartMove.hop_stick_x()
        lean_rate = mkw.KartMove.TurningParameters.drift_stick_x_factor()
        left_end = vw(0.5) + (min(drift_lean_min, drift_lean_max) * scale)
        right_end = vw(0.5) + (max(drift_lean_min, drift_lean_max) * scale)
    else:
        lean_cap = mkw.KartMove.lean_rot_cap()
        lean_rate = mkw.KartMove.lean_rot_increase()
        left_end = vw(0.5) - (lean_cap * scale)
        right_end = vw(0.5) + (lean_cap * scale)

    left_red = left_end + (lean_rate * scale)
    right_red = right_end - (lean_rate * scale)

    line_x = vw(0.5) + (lean_rot * scale)
    line_gap = em(0.2)
    line_color = YELLOW if line_x < left_red or line_x > right_red else WHITE

    if ignore_lean:
        gui.draw_rect_filled((left_end, y), (right_end, y + height), color=GRAY)
    else: 
        gui.draw_rect_filled((left_end, y), (right_end, y + height), color=RED)
        gui.draw_rect_filled((left_red, y), (right_red, y + height), color=GREEN)
    gui.draw_rect((left_end, y), (right_end, y + height), color=WHITE, thickness=2)
    gui.draw_line((vw(0.5), y - em(0.5)), (vw(0.5), y + height + em(0.5)), color=T_WHITE, thickness=2)
    gui.draw_line((line_x, y - line_gap), (line_x, y + height + line_gap), color=line_color, thickness=6)
    


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