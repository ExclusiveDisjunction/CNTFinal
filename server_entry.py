import Server.pool as pool
from Server.server_paths import ensure_directories, file_owner_db_path, user_database_loc
from Server.io_tools import file_owner_db, FileOwnerDB
from Server.credentials import user_database, UserDatabase

import socket

print("Ensuring root directory exists...")
if not ensure_directories():
    print("Could not establish root directory. Aborting.")
    quit(1)
else:
    print("Root directory established/already exists")

threadPool = pool.ThreadPool()
user_database = UserDatabase(user_database_loc)
file_owner_db = FileOwnerDB(file_owner_db_path)

hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
port = 61324

print(f"Setting up thread pool, binding on port {port} with IP {ip}")
try:
    threadPool.bind(port, ip)
    threadPool.listen()
    print("Entering main loop...\n")
    threadPool.mainLoop()

except KeyboardInterrupt:
    print(f"Keyboard interupt")
except OSError as e:
    print(f"OS Exception: {str(e)}")
except Exception as e:
    print(f"Unknown exception caught: {str(e)}")
finally:
    print(f"Shutting down thread pool")
    threadPool.kill()
    
user_database.save()
file_owner_db.save()
print("Goodbye!")