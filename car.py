from lap import LapClass
from car_data import CarDataClass
from constants import *

class Car:
    def __init__(self, car_index):
        self.car_index = car_index
        self.speed = 0.0
        self.throttle = 0.0
        self.brake = 0.0
        self.steer = 0.0
        self.clutch = 0.0
        self.gear = 0
        self.tire_wear = [0.0, 0.0, 0.0, 0.0]  # FL, FR, RL, RR
        self.tire_type = 0
        self.used_race_tires = []
        self.fastest_lap = 0.0
        self.laps = []
        self.lap = LapClass(0)  # Current lap snapshot
        self.sector_number = 0  # Current sector number
        self.car_data = []

    def update_car_damage(self, tire_wear):
        if len(tire_wear) == 4:
            self.tire_wear = tire_wear
            self.lap.update_tire_wear(tire_wear)
        else:
            raise ValueError("Tire wear data must contain exactly 4 values for FL, FR, RL, RR.")
        
    def update_car_status(self, tire_type):
        if tire_type != self.tire_type:
            self.tire_type = tire_type
            self.used_race_tires.append(tire_type)
            self.lap.update_tire_type(tire_type)

    def update_car_inputs(self, speed, throttle, brake, steer, clutch, gear, lap_distance=0.0, track_length=0.0):
        self.speed = speed
        self.throttle = throttle
        self.brake = brake
        self.steer = steer
        self.clutch = clutch
        self.gear = gear

        carData = CarDataClass(
            self.car_index, speed, throttle, brake, steer, clutch, gear,
            self.tire_wear, self.tire_type, lap_distance, track_length
        )
        self.car_data.append(carData)



    def update_lap_time(self, lap_time):
        self.lap.update_lap_time(lap_time)

    def started_new_lap(self, lap_number):
        self.laps.append(self.lap)

        self.lap.lap_number = lap_number
        if self.lap.time < self.fastest_lap or self.fastest_lap == 0.0:
            self.fastest_lap = self.lap.time
        self.lap = LapClass(lap_number)

        if DEBUG_PRINT:
            print(f"New lap started: {lap_number}, Fastest Lap: {self.fastest_lap:.3f}s")
    
    def started_new_sector(self, sector_number):
        self.lap.add_sector(sector_number)
        self.sector_number = sector_number

        if DEBUG_PRINT:
            print(f"New sector started: {sector_number} for Lap {self.lap.lap_number}")

    def print_status(self):
        #print(f"Car Index: {self.car_index}")
        #print(f"Speed: {self.speed:.2f} km/h, Throttle: {self.throttle:.2f}, Brake: {self.brake:.2f}, Steer: {self.steer:.2f}, Clutch: {self.clutch:.2f}, Gear: {self.gear}")
        #print(f"Tire Wear: FL={self.tire_wear[0]:.1f}%, FR={self.tire_wear[1]:.1f}%, RL={self.tire_wear[2]:.1f}%, RR={self.tire_wear[3]:.1f}%")
        #print(f"Tire Type: {self.tire_type}")
        #print(f"Fastest Lap: {self.fastest_lap:.3f}s, Current Lap: {self.lap.lap_number}")
        print(f"Current Lap: {self.lap}")
        