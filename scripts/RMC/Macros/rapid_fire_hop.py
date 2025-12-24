"""
Usage: Hold B to rapid fire hop. Enable the `optimize_EV` script to supergrind.
"""
from dolphin import controller, event # type: ignore
from Modules import mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

def on_frame_advance(*_):
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    if user_inputs["B"]:
        drift_input = mkw.KartState.bitfield() & 4 > 0
        ctrl.set_inputs({
            "B": not drift_input,
        })

event.on_frameadvance(on_frame_advance)
event.on_savestateload(on_frame_advance)
