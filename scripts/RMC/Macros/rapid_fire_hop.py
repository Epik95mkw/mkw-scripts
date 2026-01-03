"""
Usage: Hold B to rapid fire hop. Enable the `optimize_EV` script to supergrind.
"""
from dolphin import controller, event # type: ignore
from Modules import mkw_classes as mkw, mkw_utils, ttk_lib
from Modules.macro_utils import MKWiiGCController
from Modules.framesequence import Frame

# "B" or "R"
RFH_INPUT = "R"

def on_frame_advance(*_):
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()
    # internal_inputs = Frame.from_current_frame(0)

    is_starting_drift = mkw.KartState.bitfield() & 4 > 0

    # print(mkw_utils.frame_of_input(), user_inputs[RFH_INPUT], ctrl.current_inputs()[RFH_INPUT])

    if user_inputs[RFH_INPUT]:
        # print(True)
        # internal_inputs.brake = not is_starting_drift
        # ttk_lib.write_player_inputs(internal_inputs)
        if is_starting_drift:
            ctrl.set_inputs({
                "B": False,
                "R": False,
                "TriggerRight": 1,
            })
        else:
            ctrl.set_inputs({
                "B": True,
            })

    # print(ctrl.current_inputs()["TriggerRight"])

event.on_frameadvance(on_frame_advance)
event.on_savestateload(on_frame_advance)
