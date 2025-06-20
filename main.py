
from telemetry_gui import TelemetryGUI
from listener import udp_listener
import threading

if __name__ == '__main__':
    gui = TelemetryGUI()
    threading.Thread(target=udp_listener, args=(gui,), daemon=True).start()
    gui.run()
