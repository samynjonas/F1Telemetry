import csv
import os
from datetime import datetime

from constants import *

from car import Car
from lap import LapClass

# Logger file for telemetry data
class TelemetryLogger:
    def __init__(self, base_dir="logs"):
        os.makedirs(base_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.lap_file_path = os.path.join(base_dir, f"lap_telemetry_TRACK_SESSIONTYPE_{timestamp}.csv")
        self.input_file_path = os.path.join(base_dir, f"input_telemetry_TRACK_SESSIONTYPE_{timestamp}.csv")
        self.lap_header_written = False
        self.input_header_written = False

    def log_lap(self, car):
        with open(self.lap_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not self.lap_header_written:
                writer.writerow([
                    "CarIndex", "Lap", "LapTime", "Compound",
                    "FL_Wear", "FR_Wear", "RL_Wear", "RR_Wear",
                    "Sector", "SectorTime"
                ])
                self.lap_header_written = True

            for sector in car.lap.sectors:
                writer.writerow([
                    car.car_index,
                    car.lap.lap_number,
                    round(car.lap.time, 3),
                    TYRE_COMPOUND_MAP.get(car.lap.tire_type, f"Type {car.lap.tire_type}"),
                    round(sector.tire_wear[0], 1),
                    round(sector.tire_wear[1], 1),
                    round(sector.tire_wear[2], 1),
                    round(sector.tire_wear[3], 1),
                    sector.sector_number,
                    round(sector.time, 3)
                ])

    def log_car_status(self, car):
        with open(self.input_file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not self.input_header_written:
                writer.writerow([
                    "CarIndex", "Speed", "Throttle", "Brake", "Steer", "Clutch", "Gear",
                    "TireType", "FL_Wear", "FR_Wear", "RL_Wear", "RR_Wear"
                ])
                self.input_header_written = True

            writer.writerow([
                car.car_index,
                round(car.speed, 1),
                round(car.throttle, 2),
                round(car.brake, 2),
                round(car.steer, 2),
                round(car.clutch, 2),
                car.gear,
                TYRE_COMPOUND_MAP.get(car.tire_type, f"Type {car.tire_type}"),
                round(car.tire_wear[0], 1),
                round(car.tire_wear[1], 1),
                round(car.tire_wear[2], 1),
                round(car.tire_wear[3], 1)
            ])