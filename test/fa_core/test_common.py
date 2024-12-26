from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from fa_core.common import get_session_id


def test_get_session_id():
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(tqdm(executor.map(lambda _: get_session_id(), range(100)), total=100, desc="running tasks"))
    print(f"unique session_ids: {len(set(results))} / {len(results)}")
    print()


test_get_session_id()
