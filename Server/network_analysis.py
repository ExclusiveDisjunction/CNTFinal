import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TransferStats:
    file_size: int
    transfer_time: float
    data_rate: float
    latency: float
    transfer_type: str # 'upload' or 'download'

class NetworkAnalyzer:
    def __init__(self, stats_file: str = "network_stats.json"):
        self.stats_file = stats_file
        self.stats: Dict[str, list[TransferStats]] = {
            "transfers": []
        }
        self._load_stats()

    # Loads existing statistics from file if it exists
    def _load_stats(self):
        try:
            with open(self.stats_file, 'r') as f:
                data = json.load(f)
                # Convert dictionary data back to TransferStats objects
                self.stats["transfers"] = [
                    TransferStats(**transfer) for transfer in data["transfers"]
                ]
        except (FileNotFoundError, json.JSONDecodeError):
            self.stats = {"transfers": []}

    # Saves statistics to file
    def save_stats(self):
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
        self.save_stats()
        return stat.__dict__

    # Calculates data rate in MB/s
    def _calculate_data_rate(self, file_size: int, transfer_time: float) -> float:
        if transfer_time > 0:
            return (file_size / transfer_time) / 1e6  # Convert to MB/s
        return 0.0

    # Calculates average statistics
    def get_average_stats(self) -> Dict[str, Any]:
        if not self.stats["transfers"]:
            return {
                "avg_data_rate": 0,
                "avg_transfer_time": 0,
                "avg_latency": 0 
            }

        transfers = self.stats["transfers"]
        avg_data_rate = sum(t.data_rate for t in transfers) / len(transfers)
        avg_transfer_time = sum(t.transfer_time for t in transfers) / len(transfers)
        avg_latency = sum(t.latency for t in transfers) / len(transfers)

        return {
            "avg_data_rate": avg_data_rate,
            "avg_transfer_time": avg_transfer_time,
            "avg_latency": avg_latency 
        }

# Global instance
network_analyzer = NetworkAnalyzer()