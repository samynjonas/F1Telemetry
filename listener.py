
import socket
import time
import threading
import csv

from datetime import datetime
from constants import *
from packet_parsers import F1PacketParser

from car import Car
from data_logging import TelemetryLogger

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening for F1 25 telemetry on port {UDP_PORT}...")

data_logger = TelemetryLogger()
parser = F1PacketParser()

def udp_listener(gui):
    last_log_time = 0

    player_car = Car(-1)
    player_index = 0

    track_length = 5000  # Default fallback value
    distance_around_track = 0.0

    while True:
        data, _ = sock.recvfrom(2048)
        if len(data) < HEADER_SIZE:
            continue  # Ignore incomplete headers

        try:
            parse_result = parser.parse_packet(data, car_index=player_index)
        except (ValueError, struct.error) as e:
            print(f"Skipping packet due to error: {e}")
            continue

        parse_result = parser.parse_packet(data, car_index=player_index)
        header = parse_result['header']
        packet_id = header.m_packetId
        player_index = header.m_playerCarIndex

        # Initialize player car if not already set
        if player_car.car_index != player_index:
            player_car = Car(player_index)

        if packet_id == 1:
            session_data = parser.parse_session(header, data)
            track_length = session_data["trackLength"]
        elif packet_id == 2:
            lap_info = parser.parse_lap_data(header, data, car_index=player_index)['lapData']
            lap_time = lap_info['currentLapTimeInMS'] / 1000.0
            distance_around_track = lap_info['lapDistance']
            player_car.update_lap_time(lap_time)
            if lap_info['sector'] != player_car.sector_number:
                player_car.started_new_sector(lap_info['sector'])
            if lap_info['currentLapNum'] != player_car.lap.lap_number:
                data_logger.log_lap(player_car)
                player_car.started_new_lap(lap_info['currentLapNum'])
        elif packet_id == 10:
            try:
                car_damage_data = parser.parse_car_damage(header, data, car_index=player_index)
                current_tire_wear = car_damage_data['carDamageData'][0]['tyresWear']
                player_car.update_car_damage(current_tire_wear)
            except struct.error:
                continue
        elif packet_id == 7:
            try:
                car_status = parser.parse_car_status(header, data, car_index=player_index)
                tire_type = car_status['carStatusData'][0]['visualTyreCompound']
                player_car.update_car_status(tire_type)
            except struct.error:
                continue
        elif packet_id == 6:
            try:
                car_telemetry_data = parser.parse_car_telemetry(header, data, car_index=player_index)
                data = car_telemetry_data['carTelemetryData']
                player_car.update_car_inputs(
                    data['speed'], data['throttle'], data['brake'],
                    data['steer'], data['clutch'], data['gear'], 
                    distance_around_track, track_length
                )
                now = time.time()
                last_log_time = now
            except struct.error:
                continue

        if DEBUG_PRINT:
            print(f"Distance: {distance_around_track:.2f}m | Track Length: {track_length}m")

        now = time.time()
        if now - last_log_time > LOG_INTERVAL:
            # Log the current lap data
            data_logger.log_car_status(player_car)
            last_log_time = now
