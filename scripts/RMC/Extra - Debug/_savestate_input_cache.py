from dolphin import controller, event # type: ignore
from Modules import mkw_utils

@event.on_savestatesave
def on_save_state(is_slot: bool, slot: int):
    if is_slot:
        cache[slot] = controller.get_gc_buttons(0)
        print(f'Cached inputs for savestate slot {slot} on frame {mkw_utils.frame_of_input()}')

@event.on_savestateload
def on_load_state(is_slot: bool, slot: int):
    if is_slot and cache.get(slot):
        controller.set_gc_buttons(0, cache[slot])


def main():
    global cache
    cache = {}


if __name__ == '__main__':
    main()