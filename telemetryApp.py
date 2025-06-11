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
    def __init__(self, sector, lap, time, tire_wear):
        self.sector = sector
        self.lap = lap
        self.time = time
        self.tire_wear = tire_wear

    def __str__(self):
        return f"Sector {self.sector} (Lap {self.lap}): Time={self.time:.3f}s, Tire Wear: {self.tire_wear}"

class LapSnapshot:
    def __init__(self, lap, time, tire_wear):
        self.lap = lap
        self.time = time
        self.tire_wear = tire_wear
        self.sectors = []

    def add_sector(self, sector_snapshot):
        self.sectors.append(sector_snapshot)

    def __str__(self):
        lapString = f"Lap {self.lap}: Time={self.time:.3f}s, Tire Wear: {self.tire_wear}"
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

    def cache_lap_data(self):
        print(f"Cached data from lap: {self.current_lap}")
        tyreSnapshot = TyreWearSnapshot(*self.tire_wear)
        lapSnapshot = LapSnapshot(self.current_lap, self.current_lap_time, tyreSnapshot)
        for sector in self.current_lap_sectors:
            lapSnapshot.add_sector(sector)
        print(lapSnapshot)
        self.current_lap_time = 0.0
        self.current_lap_sectors = []

    def cache_sector_data(self):
        print(f"Cached data from sector {self.current_sector + 1}")
        tyreSnapshot = TyreWearSnapshot(*self.tire_wear)
        sectorSnapshot = SectorSnapshot(self.current_sector + 1, self.current_lap, self.current_lap_time, tyreSnapshot)
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

isFirstLap = False

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
    return list(unpacked[0:4])  # Tyres wear only

# Main loop
tracker = TelemetryTracker()

while True:
    data, _ = sock.recvfrom(2048)
    if len(data) < HEADER_SIZE:
        continue

    header = parse_packet_header(data)
    packet_id = header['packetId']
    player_index = header['playerCarIndex']

    if packet_id == 2:
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

    # IDEAS
    # - Store telemetry data in a structured format (e.g., list of dicts)
    # - Implement a simple GUI to visualize telemetry data in real-time
    # - Check average tire wear per lap and calculate if the driver is managing tires well
    # - Check if driver is using DRS effectively (e.g., activating it in zones)
    # - Calculate average speed per sector and compare with previous laps
    # - Implement a simple analysis of lap times and consistency
    # - Add voice alerts for significant events (e.g., tire wear above a threshold, DRS not used in a DRS zone)
    # - Get tire type and save with tyre wear data