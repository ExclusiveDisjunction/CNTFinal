import Server.pool as pool
from Server.server_paths import ensure_directories, file_owner_db_path, user_database_loc, network_analyzer_path
from Server.io_tools import file_owner_db, FileOwnerDB
from Server.credentials import user_database, UserDatabase
from Server.network_analysis import network_analyzer

import socket

print("Ensuring root directory exists...")
if not ensure_directories():
    print("Could not establish root directory. Aborting.")
    quit(1)
else:
    print("Root directory established/already exists")

threadPool = pool.ThreadPool()
user_database.open(user_database_loc)
file_owner_db.open(file_owner_db_path)
network_analyzer.open(network_analyzer_path)

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)

port_raw = int(input("Port? (0 for default)"))
if port_raw == 0:
    port = 61324
else:
    port = port_raw

print(f"Setting up thread pool, binding on port {port} with IP {ip}")
try:
    threadPool.bind(port, ip)
    threadPool.listen()
    print("Entering main loop...\n")
    threadPool.mainLoop()
except KeyboardInterrupt:
    print(f"\n[CONTROL] Keyboard Interupt")
except OSError as e:
    print(f"[CONTROL] OS Exception: {str(e)}")
except Exception as e:
    print(f"[CONTROL] Unknown exception caught: {str(e)}")
finally:
    print(f"[CONTROL] Terminating thread pool")
    threadPool.kill()
    
user_database.save()
file_owner_db.save()
network_analyzer.save()
print("Goodbye!")