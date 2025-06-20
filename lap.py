from constants import *

class SectorClass:
    def __init__(self, sector_number):
        self.sector_number = sector_number
        self.time = 0.0
        self.tire_wear = [0.0, 0.0, 0.0, 0.0]

class LapClass:
    def __init__(self, lap_number):
        self.lap_number = lap_number
        self.time = 0.0
        self.tire_wear = [0.0, 0.0, 0.0, 0.0]
        self.tire_type = -1
        self.sectors = [SectorClass(1), SectorClass(2), SectorClass(3)]

    def add_sector(self, sector_number):
        self.sectors[sector_number].time = self.time
        self.sectors[sector_number].tire_wear = self.tire_wear

    def update_lap_time(self, lap_time):
        if lap_time > self.time:
            self.time = lap_time

    def update_tire_wear(self, tire_wear):
        if len(tire_wear) == 4:
            self.tire_wear = tire_wear
        else:
            raise ValueError("Tire wear data must contain exactly 4 values for FL, FR, RL, RR.")
        
    def update_tire_type(self, tire_type):
        if tire_type != self.tire_type:
            self.tire_type = tire_type

    def __str__(self):
        compound = TYRE_COMPOUND_MAP.get(self.tire_type, f"Type {self.tire_type}")
        lapString = f"Lap: {self.lap_number} | Time={self.time:.3f}s, Compound: {compound}"
        for sector in self.sectors:
            lapString += f"\n Sector: {sector.sector_number} | {sector.time:.3f}s"
        return lapString