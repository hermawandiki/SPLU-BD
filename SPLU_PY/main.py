from src.charge_point import OfflineOperation
from src.modbus import read_power_meter, timeout_relay, client
import time
import asyncio
import tkinter as tk
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
import threading
from mfrc522 import SimpleMFRC522
import logging
import os
from datetime import datetime

GPIO.setwarnings(False)

CHARGEBOXID = "BDTEST1"
WS_ADDRESS = "wss://ocpp.bambangdjaja.com/ws/BDTEST5"
EMERGENCY_PIN = 29
CTRATIO = 4
ws_connected = None
offline = OfflineOperation()
READ_COOLDOWN = 3.0
last_card_id = None
last_read_time = 0
MAX_CONNECTORS = 6

active_cards = {}
available_connectors = set(range(MAX_CONNECTORS))
NO_CURRENT_TIMEOUT = 30
CURRENT_THRESHOLD = 0
last_current_time = {}
start_kwh = {}
last_session_kwh = {}

log_dir = "log"
os.makedirs(log_dir, exist_ok=True)
log_date = datetime.now().strftime("%d%m%Y")
log_file = os.path.join(log_dir, f"log-{log_date}.txt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(
            log_file,
            encoding="utf-8"
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Logging started: {log_file}")

def assign_connector() -> int | None:
    if not available_connectors:
        return None
    return min(available_connectors)

async def handle_rfid(card_id):
    global active_cards, available_connectors

    if card_id in active_cards:
        connector_id = active_cards.pop(card_id)
        available_connectors.add(connector_id)

        last_current_time.pop(connector_id, None)

        kwh_now = read_power_meter(connector_id + 1, 4, CTRATIO)
        kwh_start = start_kwh.get(connector_id, kwh_now)
        last_session_kwh[connector_id] = max(0, kwh_now - kwh_start)

        start_kwh.pop(connector_id, None)
        print(f"[STOP] RFID {card_id} ? Relay {connector_id + 1}")
        logger.info(f"[STOP] RFID {card_id} -> Relay {connector_id + 1}")
        await offline.local_stop(connector_id)
    else:
        connector_id = assign_connector()
        if connector_id is None:
            print("[ERROR] No connector available")
            logger.error("[ERROR] No connector available")
            return

        active_cards[card_id] = connector_id
        available_connectors.remove(connector_id)
        last_current_time[connector_id] = time.time()

        print(f"[START] RFID {card_id} ? Relay {connector_id + 1}")
        logger.info(f"[START] RFID {card_id} -> Relay {connector_id + 1}")

        kwh_now = read_power_meter(connector_id + 1, 4, CTRATIO)
        start_kwh[connector_id] = kwh_now

        await offline.local_start(connector_id)

async def monitor_idle_connectors():
    while True:
        now = time.time()

        for card_id, connector_id in list(active_cards.items()):
            try:
                current = timeout_relay(connector_id + 1, CTRATIO)
                if current > CURRENT_THRESHOLD:
                    last_current_time[connector_id] = now
                else:
                    last_seen = last_current_time.get(connector_id, now)
                    idle_time = now - last_seen

                    if idle_time >= NO_CURRENT_TIMEOUT:
                        print(f"[AUTO OFF] Connector {connector_id + 1} idle {idle_time:.0f}s")
                        logger.info(f"[AUTO OFF] Connector {connector_id + 1} idle {idle_time:.0f}s")
                        await offline.local_stop(connector_id)

                        active_cards.pop(card_id, None)
                        available_connectors.add(connector_id)
                        last_current_time.pop(connector_id, None)
                        start_kwh.pop(connector_id, None)
            except Exception as e:
                print("[AUTO OFF ERROR]", e)
                logger.error(f"[AUTO OFF ERROR] {e}", exc_info=True)
        await asyncio.sleep(1)

async def main():
    global last_card_id, last_read_time
    rfid = SimpleMFRC522()
    try:
        await offline.all_off()
    except Exception as e:
        print("[ERROR] Failed to turn off all relays:", e)
        logger.error(f"[ERROR] Failed to turn off all relays: {e}", exc_info=True)

    while True:
        try:
            print("Please Tap RFID Card...")
            logger.info("Please Tap RFID Card...")
            # rfid = SimpleMFRC522()
            card_id, text = rfid.read()
            now = time.time()

            if card_id == last_card_id and (now - last_read_time) < READ_COOLDOWN:
                await asyncio.sleep(2)
                continue

            last_card_id = card_id
            last_read_time = now

            print("UID:", card_id)
            logger.info(f"UID: {card_id}")
            await handle_rfid(card_id)

            print(active_cards)
        except Exception as e:
            print("RFID error:", e)
            logger.error(f"RFID error: {e}")
            await asyncio.sleep(1)

def show_gui():
    global ws_connected, available_connectors
    master = tk.Tk()
    master.geometry("800x450")

    master_frame = tk.Frame(master)
    master_frame.place(relx=0.5, rely=0.5, anchor="c")

    img = Image.open("/home/admin/SPLU_PY/logo.jpeg")
    img = img.resize((35, 35), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)

    header = tk.Frame(master_frame, borderwidth=0, relief="solid", height=40, bg="red")
    g_1 = tk.Frame(master_frame, borderwidth=2, relief="solid", width=266, height=140)
    g_2 = tk.Frame(master_frame, borderwidth=2, relief="solid", width=266, height=140)
    g_3 = tk.Frame(master_frame, borderwidth=2, relief="solid", width=266, height=140)
    g_4 = tk.Frame(master_frame, borderwidth=2, relief="solid", width=266, height=140)
    g_5 = tk.Frame(master_frame, borderwidth=2, relief="solid", width=266, height=140)
    g_6 = tk.Frame(master_frame, borderwidth=2, relief="solid", width=266, height=140)
    footer = tk.Frame(master_frame, borderwidth=0, relief="solid", height=20, bg="red")

    header.grid(row=0, columnspan=6)
    g_1.grid(row=1, column=0, padx=6.5, pady=(6.5, 6.5))
    g_2.grid(row=1, column=1, padx=6.5, pady=(6.5, 6.5))
    g_3.grid(row=1, column=2, padx=6.5, pady=(6.5, 6.5))
    g_4.grid(row=2, column=0, padx=6.5, pady=(6.5, 6.5))
    g_5.grid(row=2, column=1, padx=6.5, pady=(6.5, 6.5))
    g_6.grid(row=2, column=2, padx=6.5, pady=(6.5, 6.5))
    footer.grid(row=3, columnspan=6)

    grids = [g_1, g_2, g_3, g_4, g_5, g_6]

    img_label = tk.Label(header, image=img, height=40, width=50, bd=-2, anchor='w')
    img_label.grid(row=0, column=0, sticky='nswe')

    header_label = tk.Label(header, text="Bambang Djaja SPLU BDTEST1", font=("Arial", 22), height=1, bd=-2)
    header_label.grid(row=0, column=1, sticky='nswe', columnspan=5)

    status_on_off = []
    status_available = []
    kwh_values = []
    vol_values = []
    curr_values = []

    connected_to = tk.StringVar()

    for p in range(len(grids)):
        status_on_off.append(tk.StringVar())
        status_available.append(tk.StringVar())
        kwh_values.append(tk.StringVar())
        vol_values.append(tk.StringVar())
        curr_values.append(tk.StringVar())

    for j in range(len(status_available)):
        connector_id = j
        print(f"Init Connector {connector_id}")
        if(int(read_power_meter(j + 1, 0, CTRATIO)) > 200):
            status_on_off[j].set(": ON")
        else:
            status_on_off[j].set(": OFF")

        if connector_id in available_connectors:
            status_available[j].set("AVAILABLE")
        else:
            status_available[j].set("IN USE")

        # kwh_values[j].set(": {}".format((read_power_meter(j + 1, 4, CTRATIO))))
        # vol_values[j].set(": {}".format((read_power_meter(j + 1, 0, CTRATIO))))
        # curr_values[j].set(": {}".format((read_power_meter(j + 1, 1, CTRATIO))))

        kwh_values[j].set(": 0")
        vol_values[j].set(": 0")
        curr_values[j].set(": 0")

    COLS = 3
    for i, grid in enumerate(grids):
        if i < COLS:
            connector_num = 2 * i + 1
        else:
            connector_num = 2 * (i - COLS) + 2

        connector = tk.Label(
            grid,
            text=f"CONNECTOR {connector_num}",
            font=("Arial", 14),
            width=22,
            height=1,
            bd=-2
        )
        connector.grid(row=0, column=0, sticky='nswe', columnspan=2)
        connector.config(bg="white")

        available = tk.Label(grid, textvariable=status_available[i], font=("Arial", 14), width=22, height=1)
        available.grid(row=1, column=0, sticky='nswe', columnspan=2)
        available.config(bg="white")

        status_connector = tk.Label(grid, text="Status", font=("Arial", 14), width=11, height=1, anchor='w')
        status_connector.grid(row=2, column=0, sticky='nswe')

        status_connector_value = tk.Label(grid, textvariable=status_on_off[i], font=("Arial", 14), width=11, height=1, anchor='w')
        status_connector_value.grid(row=2, column=1, sticky='nswe')

        kwh = tk.Label(grid, text="KWh", font=("Arial", 14), width=11, height=1, anchor='w')
        kwh.grid(row=3, column=0, sticky='nswe')

        kwh_value = tk.Label(grid, textvariable=kwh_values[i], font=("Arial", 14), width=11, height=1, anchor='w')
        kwh_value.grid(row=3, column=1, sticky='nswe')

        voltage = tk.Label(grid, text="Voltage", font=("Arial", 14), width=11, height=1, anchor='w')
        voltage.grid(row=4, column=0, sticky='nswe')

        voltage_value = tk.Label(grid, textvariable=vol_values[i], font=("Arial", 14), width=11, height=1, anchor='w')
        voltage_value.grid(row=4, column=1, sticky='nswe')

        current = tk.Label(grid, text="Current", font=("Arial", 14), width=11, height=1, anchor='w')
        current.grid(row=5, column=0, sticky='nswe')

        current_value = tk.Label(grid, textvariable=curr_values[i], font=("Arial", 14), width=11, height=1, anchor='w')
        current_value.grid(row=5, column=1, sticky='nswe')

    current_ws = tk.Label(footer,
                          textvariable=connected_to,
                          font=("Arial", 14),
                          height=1
                        )

    current_ws.grid(row=6, sticky='nswe', columnspan=2)
    # master.attributes('-fullscreen', True)
    print("Initialized")

    def update_gui():
        if ws_connected is not None:
            connected_to.set(f"Connected to: {ws_connected}")
        else:
            connected_to.set("Offline (Not Connected)")

        for x in range(len(status_available)):
            connector_id = x

            if int(read_power_meter(x + 1, 0, CTRATIO)) > 200:
                status_on_off[x].set(": ON")
            else:
                status_on_off[x].set(": OFF")

            if connector_id in available_connectors:
                status_available[x].set("AVAILABLE")
            else:
                status_available[x].set("IN USE")

            kwh_now = read_power_meter(x + 1, 4, CTRATIO)

            if x in start_kwh:
                kwh_display = max(0, kwh_now - start_kwh[x])
            else:
                kwh_display = last_session_kwh.get(x, 0)

            kwh_values[x].set(f": {kwh_display:.2f}")
            vol_values[x].set(f": {(read_power_meter(x + 1, 0, CTRATIO))}")
            curr_values[x].set(f": {(read_power_meter(x + 1, 1, CTRATIO))}")

        master.after(1000, update_gui)

    update_gui()
    master.mainloop()

def start_main():
    logger.info("Start main loop")
    asyncio.run(main())

def start_monitor_idle_connectors():
    logger.info("Start monitor idle connector loop")
    asyncio.run(monitor_idle_connectors())

if __name__ == "__main__":
    try:
        threading.Thread(target=start_main, daemon=True).start()
        threading.Thread(target=start_monitor_idle_connectors, daemon=True).start()
        logger.info("Start GUI loop")
        show_gui()
    except KeyboardInterrupt:
        print('Interrupted')
        logger.info("Interrupted")
    finally:
        print('Cleaning up...')
        logger.info("Cleaning up...")
        # GPIO.cleanup()
        client.close()
