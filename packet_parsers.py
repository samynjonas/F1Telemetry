import struct
from constants import *
from dataclasses import dataclass
from typing import List

HEADER_FORMAT = '<HBBBBBQfIIBB'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

@dataclass
class PacketHeader:
    m_packetFormat: int
    m_gameYear: int
    m_gameMajorVersion: int
    m_gameMinorVersion: int
    m_packetVersion: int
    m_packetId: int
    m_sessionUID: int
    m_sessionTime: float
    m_frameIdentifier: int
    m_overallFrameIdentifier: int
    m_playerCarIndex: int
    m_secondaryPlayerCarIndex: int

    @classmethod
    def from_buffer(cls, buffer: bytes):
        return cls(*struct.unpack_from(HEADER_FORMAT, buffer, 0))


class F1PacketParser:
    def __init__(self):
        self.parsers = {
            0: self.parse_motion,
            1: self.parse_session,
            2: self.parse_lap_data,
            3: self.parse_event,
            4: self.parse_participants,
            5: self.parse_car_setups,
            6: self.parse_car_telemetry,
            7: self.parse_car_status,
            8: self.parse_final_classification,
            9: self.parse_lobby_info,
            10: self.parse_car_damage,
            11: self.parse_session_history,
            12: self.parse_tyre_sets,
            13: self.parse_motion_ex,
            14: self.parse_time_trial,
            15: self.parse_lap_positions,
        }

    def parse_packet(self, buffer: bytes, car_index: int = 0):
        header = PacketHeader.from_buffer(buffer)
        parser = self.parsers.get(header.m_packetId, self.unknown_packet)
        return parser(header, buffer, car_index)

    def unknown_packet(self, header: PacketHeader, buffer: bytes, *_):
        return {'header': header, 'data': None, 'note': 'Unknown packet ID'}

    def parse_motion(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 0'}
    def parse_session(self, header: PacketHeader, buffer: bytes):
        return {'header': header, 'data': 'Parsed packet type 1'}
    def parse_lap_data(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 2'}
    def parse_event(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 3'}
    def parse_participants(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 4'}
    def parse_car_setups(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 5'}
    def parse_car_telemetry(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 6'}
    def parse_car_status(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 7'}
    def parse_final_classification(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 8'}
    def parse_lobby_info(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 9'}
    def parse_car_damage(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 10'}
    def parse_session_history(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 11'}
    def parse_tyre_sets(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 12'}
    def parse_motion_ex(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 13'}
    def parse_time_trial(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 14'}
    def parse_lap_positions(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        return {'header': header, 'data': 'Parsed packet type 15'}

    def parse_motion(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        car_format = '<fff fff hhh hhh fff fff'
        car_size = struct.calcsize(car_format)
        offset = HEADER_SIZE + car_index * car_size
        data = struct.unpack_from(car_format, buffer, offset)
        return {
            'header': header,
            'carMotionData': [{
                'worldPositionX': data[0], 'worldPositionY': data[1], 'worldPositionZ': data[2],
                'worldVelocityX': data[3], 'worldVelocityY': data[4], 'worldVelocityZ': data[5],
                'worldForwardDirX': data[6], 'worldForwardDirY': data[7], 'worldForwardDirZ': data[8],
                'worldRightDirX': data[9], 'worldRightDirY': data[10], 'worldRightDirZ': data[11],
                'gForceLateral': data[12], 'gForceLongitudinal': data[13], 'gForceVertical': data[14],
                'yaw': data[15], 'pitch': data[16], 'roll': data[17]
            }]
        }

    def parse_session(self, header: PacketHeader, buffer: bytes, *_):
        # Based on F1 25 UDP spec from the uploaded document
        session_format = '<BbbBHBHBBfBBBBBBB'
        data = struct.unpack_from(session_format, buffer, HEADER_SIZE)
        return {
            'header': header,
            'weather': data[0],
            'trackTemperature': data[1],
            'airTemperature': data[2],
            'totalLaps': data[3],
            'trackLength': data[4],
            'sessionType': data[5],
            'trackId': data[6],
            'formula': data[7],
            'sessionTimeLeft': data[8],
            'sessionDuration': data[9],
            'pitSpeedLimit': data[10],
            'gamePaused': data[11],
            'isSpectating': data[12],
            'spectatorCarIndex': data[13],
            'sliProNativeSupport': data[14],
            'numMarshalZones': data[15]
        }

    def parse_car_telemetry(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        car_format = '<HfffBbhBBH4H4B4BH4f4B'  # 32 bytes per car
        car_size = struct.calcsize(car_format)
        offset = HEADER_SIZE + car_index * car_size
        data = struct.unpack_from(car_format, buffer, offset)
    
        return {
            'header': header,
            'carTelemetryData': {
                'speed': data[0],
                'throttle': data[1],
                'steer': data[2],
                'brake': data[3],
                'clutch': data[4],
                'gear': data[5],
                'engineRPM': data[6],
                'drs': data[7],
                'revLightsPercent': data[8],
                'revLightsBitValue': data[9],
                'brakesTemperature': list(data[10:14]),
                'tyresSurfaceTemperature': list(data[14:18]),
                'tyresInnerTemperature': list(data[18:22]),
                'engineTemperature': data[22],
                'tyresPressure': list(data[23:27]),
                'surfaceType': list(data[27:31])
            }
        }
    
    
    def parse_lap_data(self, header: PacketHeader, buffer: bytes, car_index: int = None):
        lap_format = '<IIH B H B H B H B f f f B B B B B B B B B B B B B B B H H B f B'
        lap_size = struct.calcsize(lap_format)

        if car_index is not None:
            offset = HEADER_SIZE + car_index * lap_size
            if offset + lap_size > len(buffer):
                raise IndexError(f"car_index {car_index} out of bounds for lap data packet size {len(buffer)}")
            data = struct.unpack_from(lap_format, buffer, offset)
            return {
                'header': header,
                'lapData': dict(zip([
                    'lastLapTimeInMS', 'currentLapTimeInMS', 'sector1TimeMS', 'sector1TimeMin',
                    'sector2TimeMS', 'sector2TimeMin', 'deltaToCarInFrontMS', 'deltaToCarInFrontMin',
                    'deltaToRaceLeaderMS', 'deltaToRaceLeaderMin', 'lapDistance', 'totalDistance',
                    'safetyCarDelta', 'carPosition', 'currentLapNum', 'pitStatus', 'numPitStops',
                    'sector', 'currentLapInvalid', 'penalties', 'totalWarnings', 'cornerCuttingWarnings',
                    'numUnservedDriveThroughPens', 'numUnservedStopGoPens', 'gridPosition', 'driverStatus',
                    'resultStatus', 'pitLaneTimerActive', 'pitLaneTimeInLaneInMS', 'pitStopTimerInMS',
                    'pitStopShouldServePen', 'speedTrapFastestSpeed', 'speedTrapFastestLap'
                ], data))
            }

        # If no car index is provided, return all cars' data
        lap_data = []
        for i in range(22):  # max cars
            offset = HEADER_SIZE + i * lap_size
            if offset + lap_size > len(buffer):
                break
            data = struct.unpack_from(lap_format, buffer, offset)
            lap_data.append(dict(zip([
                'lastLapTimeInMS', 'currentLapTimeInMS', 'sector1TimeMS', 'sector1TimeMin',
                'sector2TimeMS', 'sector2TimeMin', 'deltaToCarInFrontMS', 'deltaToCarInFrontMin',
                'deltaToRaceLeaderMS', 'deltaToRaceLeaderMin', 'lapDistance', 'totalDistance',
                'safetyCarDelta', 'carPosition', 'currentLapNum', 'pitStatus', 'numPitStops',
                'sector', 'currentLapInvalid', 'penalties', 'totalWarnings', 'cornerCuttingWarnings',
                'numUnservedDriveThroughPens', 'numUnservedStopGoPens', 'gridPosition', 'driverStatus',
                'resultStatus', 'pitLaneTimerActive', 'pitLaneTimeInLaneInMS', 'pitStopTimerInMS',
                'pitStopShouldServePen', 'speedTrapFastestSpeed', 'speedTrapFastestLap'
            ], data)))

        return {'header': header, 'lapData': lap_data}

    def parse_car_status(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        # Adjusted to correct field count (F1 25 spec)
        car_format = '<BBBBBfffHHBBHBBbfffBff'
        car_size = struct.calcsize(car_format)
        offset = HEADER_SIZE + car_index * car_size
        data = struct.unpack_from(car_format, buffer, offset)
        return {
            'header': header,
            'carStatusData': [{
                'tractionControl': data[0],
                'antiLockBrakes': data[1],
                'fuelMix': data[2],
                'frontBrakeBias': data[3],
                'pitLimiterStatus': data[4],
                'fuelInTank': data[5],
                'fuelCapacity': data[6],
                'fuelRemainingLaps': data[7],
                'maxRPM': data[8],
                'idleRPM': data[9],
                'maxGears': data[10],
                'drsAllowed': data[11],
                'drsActivationDistance': data[12],
                'actualTyreCompound': data[13],
                'visualTyreCompound': data[14],
                'tyresAgeLaps': data[15],
                'vehicleFiaFlags': data[16],
                'enginePowerICE': data[17],
                'enginePowerMGUK': data[18],
                'ersStoreEnergy': data[19],
                'ersDeployMode': data[20]
            }]
        }
    
    def parse_participants(self, header: PacketHeader, buffer: bytes, *_):
        num_active_cars = struct.unpack_from('<B', buffer, HEADER_SIZE)[0]
        participant_format = '<BBBBBBB32sBBHB4B'
        participant_size = struct.calcsize(participant_format)
        participants = []
        for i in range(22):
            offset = HEADER_SIZE + 1 + i * participant_size
            data = struct.unpack_from(participant_format, buffer, offset)
            participants.append({
                'aiControlled': data[0],
                'driverId': data[1],
                'networkId': data[2],
                'teamId': data[3],
                'myTeam': data[4],
                'raceNumber': data[5],
                'nationality': data[6],
                'name': data[7].decode('utf-8', errors='ignore').strip('\x00'),
                'yourTelemetry': data[8],
                'showOnlineNames': data[9],
                'techLevel': data[10],
                'platform': data[11],
                'numColours': data[12],
                'liveryColours': list(data[13:17])
            })
        return {'header': header, 'numActiveCars': num_active_cars, 'participants': participants}

    def parse_event(self, header: PacketHeader, buffer: bytes, *_):
        event_code = struct.unpack_from('<4s', buffer, HEADER_SIZE)[0].decode('utf-8')
        return {'header': header, 'eventCode': event_code}

    def parse_final_classification(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        class_format = '<BBBBBBIdBBB8B8B8B'
        class_size = struct.calcsize(class_format)
        offset = HEADER_SIZE + 1 + car_index * class_size
        num_cars = struct.unpack_from('<B', buffer, HEADER_SIZE)[0]
        data = struct.unpack_from(class_format, buffer, offset)
        return {
            'header': header,
            'numCars': num_cars,
            'classificationData': [{
                'position': data[0],
                'numLaps': data[1],
                'gridPosition': data[2],
                'points': data[3],
                'numPitStops': data[4],
                'resultStatus': data[5],
                'resultReason': data[6],
                'bestLapTimeInMS': data[7],
                'totalRaceTime': data[8],
                'penaltiesTime': data[9],
                'numPenalties': data[10],
                'numTyreStints': data[11],
                'tyreStintsActual': list(data[12:20]),
                'tyreStintsVisual': list(data[20:28]),
                'tyreStintsEndLaps': list(data[28:36])
            }]
        }

    def parse_car_damage(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        car_format = '<4f4B4B3B6B2B8B2B'
        car_size = struct.calcsize(car_format)
        offset = HEADER_SIZE + car_index * car_size
        data = struct.unpack_from(car_format, buffer, offset)
        return {
            'header': header,
            'carDamageData': [{
                'tyresWear': list(data[0:4]),
                'tyresDamage': list(data[4:8]),
                'brakesDamage': list(data[8:12]),
                'tyreBlisters': list(data[12:15]),
                'frontLeftWingDamage': data[15],
                'frontRightWingDamage': data[16],
                'rearWingDamage': data[17],
                'floorDamage': data[18],
                'diffuserDamage': data[19],
                'sidepodDamage': data[20],
                'drsFault': data[21],
                'ersFault': data[22],
                'gearBoxDamage': data[23],
                'engineDamage': data[24],
                'engineMGUHWear': data[25],
                'engineESWear': data[26],
                'engineCEWear': data[27],
                'engineICEWear': data[28],
                'engineMGUKWear': data[29],
                'engineTCWear': data[30],
                'engineBlown': data[31],
                'engineSeized': data[32]
            }]
        }

    def parse_session_history(self, header: PacketHeader, buffer: bytes, *_):
        car_idx, num_laps, num_stints, best_lap, best_s1, best_s2, best_s3 = struct.unpack_from('<BBBBBBB', buffer, HEADER_SIZE)
        lap_data_format = '<I H B H B H B B'
        lap_data_size = struct.calcsize(lap_data_format)
        lap_offset = HEADER_SIZE + 7

        laps = [
            dict(zip([
                'lapTimeInMS', 'sector1MS', 'sector1Min', 'sector2MS', 'sector2Min',
                'sector3MS', 'sector3Min', 'lapValidFlags'
            ], struct.unpack_from(lap_data_format, buffer, lap_offset + i * lap_data_size)))
            for i in range(100)
        ]

        stint_format = '<BBB'
        stint_offset = lap_offset + 100 * lap_data_size
        stints = [
            dict(zip(['endLap', 'actualTyre', 'visualTyre'],
                     struct.unpack_from(stint_format, buffer, stint_offset + i * 3)))
            for i in range(8)
        ]

        return {
            'header': header,
            'carIdx': car_idx,
            'numLaps': num_laps,
            'numTyreStints': num_stints,
            'bestLapTimeLapNum': best_lap,
            'bestSector1LapNum': best_s1,
            'bestSector2LapNum': best_s2,
            'bestSector3LapNum': best_s3,
            'lapHistoryData': laps,
            'tyreStintsHistoryData': stints
        }


    def parse_tyre_sets(self, header: PacketHeader, buffer: bytes, car_index: int = 0):
        tyre_format = '<BBBBBBBhB'
        tyre_size = struct.calcsize(tyre_format)
        offset = HEADER_SIZE + 1 + car_index * tyre_size
        car_idx = struct.unpack_from('<B', buffer, HEADER_SIZE)[0]
        data = struct.unpack_from(tyre_format, buffer, offset)
        return {
            'header': header,
            'carIdx': car_idx,
            'tyreSetData': [{
                'actualCompound': data[0],
                'visualCompound': data[1],
                'wear': data[2],
                'available': data[3],
                'recommendedSession': data[4],
                'lifeSpan': data[5],
                'usableLife': data[6],
                'lapDeltaTime': data[7],
                'fitted': data[8]
            }],
            'fittedIdx': data[8]
        }

    def parse_motion_ex(self, header: PacketHeader, buffer: bytes, *_):
        format_str = '<' + 'f'*88  # 88 floats
        expected_size = HEADER_SIZE + struct.calcsize(format_str)

        if len(buffer) < expected_size:
            #print(f"Skipping packet due to error: MotionEx packet too short: expected {expected_size}, got {len(buffer)}")
            return {'header': header, 'motionEx': []}

        data = struct.unpack_from(format_str, buffer, HEADER_SIZE)
        return {
            'header': header,
            'motionEx': list(data)
        }

    def parse_time_trial(self, header: PacketHeader, buffer: bytes, *_):
        car_format = '<B B 4I 5B'
        section_size = struct.calcsize(car_format)
        result = {'header': header}
        for i, name in enumerate(['playerSessionBest', 'personalBest', 'rival']):
            offset = HEADER_SIZE + i * section_size
            d = struct.unpack_from(car_format, buffer, offset)
            result[name] = {
                'carIdx': d[0],
                'teamId': d[1],
                'lapTime': d[2],
                's1Time': d[3],
                's2Time': d[4],
                's3Time': d[5],
                'tractionControl': d[6],
                'gearboxAssist': d[7],
                'antiLockBrakes': d[8],
                'equalCarPerformance': d[9],
                'customSetup': d[10],
                'valid': d[11]
            }
        return result

    def parse_lap_positions(self, header: PacketHeader, buffer: bytes, *_):
        num_laps, lap_start = struct.unpack_from('<BB', buffer, HEADER_SIZE)
        base = HEADER_SIZE + 2
        positions = [
            list(struct.unpack_from('22B', buffer, base + i * 22)) for i in range(50)
        ]
        return {
            'header': header,
            'numLaps': num_laps,
            'lapStart': lap_start,
            'positionForVehicleIdx': positions
        }