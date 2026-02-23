from dolphin import memory

from . import KartObject, vec3

class KartState:
    def __init__(self, player_idx=0, addr=None):
        self.addr = addr if addr else KartState.chain(player_idx)

        self.bitfield = self.inst_bitfield
        self.airtime = self.inst_airtime
        self.top = self.inst_top
        self.hwg_timer = self.inst_hwg_timer
        self.boost_ramp_type = self.inst_boost_ramp_type
        self.jump_pad_type = self.inst_jump_pad_type
        self.cnpt_id = self.inst_cnpt_id
        self.stick_x = self.inst_stick_x
        self.stick_y = self.inst_stick_y
        self.oob_wipe_state = self.inst_oob_wipe_state
        self.oob_wipe_frame = self.inst_oob_wipe_frame
        self.start_boost_charge = self.inst_start_boost_charge
        self.start_boost_idx = self.inst_start_boost_idx
        self.trickable_timer = self.inst_trickable_timer
    
    @staticmethod
    def chain(player_idx=0) -> int:
        return KartObject.kart_state(player_idx)
    
    class Flags:
        # https://github.com/vabold/Kinoko/blob/main/source/game/kart/KartMove.cc#L2434-L2436

        Accelerate = 0, #< Accel button is pressed.
        Brake = 1,      #< Brake button is pressed.
        # @brief A "fake" button, normally set if you meet the speed requirement to hop.
        # @warning When playing back a ghost, the game will register a hop regardless of whether
        # or not the acceleration button is pressed. This can lead to "successful" synchronization
        # of ghosts which could not have been created legitimately in the first place.
        DriftInput = 2,
        DriftManual = 3,                #< Currently in a drift w/ manual.
        BeforeRespawn = 4,              #< Set on respawn collision, cleared on position snap.
        Wall3Collision = 5,             #< Set when colliding with wall KCL #COL_TYPE_WALL_2
        WallCollision = 6,              #< Set if we are colliding with a wall.
        HopStart = 7,                   #< Set if @ref m_bDriftInput was toggled on this frame.
        AccelerateStart = 8,            #< Set if @ref m_bAccelerate was toggled on this frame.
        GroundStart = 9,                #< Set first frame landing from airtime.
        VehicleBodyFloorCollision = 10, #< Set if the vehicle body is colliding with the floor.
        AnyWheelCollision = 11,         #< Set when any wheel is touching floor collision.
        AllWheelsCollision = 12,        #< Set when all wheels are touching floor collision.
        StickLeft = 13,          #< Set on left stick input. Mutually exclusive to @ref m_bStickRight.
        WallCollisionStart = 14, #< Set if we have just started colliding with a wall.
        AirtimeOver20 = 15,      #< Set after 20 frames of airtime, resets on landing.
        StickyRoad = 16,         #< Like the rBC stairs
        TouchingGround = 18,     #< Set when any part of the vehicle is colliding with floor KCL.
        Hop = 19,                #< Set while we are in a drift hop. Clears when we land.
        Boost = 20,              #< Set while in a boost.
        DisableAcceleration = 22,
        AirStart = 23,
        StickRight = 24,      #< Set on right stick input. Mutually exclusive to @ref m_bStickLeft.
        LargeFlipHit = 25,    #< Set when hitting an exploding object.
        MushroomBoost = 26,   #< Set while we are in a mushroom boost.
        SlipdriftCharge = 27, #< Currently in a drift w/ automatic.
        DriftAuto = 28,
        Wheelie = 29, #< Set while we are in a wheelie (even during the countdown).
        JumpPad = 30,
        RampBoost = 31,

        InAction = 32,
        TriggerRespawn = 33,
        CannonStart = 35,
        InCannon = 36,
        TrickStart = 37,
        InATrick = 38,
        BoostOffroadInvincibility = 39, #< Set if we should ignore offroad slowdown this frame.
        HalfPipeRamp = 41,              #< Set while colliding with zipper KCL.
        OverZipper = 42,                #< Set while mid-air from a zipper.
        JumpPadMushroomCollision = 43,
        ZipperInvisibleWall = 44,   #< Set when colliding with invisible wall above a zipper.
        ZipperBoost = 45,           #< Set when boosting after landing from a zipper.
        ZipperStick = 46,           #< Set while mid-air and still influenced by the zipper.
        ZipperTrick = 47,           #< Set while tricking mid-air from a zipper.
        DisableBackwardsAccel = 48, #< Enforces a 20f delay when reversing after charging SSMT.
        RespawnKillY = 49,          #< Set while respawning to cap external velocity at 0.
        Burnout = 50,               #< Set during a burnout on race start.
        TrickRot = 54,
        JumpPadMushroomVelYInc = 55,
        ChargingSSMT = 57,      #< Tracks whether we are charging a stand-still mini-turbo.
        RejectRoad = 59,        #< Collision which causes a change in the player's pos and rot.
        RejectRoadTrigger = 60, #< e.g. DK Summit ending, and Maple Treeway side walls.
        Trickable = 62,

        WheelieRot = 68,
        SkipWheelCalc = 69,
        JumpPadMushroomTrigger = 70,
        Shocked = 71,
        MovingWaterStickyRoad = 73,
        NoSparkInvisibleWall = 75,
        CollidingOffroad = 76,
        InRespawn = 77,
        AfterRespawn = 78,
        Crushed = 80,
        JumpPadFixedSpeed = 84,
        MovingWaterDecaySpeed = 85,
        JumpPadDisableYsusForce = 86,
        HalfpipeMidair = 87,

        UNK2 = 97,
        SomethingWallCollision = 99,
        SoftWallDrift = 100,
        HWG = 101, #< Set when "Horizontal Wall Glitch" is active.
        AfterCannon = 102,
        ActionMidZipper = 103,  #< Set when we enter an action while mid-air from a zipper.
        ChargeStartBoost = 104, #< Like @ref m_bAccelerate but during countdown.
        MovingWaterVertical = 105,
        EndHalfPipe = 107,

        AutoDrift = 133, #< True if auto transmission, false if manual.

        def __init__(self, player_idx=0):
            self.player_idx = player_idx

        def on_bit(self, *flags) -> bool:
            mask = sum((1 << f) for (f,) in flags)
            for i in range(5):
                bitfield = KartState.bitfield(self.player_idx, field_idx=i)
                if bitfield & (mask >> 32*i) & ((1 << 32) - 1):
                    return True
            return False
            

    @staticmethod
    def bitfield(player_idx=0, field_idx=0) -> int:
        assert(0 <= field_idx < 5)
        kart_state_ref = KartState.chain(player_idx)
        bitfield_ref = kart_state_ref + 0x4 + (field_idx * 0x4)
        return memory.read_u32(bitfield_ref)

    def inst_bitfield(self, field_idx=0) -> int:
        assert(0 <= field_idx < 5)
        bitfield_ref = self.addr + 0x4 + (field_idx * 0x4)
        return memory.read_u32(bitfield_ref)

    @staticmethod
    def airtime(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        airtime_ref = kart_state_ref + 0x1C
        return memory.read_u32(airtime_ref)

    def inst_airtime(self) -> int:
        airtime_ref = self.addr + 0x1C
        return memory.read_u32(airtime_ref)

    @staticmethod
    def top(player_idx=0) -> vec3:
        """Significance unknown?"""
        kart_state_ref = KartState.chain(player_idx)
        top_ref = kart_state_ref + 0x28
        return vec3.read(top_ref)

    def inst_top(self) -> int:
        top_ref = self.addr + 0x28
        return vec3.read(top_ref)

    @staticmethod
    def hwg_timer(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        hwg_timer_ref = kart_state_ref + 0x6C
        return memory.read_u32(hwg_timer_ref)

    def inst_hwg_timer(self) -> int:
        hwg_timer_ref = self.addr + 0x6C
        return memory.read_u32(hwg_timer_ref)

    @staticmethod
    def boost_ramp_type(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        boost_ramp_type_ref = kart_state_ref + 0x74
        return memory.read_u32(boost_ramp_type_ref)

    def inst_boost_ramp_type(self) -> int:
        boost_ramp_type_ref = self.addr + 0x74
        return memory.read_u32(boost_ramp_type_ref)

    @staticmethod
    def jump_pad_type(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        jump_pad_type_ref = kart_state_ref + 0x78
        return memory.read_u32(jump_pad_type_ref)

    def inst_jump_pad_type(self) -> int:
        jump_pad_type_ref = self.addr + 0x78
        return memory.read_u32(jump_pad_type_ref)

    @staticmethod
    def cnpt_id(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        cnpt_id_ref = kart_state_ref + 0x80
        return memory.read_u32(cnpt_id_ref)

    def inst_cnpt_id(self) -> int:
        cnpt_id_ref = self.addr + 0x80
        return memory.read_u32(cnpt_id_ref)

    @staticmethod
    def stick_x(player_idx=0) -> float:
        kart_state_ref = KartState.chain(player_idx)
        stick_x_ref = kart_state_ref + 0x88
        return memory.read_f32(stick_x_ref)

    def inst_stick_x(self) -> float:
        stick_x_ref = self.addr + 0x88
        return memory.read_f32(stick_x_ref)

    @staticmethod
    def stick_y(player_idx=0) -> float:
        kart_state_ref = KartState.chain(player_idx)
        stick_y_ref = kart_state_ref + 0x8C
        return memory.read_f32(stick_y_ref)

    def inst_stick_y(self) -> float:
        stick_y_ref = self.addr + 0x8C
        return memory.read_f32(stick_y_ref)

    @staticmethod
    def oob_wipe_state(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        oob_wipe_state_ref = kart_state_ref + 0x90
        return memory.read_u32(oob_wipe_state_ref)

    def inst_oob_wipe_state(self) -> int:
        oob_wipe_state_ref = self.addr + 0x90
        return memory.read_u32(oob_wipe_state_ref)

    @staticmethod
    def oob_wipe_frame(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        oob_wipe_frame_ref = kart_state_ref + 0x94
        return memory.read_u32(oob_wipe_frame_ref)

    def inst_oob_wipe_frame(self) -> int:
        oob_wipe_frame_ref = self.addr + 0x94
        return memory.read_u32(oob_wipe_frame_ref)

    @staticmethod
    def start_boost_charge(player_idx=0) -> float:
        kart_state_ref = KartState.chain(player_idx)
        start_boost_charge_ref = kart_state_ref + 0x9C
        return memory.read_f32(start_boost_charge_ref)

    def inst_start_boost_charge(self) -> float:
        start_boost_charge_ref = self.addr + 0x9C
        return memory.read_f32(start_boost_charge_ref)

    @staticmethod
    def start_boost_idx(player_idx=0) -> float:
        kart_state_ref = KartState.chain(player_idx)
        start_boost_idx_ref = kart_state_ref + 0xA0
        return memory.read_f32(start_boost_idx_ref)

    def inst_start_boost_idx(self) -> float:
        start_boost_idx_ref = self.addr + 0xA0
        return memory.read_f32(start_boost_idx_ref)

    @staticmethod
    def trickable_timer(player_idx=0) -> int:
        kart_state_ref = KartState.chain(player_idx)
        trickable_timer_ref = kart_state_ref + 0xA6
        return memory.read_u16(trickable_timer_ref)

    def inst_trickable_timer(self) -> int:
        trickable_timer_ref = self.addr + 0xA6
        return memory.read_u16(trickable_timer_ref)