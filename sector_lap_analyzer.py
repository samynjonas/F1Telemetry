class PerformanceAnalyzer:
    def __init__(self):
        self.best_sector_times = {}  # key: sector number, value: time in seconds
        self.best_lap_time = float('inf')
        self.last_lap_time = 0.0
        self.lap_times = []

    def update_sector(self, sector_snapshot):
        if sector_snapshot.sector not in self.best_sector_times or \
           sector_snapshot.time < self.best_sector_times[sector_snapshot.sector]:
            self.best_sector_times[sector_snapshot.sector] = sector_snapshot.time

    def update_lap(self, lap_snapshot):
        self.last_lap_time = lap_snapshot.time
        self.lap_times.append(lap_snapshot.time)
        if lap_snapshot.time < self.best_lap_time:
            self.best_lap_time = lap_snapshot.time

    def get_consistency_tip(self):
        if len(self.lap_times) < 3:
            return "Need more laps to judge consistency."
        avg = sum(self.lap_times) / len(self.lap_times)
        variance = max(self.lap_times) - min(self.lap_times)
        if variance < 0.3:
            return "Very consistent lap times. Good job!"
        elif variance < 1.0:
            return "Lap times are okay. Try to reduce mistakes."
        else:
            return "High lap time variance. Focus on braking and throttle points."

    def report_best_times(self):
        sector_report = ", ".join([
            f"S{sector}: {time:.3f}s" for sector, time in sorted(self.best_sector_times.items())
        ])
        return f"Best Lap: {self.best_lap_time:.3f}s | Sectors: {sector_report}"
