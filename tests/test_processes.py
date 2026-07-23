from src.core.process_filter import filter_top_processes
def test_filter():
    procs = [{'pid': 1, 'cpu_percent': 10}, {'pid': 2, 'cpu_percent': 50}]
    top = filter_top_processes(procs, 1)
    assert top[0]['pid'] == 2
