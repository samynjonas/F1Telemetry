class RaceStrategyAdvisor:
    def __init__(self):
        self.practice_data = []  # stores (lap, tire_type, avg_wear)
        self.race_data = []      # stores (lap, tire_type, avg_wear)

    def add_practice_lap(self, lap, tire_type, tire_snapshot):
        avg_wear = (tire_snapshot.average_front() + tire_snapshot.average_rear()) / 2
        self.practice_data.append((lap, tire_type, avg_wear))

    def add_race_lap(self, lap, tire_type, tire_snapshot):
        avg_wear = (tire_snapshot.average_front() + tire_snapshot.average_rear()) / 2
        self.race_data.append((lap, tire_type, avg_wear))

    def estimate_wear_rates(self):
        """Estimates wear per lap for each tire type from practice data."""
        wear_rates = {}
        type_data = {}
        for _, tire_type, wear in self.practice_data:
            if tire_type not in type_data:
                type_data[tire_type] = []
            type_data[tire_type].append(wear)

        for tire_type, wears in type_data.items():
            if len(wears) > 1:
                avg_delta = (max(wears) - min(wears)) / len(wears)
                wear_rates[tire_type] = avg_delta
            else:
                wear_rates[tire_type] = 0.0

        return wear_rates

    def check_race_strategy(self, current_lap, pit_window_start, pit_window_end):
        if not self.race_data:
            return "Not enough data yet."

        last_lap, tire_type, last_avg = self.race_data[-1]
        previous = [entry for entry in self.race_data if entry[1] == tire_type]

        if len(previous) < 2:
            return "Collecting more data to provide tips..."

        wear_deltas = [j[2] - i[2] for i, j in zip(previous[:-1], previous[1:]) if j[2] > i[2]]
        avg_wear_per_lap = sum(wear_deltas) / len(wear_deltas)

        if avg_wear_per_lap == 0:
            return "Tire wear stable."

        projected_life = (100 - last_avg) / avg_wear_per_lap

        if current_lap + projected_life < pit_window_start:
            return "You're wearing tires too fast! You won't reach the pit window."
        elif current_lap + projected_life > pit_window_end:
            return "Tire wear is low. You can afford to push harder."
        else:
            return "You're on track for your pit strategy."
