
import struct

UDP_IP = "0.0.0.0"
UDP_PORT = 20777
LOG_INTERVAL = 0.2  # seconds

DEBUG_PRINT = True

HEADER_FORMAT = '<HBBBBBQfIIBB'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

MOTION_DATA_FORMAT = '<fff fff hhh hhh ffffff' # world pos, vel, forward dir, right dir, gforce, angles
MOTION_DATA_SIZE = struct.calcsize(MOTION_DATA_FORMAT)

CAR_DAMAGE_DATA_FORMAT = '<4f4B4B4B18B'
CAR_DAMAGE_DATA_SIZE = struct.calcsize(CAR_DAMAGE_DATA_FORMAT)

LAP_DATA_FORMAT = '<IIHBHBHBHBfffBBBBBBBBBBBBBBBHHBfB'
LAP_DATA_SIZE = struct.calcsize(LAP_DATA_FORMAT)

CAR_STATUS_DATA_FORMAT = '<5B3fHHBBHBBb2fBfffffB'
CAR_STATUS_DATA_SIZE = struct.calcsize(CAR_STATUS_DATA_FORMAT)

SESSION_DATA_FORMAT = '<BBBBBQfII BBBbBHHbB'
SESSION_DATA_SIZE = struct.calcsize(SESSION_DATA_FORMAT)

CAR_TELEMETRY_FORMAT = "<HfffBbb"
CAR_TELEMETRY_SIZE = struct.calcsize(CAR_TELEMETRY_FORMAT)

SESSION_TYPE_MAP = {
    0: 'Unknown', 1: 'Practice 1', 2: 'Practice 2', 3: 'Practice 3', 4: 'Short Practice',
    5: 'Qualifying 1', 6: 'Qualifying 2', 7: 'Qualifying 3', 8: 'Short Qualifying', 9: 'One-Shot Qualifying',
    10: 'Sprint Shootout 1', 11: 'Sprint Shootout 2', 12: 'Sprint Shootout 3', 13: 'Short Sprint Shootout',
    14: 'One-Shot Sprint Shootout', 15: 'Race', 16: 'Race 2', 17: 'Race 3', 18: 'Time Trial', 28: 'F1 World Event (Unmapped)'
}

TYRE_COMPOUND_MAP = {
    16: 'C5', 17: 'C4', 18: 'C3', 19: 'C2', 20: 'C1', 21: 'C0', 22: 'C6',
    7: 'Intermediate', 8: 'Wet',
    9: 'Classic Dry', 10: 'Classic Wet',
    11: 'F2 Super Soft', 12: 'F2 Soft', 13: 'F2 Medium', 14: 'F2 Hard', 15: 'F2 Wet',
    0: 'Unknown'
}
