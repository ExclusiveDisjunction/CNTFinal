import json
from pathlib import Path
from dataclasses import dataclass

@dataclass
class TransferStats:
    file_size: int
    transfer_time: float
    data_rate: float
    latency: float
    ip: str

class NetworkAnalyzer:
    def __init__(self):
        self.stats_file = None
        self.stats: list[TransferStats] = None

    def open(self, path: Path):
        self.stats_file = path
        
        try:
            with open(self.stats_file, 'r') as f:
                contents = f.read()
                if contents is None or len(contents) == 0:
                    contents = "[]"

                data = json.loads(contents)
                self.stats = data
        except (FileNotFoundError, json.JSONDecodeError):
            self.stats = []

    # Saves statistics to file
    def save(self):
        with open(self.stats_file, 'w') as f:
            # Convert TransferStats objects to dictionaries
            data =  [
                        {
                            "file_size": stat.file_size,
                            "transfer_time": stat.transfer_time,
                            "data_rate": stat.data_rate,
                            "latency": stat.latency,
                            "ip": stat.ip,
                        }
                        for stat in self.stats
                    ]
            json.dump(data, f)

    # Records statistics for a file transfer
    def record_transfer(self, file_size: int, start_time: float, end_time: float, ip: str) -> None:
        time = end_time - start_time
        rate = NetworkAnalyzer._calculate_data_rate(file_size, time)
        latency = 1 / time

        stat = TransferStats(
            file_size = file_size,
            transfer_time = time,
            data_rate = rate,
            latency = latency,
            ip = ip
        )

        self.stats.append(stat)

    def get_ip_stats(self, ip: str) -> list[TransferStats]:
        return [stat for stat in self.stats if stat.ip == ip]
    def get_last_ip_stats(self, ip: str) -> TransferStats | None:
        ip_stats = self.get_ip_stats(ip)
        return ip_stats[-1] if ip_stats else None

    # Calculates data rate in MB/s
    def _calculate_data_rate(file_size: int, transfer_time: float) -> float:
        if transfer_time > 0:
            return (file_size / transfer_time) / 1e6  # Convert to MB/s
        return 0.0

# Global instance
network_analyzer = NetworkAnalyzer()