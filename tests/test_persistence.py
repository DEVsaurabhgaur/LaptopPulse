from src.core.state_persistence import save_state
import os
def test_save(tmp_path):
    p = str(tmp_path / 'test.json')
    save_state(p, {'status': 'ok'})
    assert os.path.exists(p)
