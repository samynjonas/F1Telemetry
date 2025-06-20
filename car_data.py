class CarDataClass:
    def __init__(self, car_index, speed=0.0, throttle=0.0, brake=0.0, steer=0.0, clutch=0.0, gear=0,
                 tire_wear=None, tire_type=0, distance_around_track=0.0, track_length=0.0):
        self.car_index = car_index
        self.speed = speed
        self.throttle = throttle
        self.brake = brake
        self.steer = steer
        self.clutch = clutch
        self.gear = gear
        self.tire_wear = tire_wear
        self.tire_type = tire_type
        self.distance_around_track = distance_around_track
        self.track_length = track_length