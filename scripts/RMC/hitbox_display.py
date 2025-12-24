from dolphin import event, gui, memory # type: ignore
from Modules import mkw_classes as mkw, mkw_utils

DRAW_POSITION = (10, 10)
NO_DELAY = True

def draw_hitboxes(origin):
    hitbox_spheres = [s for s in [mkw.BSP.Hitbox(0, i) for i in range(16)] if s.enable()]
    wheel_spheres = [s for s in [mkw.BSP.Wheel(0, i) for i in range(4)] if s.rel_pos().length() > 0]

    for h in hitbox_spheres:
        pos = h.pos()
        gui.draw_circle(
            center=(origin[0] + pos.z, origin[1] - pos.y),
            radius=h.radius(),
            color=0xFFFFFFFF,
            thickness=2,
            num_segments=32
        )
    
    for w in wheel_spheres:
        pos = w.rel_pos()
        gui.draw_circle(
            center=(origin[0] + pos.z, origin[1] - pos.y),
            radius=w.wheel_radius(),
            color=0xFFFFFF00,
            thickness=2,
            num_segments=32
        )
        gui.draw_circle(
            center=(origin[0] + pos.z, origin[1] - pos.y),
            radius=w.sphere_radius(),
            color=0xFFFF00FF,
            thickness=2,
            num_segments=32
        )
    
    # temp
    hitboxes_text = '\n'.join([f'pos: {h.pos()} | radius: {h.radius()} | walls: {h.inst_walls_only()}' for h in hitbox_spheres])
    wheels_text = '\n'.join([f'pos: {h.rel_pos()} | wheel_radius: {h.wheel_radius()} | sphere_radius: {h.sphere_radius()}' for h in wheel_spheres])
    gui.draw_text(DRAW_POSITION, 0xFFFFFFFF, f'{hitboxes_text}\n\n{wheels_text}')


def render(player_idx: int = 0):
    draw_hitboxes((150, 350))


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


if __name__ == '__main__':
    main()