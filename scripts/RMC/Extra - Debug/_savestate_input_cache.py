from dolphin import controller, event # type: ignore

@event.on_savestatesave
def on_save_state(is_slot: bool, slot: int):
    if is_slot:
        cache[slot] = controller.get_gc_buttons(0)

@event.on_savestateload
def on_load_state(is_slot: bool, slot: int):
    if is_slot and cache.get(slot):
        controller.set_gc_buttons(0, cache[slot])


def main():
    global cache
    cache = {}


if __name__ == '__main__':
    main()