from dolphin import event, savestate # type: ignore
from Modules import mkw_classes as mkw, mkw_utils
import math

START_FRAME = 1088
TEST_FRAME = 1098

class State:
    def __init__(self):
        self.savestate = None
        self.iteration = 0
    
    def set(self):
        if self.savestate is None:
            self.savestate = savestate.save_to_bytes()
    
    def load(self):
        self.iteration += 1
        savestate.load_from_bytes(self.savestate)

state = State()


@event.on_frameadvance
def on_frame_advance():
    frame = mkw_utils.frame_of_input()
 
    if frame == START_FRAME - 1:
        state.set()
    
    if frame == START_FRAME:
        print(f"Iteration {state.iteration}")
        position = mkw.VehiclePhysics.position()
        x_offset = (state.iteration * 0) - 12.6
        y_offset = (state.iteration * 1)
        z_offset = (state.iteration * 0) - 53
        position.x += x_offset
        position.y += y_offset
        position.z += z_offset
        print(f"  X: {position.x:.4f} ({x_offset:.4f}), Y: {position.y:.4f} ({y_offset:.4f}), Z: {position.z:.4f} ({z_offset:.4f})")
        position.write(mkw.VehiclePhysics.chain() + 0x68)
    
    if frame == TEST_FRAME:
        speed = mkw.KartMove.speed()
        print(f"  Speed: {speed:.4f}")
        if speed < 5 or mkw.KartState.hwg_timer() == 0:
            print("  FAILED")
            state.load()
