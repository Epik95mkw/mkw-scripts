from dolphin import event, gui, memory # type: ignore
from Modules import mkw_classes as mkw, mkw_utils
from typing import Tuple

Position = Tuple[float, float]

NO_DELAY = True

WHITE = 0xFFFFFFFF
BLUE = 0xFF00FFFF
YELLOW = 0xFFFFFF00
ORANGE = 0xFFFFC000
GREEN = 0xFF00FF00
LIGHTGRAY = 0xFFCCCCCC
T_WHITE = 0x88FFFFFF
T_BLACK = 0x50000000


def engine_meter(pos: Position):
    width = 150
    height = 20

    speed = mkw.KartMove.speed()
    max_speed = 120
    speed_progress = (speed / max_speed) * width

    limit = mkw.KartMove.soft_speed_limit()
    max_limit = 120
    limit_progress = (limit / max_limit) * width

    prev_speed = prev_values[0].get('engine', speed)
    diff = speed - prev_speed

    speed_color = GREEN if diff > 0 else ORANGE if diff < 0 else LIGHTGRAY

    # Speed bar
    gui.draw_rect_filled(pos, (pos[0] + speed_progress, pos[1] + height), color=speed_color)
    gui.draw_text((pos[0] - 10, pos[1] - 17), color=WHITE, text=f'{speed:>7.2f}')
    gui.draw_text((pos[0] + 40, pos[1] - 17), color=speed_color, text=f'{diff:>+7.2f}')

    # Speed limit border
    gui.draw_rect(pos, (pos[0] + limit_progress, pos[1] + height), color=WHITE, thickness=2)

    # Border
    gui.draw_rect(pos, (pos[0] + width, pos[1] + height), color=T_WHITE)

    prev_values[0].update({
        "engine": mkw.KartMove.speed()
    })


def mt_meter(pos: Position):
    width = 100
    height = 15

    drift_state = mkw.KartMove.drift_state()

    mt = mkw.KartMove.mt_charge() + (1 if drift_state >= 2 else 0)
    max_mt = 271
    mt_progress = (mt / max_mt) * width

    smt = mkw.KartMove.smt_charge() + (1 if drift_state >= 3 else 0)
    max_smt = 301
    smt_progress = (smt / max_smt) * width

    boost = mkw.KartMove.mt_boost_timer()
    max_boost = mkw.PlayerStats.mt_duration() * (1 if mkw.KartSettings.is_bike() else 3)
    boost_progress = (boost / max_boost) * width

    border_color = WHITE
    mt_color = GREEN if mt == max_mt else BLUE
    smt_color = GREEN if smt == max_smt else ORANGE
    boost_color = GREEN

    if mt > 0 or boost > 0:
        # MT charge bar
        gui.draw_rect_filled(pos, (pos[0] + mt_progress, pos[1] + height), color=mt_color)
        if mt > 0 and smt == 0:
            gui.draw_text((pos[0] - 30, pos[1]), color=mt_color, text=f'{mt:>3}')

        # SMT charge bar
        gui.draw_rect_filled(pos, (pos[0] + smt_progress, pos[1] + height), color=smt_color)
        if smt > 0:
            gui.draw_text((pos[0] - 30, pos[1]), color=smt_color, text=f'{smt:>3}')

        # MT boost bar
        gui.draw_rect_filled((pos[0] + width - boost_progress, pos[1]), (pos[0] + width, pos[1] + height), color=boost_color)
        if boost > 0:
            gui.draw_text((pos[0] + width + 5, pos[1]), color=boost_color, text=f'{boost}')

        # Border
        gui.draw_rect(pos, (pos[0] + width, pos[1] + height), color=border_color)


def ssmt_meter(pos: Position): # (also includes start boost for now)
    width = 100
    height = 15

    ssmt = mkw.KartMove.ssmt_charge()
    max_ssmt = 75
    ssmt_progress = (ssmt / max_ssmt) * width

    boost = (mkw.KartBoost.all_mt_timer() - mkw.KartMove.mt_boost_timer())
    max_boost = 70 if mkw.KartState.start_boost_charge() == 1 else 30
    boost_progress = (boost / max_boost) * width

    ssmt_color = GREEN if ssmt == max_ssmt else BLUE
    boost_color = GREEN

    if ssmt > 0 or boost > 0:
        # SSMT charge bar
        gui.draw_rect_filled(pos, (pos[0] + ssmt_progress, pos[1] + height), color=ssmt_color)
        if ssmt > 0:
            gui.draw_text((pos[0] - 30, pos[1]), color=ssmt_color, text=f'{ssmt:>3}')
        
        # SSMT boost bar
        gui.draw_rect_filled((pos[0] + width - boost_progress, pos[1]), (pos[0] + width, pos[1] + height), color=boost_color)
        if boost > 0:
            gui.draw_text((pos[0] + width + 5, pos[1]), color=boost_color, text=f'{boost}')

        # Border
        gui.draw_rect(pos, (pos[0] + width, pos[1] + height), color=WHITE)


def wheelie_meter(pos: Position):
    if not mkw.KartSettings.is_bike():
        return
    width = 100
    height = 9

    in_wheelie = mkw.KartState.bitfield(field_idx=0) & 0x20_000_000

    max_timer = 181
    timer = max_timer - mkw.KartMove.wheelie_frames()
    progress = (timer / max_timer) * width

    cooldown = mkw.KartMove.wheelie_cooldown()
    max_cooldown = 20 - min(max_timer - timer, 19)
    cooldown_progress = (cooldown / max_cooldown) * progress

    color = T_WHITE
    cooldown_color = T_BLACK

    # wheelie timer
    if in_wheelie:
        gui.draw_rect_filled((pos[0] + width - progress, pos[1]), (pos[0] + width, pos[1] + height), color=color)
        gui.draw_text((pos[0] + width + 5, pos[1] - 2), color=color, text=f'{timer}')
    # cooldown
    if not in_wheelie and cooldown > 0:
        gui.draw_rect_filled((pos[0] + width - cooldown_progress, pos[1]), (pos[0] + width, pos[1] + height), color=cooldown_color)
        gui.draw_text((pos[0] + width + 5, pos[1] - 2), color=cooldown_color, text=f'{cooldown}')


def airtime_indicator(pos: Position):
    r = 7
    airtime = mkw.KartState.airtime()
    color = T_WHITE

    if airtime > 0:
        gui.draw_circle_filled((pos[0] + r, pos[1] + r), radius=r, color=color)
        gui.draw_text((pos[0] + 2*r + 5, pos[1]), color=color, text=f'AIR {airtime}')


def boost_meter(pos: Position):
    width = 100
    height = 15

    boost = mkw.KartBoost.mushroom_and_boost_panel_timer()
    max_boost = 90
    progress = (boost / max_boost) * width

    color = ORANGE

    if boost > 0:
        gui.draw_rect_filled((pos[0] + width - progress, pos[1]), (pos[0] + width, pos[1] + height), color=color)
        gui.draw_rect(pos, (pos[0] + width, pos[1] + height), color=WHITE)
        gui.draw_text((pos[0] - 30, pos[1]), color=WHITE, text=f'{boost:>3}')
    

def trick_meter(pos: Position):
    width = 100
    height = 15

    boost = mkw.KartBoost.trick_and_zipper_timer()
    max_boost = 95
    progress = (boost / max_boost) * width

    color = ORANGE

    if boost > 0:
        gui.draw_rect_filled((pos[0] + width - progress, pos[1]), (pos[0] + width, pos[1] + height), color=color)
        gui.draw_rect(pos, (pos[0] + width, pos[1] + height), color=WHITE)
        gui.draw_text((pos[0] - 30, pos[1]), color=WHITE, text=f'{boost:>3}')


def render(player_idx: int = 0):
    engine_meter((1150, 560))
    mt_meter((765, 230))
    ssmt_meter((765, 230))
    wheelie_meter((765, 250))
    airtime_indicator((780, 262))
    boost_meter((765, 210))
    trick_meter((765, 190))


@event.on_frameadvance
def on_frame_advance():
    global current_frame
    current_frame = mkw_utils.frame_of_input()

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


def main():
    global current_frame
    current_frame = 0

    global prev_values
    prev_values = [ {}, {} ]


if __name__ == '__main__':
    main()