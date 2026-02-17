from dolphin import event, gui, memory # type: ignore
from Modules import mkw_classes as mkw, mkw_utils
from Modules.custom_hud import *


def render():
    width = em(12)
    height = em(1.5)
    x = vw(0.95) - width
    y = vh(0.95) - height

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
    gui.draw_rect_filled((x, y), (x + speed_progress, y + height), color=speed_color)
    gui.draw_text((x - em(0.5), y - em(1)), color=WHITE, text=f'{speed:>7.2f}')
    gui.draw_text((x + em(3), y - em(1)), color=speed_color, text=f'{diff:>+7.2f}')

    # Speed limit border
    gui.draw_rect((x, y), (x + limit_progress, y + height), color=WHITE, thickness=2)

    # Border
    gui.draw_rect((x, y), (x + width, y + height), color=T_WHITE)

    prev_values[0].update({
        "engine": mkw.KartMove.speed()
    })


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