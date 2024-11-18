import Server.pool as pool
<<<<<<< HEAD
from Server.io_tools import ensure_root_directory
=======
from Server.io_tools import ensure_root_directory, file_owner_db
>>>>>>> server-branch
from Server.credentials import user_database

threadPool = pool.ThreadPool()

print("Ensuring root directory exists...")
if not ensure_root_directory():
    print("Could not establish root directory. Aborting.")
    quit(1)
else:
    print("Root directory established/already exists")

port = 8081
ip = "127.0.0.1"

print(f"Setting up thread pool, binding on port {port}")
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
<<<<<<< HEAD
=======
file_owner_db.save()
>>>>>>> server-branch
print("Goodbye!")