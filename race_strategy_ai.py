class RaceStrategyAI:
    def __init__(self):
        self.stint_wear = {}  # compound -> [wear per lap values]
        self.last_lap = -1

    def record_practice_wear(self, compound, avg_wear):
        if compound not in self.stint_wear:
            self.stint_wear[compound] = []
        self.stint_wear[compound].append(avg_wear)

    def simulate_stint_lengths(self):
        simulation = {}
        for compound, wears in self.stint_wear.items():
            if not wears:
                continue
            wear_rate = sum(wears) / len(wears)
            if wear_rate == 0:
                continue
            laps_to_100 = 100 / wear_rate
            simulation[compound] = int(laps_to_100)
        return simulation

    def recommend_stint_order(self):
        stint_lengths = self.simulate_stint_lengths()
        return sorted(stint_lengths.items(), key=lambda x: -x[1])  # longest first

    def adapt_strategy(self, current_lap, current_wear, compound):
        # crude logic: warn if wear rate too high compared to practice
        practice_rates = self.stint_wear.get(compound, [])
        if len(practice_rates) < 2:
            return "Gathering more data..."

        avg_rate = sum(practice_rates) / len(practice_rates)
        if avg_rate == 0:
            return "No wear detected in practice."

        laps_left = (100 - current_wear) / avg_rate
        if laps_left + current_lap < 10:
            return "⚠️ High wear rate — consider pitting earlier than planned."
        elif laps_left + current_lap > 15:
            return "✅ Low wear — you can extend this stint."
        return "Stint wear is on plan."
