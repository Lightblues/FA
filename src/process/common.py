from pathlib import Path

class DirectoryManager:
    def __init__(self):
        _file_dir_path = Path(__file__).resolve().parent
        _dir_data_base = (_file_dir_path / "../../data/gen").resolve()
        _dir_data_output = (_file_dir_path / "../../data/v240628").resolve()
        
        self.DIR_data_base = _dir_data_base
        self.DIR_data_meta = _dir_data_base / "huabu_meta"
        self.FN_data_meta = _dir_data_base / "meta/data_meta.json"
        self.FN_data_meta_en = _dir_data_base / "meta/data_meta_en.json"
        self.FN_data_meta_extension = _dir_data_base / "meta/data_meta_extension.jsonl"
        
        self.DIR_data_output = _dir_data_output

_DIRECTORY_MANAGER = DirectoryManager()