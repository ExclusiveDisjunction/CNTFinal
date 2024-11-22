import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TransferStats:
    file_size: int
    transfer_time: float
    data_rate: float
    latency: float
    transfer_type: str # 'upload' or 'download'

class NetworkAnalyzer:
    def __init__(self):
        self.stats_file = None
        self.stats = None

    def open(self, path: Path):
        self.stats_file = path
        self.stats = { 
            "transfers": []
        }
        self._load_stats()

    # Loads existing statistics from file if it exists
    def _load_stats(self):
        try:
            with open(self.stats_file, 'r') as f:
                contents = f.read()
                if contents is None or len(contents.strip()) == 0:
                    self.stats = {"transfers": []}
                    return

                data = json.loads(contents)

                # Handle the case where data does not have transfer key
                if "transfers" not in data:
                    data["transfers"] = []

                # Convert dictionary data back to TransferStats objects
                self.stats["transfers"] = [
                    TransferStats(**transfer) for transfer in data["transfers"]
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self.stats = {"transfers": []}

    # Saves statistics to file
    def save(self):
        with open(self.stats_file, 'w') as f:
            # Convert TransferStats objects to dictionaries
            data = {
                "transfers": [
                    {
                        "file_size": stat.file_size,
                        "transfer_time": stat.transfer_time,
                        "data_rate": stat.data_rate,
                        "latency": stat.latency,
                        "transfer_type": stat.transfer_type,
                    }
                    for stat in self.stats["transfers"]
                ]
            }
            json.dump(data, f, indent=2)

    # Records statistics for a file transfer
    def record_transfer(self, file_size: int, start_time: float, end_time: float, 
                       latency: float, transfer_type: str):
        transfer_time = end_time - start_time
        data_rate = self._calculate_data_rate(file_size, transfer_time)
        
        stat = TransferStats(
            file_size=file_size,
            transfer_time=transfer_time,
            data_rate=data_rate,
            latency=latency,
            transfer_type=transfer_type,
        )
        
        self.stats["transfers"].append(stat)
        return stat.__dict__
    
    def get_last_transfer(self) -> TransferStats | None:
        """
        Gets the last transfer statistics out of the current instance
        """
        if len(self.stats["transfers"]):
            return None
        else:
            return self.stats["transfers"][-1]

    # Calculates data rate in MB/s
    def _calculate_data_rate(self, file_size: int, transfer_time: float) -> float:
        if transfer_time > 0:
            return (file_size / transfer_time) / 1e6  # Convert to MB/s
        return 0.0

# Global instance
network_analyzer = NetworkAnalyzer()