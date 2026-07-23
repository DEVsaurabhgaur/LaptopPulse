from typing import List, Dict
def filter_top_processes(processes: List[Dict], top_n: int = 5) -> List[Dict]:
    return sorted(processes, key=lambda x: x.get('cpu_percent', 0), reverse=True)[:top_n]
