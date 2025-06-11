from race_analysis_logic import RaceStrategyAdvisor
from sector_lap_analyzer import PerformanceAnalyzer
from race_strategy_ai import RaceStrategyAI
import socket
import struct

class TyreWearSnapshot:
    def __init__(self, fl, fr, rl, rr):
        self.FL = fl
        self.FR = fr
        self.RL = rl
        self.RR = rr

    def average_front(self):
        return (self.FL + self.FR) / 2

    def average_rear(self):
        return (self.RL + self.RR) / 2

    def __str__(self):
        return f"FL={self.FL:.1f}%, FR={self.FR:.1f}%, RL={self.RL:.1f}%, RR={self.RR:.1f}%"

class SectorSnapshot:
    def __init__(self, sector, lap, time, tire_wear, tire_type):
        self.sector = sector
        self.lap = lap
        self.time = time
        self.tire_wear = tire_wear
        self.tire_type = tire_type

    def __str__(self):
        compound = TYRE_COMPOUND_MAP.get(self.tire_type, f"Type {self.tire_type}")
        return f"Sector {self.sector} (Lap {self.lap}): Time={self.time:.3f}s, Tire Wear: {self.tire_wear}, Compound: {compound}"

class LapSnapshot:
    def __init__(self, lap, time, tire_wear, tire_type):
        self.lap = lap
        self.time = time
        self.tire_wear = tire_wear
        self.tire_type = tire_type
        self.sectors = []

    def add_sector(self, sector_snapshot):
        self.sectors.append(sector_snapshot)

    def __str__(self):
        compound = TYRE_COMPOUND_MAP.get(self.tire_type, f"Type {self.tire_type}")
        lapString = f"Lap {self.lap}: Time={self.time:.3f}s, Tire Wear: {self.tire_wear}, Compound: {compound}"
        for sector in self.sectors:
            lapString += f"\n  {sector}"
        return lapString

class TelemetryTracker:
    def __init__(self):
        self.current_lap = 0
        self.current_lap_time = 0.0
        self.current_sector = 0
        self.current_lap_sectors = []
        self.tire_wear = [0.0, 0.0, 0.0, 0.0]
        self.tire_type = 0
        self.session_type = "Unknown"
        self.strategy_advisor = RaceStrategyAdvisor()
        self.performance_analyzer = PerformanceAnalyzer()
        self.strategy_ai = RaceStrategyAI()

    def cache_lap_data(self):
        print(f"Cached data from lap: {self.current_lap}")
        tyreSnapshot = TyreWearSnapshot(*self.tire_wear)
        avg_wear = (tyreSnapshot.average_front() + tyreSnapshot.average_rear()) / 2
        lapSnapshot = LapSnapshot(self.current_lap, self.current_lap_time, tyreSnapshot, self.tire_type)
        for sector in self.current_lap_sectors:
            lapSnapshot.add_sector(sector)
            self.performance_analyzer.update_sector(sector)

        print(lapSnapshot)
        self.performance_analyzer.update_lap(lapSnapshot)

        if self.session_type.lower().startswith("practice"):
            self.strategy_ai.record_practice_wear(self.tire_type, avg_wear)
            self.strategy_advisor.add_practice_lap(self.current_lap, self.tire_type, tyreSnapshot)
        elif self.session_type.lower().startswith("race"):
            self.strategy_advisor.add_race_lap(self.current_lap, self.tire_type, tyreSnapshot)
            self.strategy_advisor.add_race_lap(self.current_lap, self.tire_type, tyreSnapshot)
            print(self.strategy_advisor.check_race_strategy(self.current_lap, pit_window_start=10, pit_window_end=15))
            print(self.strategy_ai.adapt_strategy(self.current_lap, avg_wear, self.tire_type))

        print(self.performance_analyzer.report_best_times())
        print(self.performance_analyzer.get_consistency_tip())

        self.current_lap_time = 0.0
        self.current_lap_sectors = []

    def cache_sector_data(self):
        print(f"Cached data from sector {self.current_sector + 1}")
        tyreSnapshot = TyreWearSnapshot(*self.tire_wear)
        sectorSnapshot = SectorSnapshot(self.current_sector + 1, self.current_lap, self.current_lap_time, tyreSnapshot, self.tire_type)
        self.current_lap_sectors.append(sectorSnapshot)

# UDP setup
UDP_IP = "0.0.0.0"
UDP_PORT = 20777
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening for F1 25 telemetry on port {UDP_PORT}...")

# Structs
HEADER_FORMAT = '<HBBBBBQfII BB'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
CAR_DAMAGE_DATA_FORMAT = '<4f4B4B4B18B'
CAR_DAMAGE_DATA_SIZE = struct.calcsize(CAR_DAMAGE_DATA_FORMAT)
LAP_DATA_FORMAT = '<IIHBHBHBHBfffBBBBBBBBBBBBBBBHHBfB'
LAP_DATA_SIZE = struct.calcsize(LAP_DATA_FORMAT)
CAR_STATUS_DATA_FORMAT = '<5B3fHHBBHBBb2fBfffffB'
CAR_STATUS_DATA_SIZE = struct.calcsize(CAR_STATUS_DATA_FORMAT)
SESSION_DATA_FORMAT = '<BBBBBQfII BBBbBHHbB'
SESSION_DATA_SIZE = struct.calcsize(SESSION_DATA_FORMAT)

SESSION_TYPE_MAP = {
    0: 'Unknown', 1: 'Practice 1', 2: 'Practice 2', 3: 'Practice 3', 4: 'Short Practice',
    5: 'Qualifying 1', 6: 'Qualifying 2', 7: 'Qualifying 3', 8: 'Short Qualifying', 9: 'One-Shot Qualifying',
    10: 'Sprint Shootout 1', 11: 'Sprint Shootout 2', 12: 'Sprint Shootout 3', 13: 'Short Sprint Shootout',
    14: 'One-Shot Sprint Shootout', 15: 'Race', 16: 'Race 2', 17: 'Race 3', 18: 'Time Trial',
    28: 'F1 World Event (Unmapped)'  # placeholder for raw 28
}

# Add this near the top with other constants
TYRE_COMPOUND_MAP = {
    16: 'Soft', 17: 'Medium', 18: 'Hard',
    7: 'Intermediate', 8: 'Wet',
    0: 'Unknown',
}

# Parser functions
def parse_packet_header(data):
    unpacked = struct.unpack_from(HEADER_FORMAT, data)
    return {
        'packetId': unpacked[5],
        'playerCarIndex': unpacked[10]
    }

def parse_lap_data(data, offset):
    unpacked = struct.unpack_from(LAP_DATA_FORMAT, data, offset)
    return {
        'currentLapTimeInMS': unpacked[1],
        'currentLapNum': unpacked[14],
        'sector': unpacked[17]
    }

def parse_car_damage(data, offset):
    unpacked = struct.unpack_from(CAR_DAMAGE_DATA_FORMAT, data, offset)
    return list(unpacked[0:4])

def parse_car_status(data, offset):
    unpacked = struct.unpack_from(CAR_STATUS_DATA_FORMAT, data, offset)
    actual = unpacked[14]
    visual = unpacked[15]
    compound = visual if visual != 0 else actual
    return compound

def parse_session_type(data):
    expected_length = HEADER_SIZE + SESSION_DATA_SIZE
    if len(data) >= expected_length:
        raw_byte = data[HEADER_SIZE + 12]
        return SESSION_TYPE_MAP.get(raw_byte, f"Unknown ({raw_byte})")
    return "Unknown"

# Main loop
tracker = TelemetryTracker()

while True:
    data, _ = sock.recvfrom(2048)
    if len(data) < HEADER_SIZE:
        continue

    header = parse_packet_header(data)
    packet_id = header['packetId']
    player_index = header['playerCarIndex']

    if packet_id == 1:
        tracker.session_type = parse_session_type(data)
        #print(f"Session type detected: {tracker.session_type}")

    elif packet_id == 2:
        base_offset = HEADER_SIZE + (LAP_DATA_SIZE * player_index)
        lap_data = parse_lap_data(data, base_offset)
        lap_time = lap_data['currentLapTimeInMS'] / 1000.0
        if lap_time > tracker.current_lap_time:
            tracker.current_lap_time = lap_time

        if lap_data['sector'] != tracker.current_sector:
            tracker.cache_sector_data()
            tracker.current_sector = lap_data['sector']

        if lap_data['currentLapNum'] != tracker.current_lap:
            if tracker.current_lap > 0:
                tracker.cache_lap_data()
            tracker.current_lap = lap_data['currentLapNum']

    elif packet_id == 10:
        base_offset = HEADER_SIZE + (CAR_DAMAGE_DATA_SIZE * player_index)
        try:
            tracker.tire_wear = parse_car_damage(data, base_offset)
        except struct.error:
            continue

    elif packet_id == 7:
        base_offset = HEADER_SIZE + (CAR_STATUS_DATA_SIZE * player_index)
        try:
            tracker.tire_type = parse_car_status(data, base_offset)
        except struct.error:
            continue
