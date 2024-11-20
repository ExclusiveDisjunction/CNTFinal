from pathlib import Path

host_directory = (Path.home() / "cnt").resolve()
root_directory = host_directory / "data"
user_database_loc = host_directory / "files.json"
file_owner_db_path = host_directory / "files.json"
network_analyzer_path = host_directory / "stats.json"

def ensure_directories() -> bool:
    global root_directory
    global host_directory
    global user_database_loc
    global file_owner_db_path
    
    try:
        if not host_directory.exists():
            host_directory.mkdir(parents=True, exist_ok=True)
            root_directory.mkdir(parents=True, exist_ok=True)
            if not user_database_loc.exists():
                user_database_loc.touch(exist_ok=True)
            
            if not file_owner_db_path.exists():
                file_owner_db_path.touch(exist_ok=True)

            if not network_analyzer_path.exists():
                network_analyzer_path.touch(exist_ok=True)
  
        return True
    except:
        return False