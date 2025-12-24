"""
"""
from dolphin import controller, event # type: ignore
from Modules import mkw_classes as mkw
from Modules.macro_utils import MKWiiGCController

def clamp(x: int, l: int, u: int):
    return l if x < l else u if x > u else x

@event.on_frameadvance
def on_frame_advance():
    if mkw.RaceManager().state() != mkw.RaceState.RACE:
        return

    ctrl = MKWiiGCController(controller)
    user_inputs = ctrl.user_inputs()

    # No vertical stick inputs while grounded
    adjusted_airtime = (mkw.KartMove.airtime() + 1) if (mkw.KartCollide.surface_properties().value & 0x1000) == 0 else 0
    if adjusted_airtime == 0:
        ctrl.set_inputs({ "StickY": 0 })

    # Clamp soft inputs to +-3
    if abs(user_inputs['StickX']) < 7:
        ctrl.set_inputs({
            "StickX": clamp(user_inputs['StickX'], -3, 3),
        })
