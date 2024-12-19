from pathlib import Path

import yaml


class YAMLIncludeLoader(yaml.SafeLoader):
    def __init__(self, stream):
        self._root = Path(stream.name).parent
        self._included_files = set()  # 防止循环引用
        super().__init__(stream)

    def include(self, node):
        filename = self.construct_scalar(node)
        filepath = self._root / filename

        # 检查循环引用
        if str(filepath) in self._included_files:
            raise yaml.constructor.ConstructorError(
                "while including file",
                node.start_mark,
                f"circular include detected for file {filename}",
                node.start_mark,
            )

        self._included_files.add(str(filepath))

        try:
            with open(filepath, "r") as f:
                data = yaml.load(f, Loader=YAMLIncludeLoader)
                if not isinstance(data, dict):
                    raise yaml.constructor.ConstructorError(
                        "while including file",
                        node.start_mark,
                        f"expected a mapping, but found {type(data)}",
                        node.start_mark,
                    )
                return data
        finally:
            self._included_files.remove(str(filepath))

    def construct_document(self, node):
        """重写构造文档的方法，处理多个配置文件的合并"""
        data = super().construct_document(node)
        if isinstance(data, dict):
            # 处理 defaults 列表
            if "defaults" in data:
                defaults = data.pop("defaults")
                if isinstance(defaults, list):
                    merged = {}
                    for default in defaults:
                        if isinstance(default, str):
                            filepath = self._root / default
                            with open(filepath, "r") as f:
                                default_data = yaml.load(f, Loader=YAMLIncludeLoader)
                        elif isinstance(default, dict):
                            default_data = default
                        else:
                            continue
                        merged.update(default_data)
                    data = {**merged, **data}
                elif isinstance(defaults, (str, dict)):
                    if isinstance(defaults, str):
                        filepath = self._root / defaults
                        with open(filepath, "r") as f:
                            default_data = yaml.load(f, Loader=YAMLIncludeLoader)
                    else:
                        default_data = defaults
                    data = {**default_data, **data}
        return data


YAMLIncludeLoader.add_constructor("!include", YAMLIncludeLoader.include)


class YAMLLoader:
    """Customized YAML Loader with !include support

    This loader adds support for including other YAML files using the !include tag.
    It also supports merging multiple config files using the 'defaults' key.

    Example YAML config:

    ```yaml
        # customized.yaml
        # --- option 1
        defaults: !include default.yaml

        # --- option 2
        defaults:
          - default.yaml
          - env: dev

    ```

    Usage:
        config = YAMLLoader.load_yaml("customized.yaml")
    """

    @staticmethod
    def load_yaml(yaml_file: str | Path) -> dict:
        yaml_path = Path(yaml_file)
        if not yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {yaml_file}")

        with open(yaml_path, "r") as f:
            return yaml.load(f, Loader=YAMLIncludeLoader)

    @staticmethod
    def save_yaml(data: dict, yaml_file: str | Path) -> None:
        yaml_path = Path(yaml_file)
        yaml_path.parent.mkdir(parents=True, exist_ok=True)

        with open(yaml_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
