"""collect analyer results"""

import itertools

import pandas as pd

from flowagent import Analyzer, Config, DataManager


MODE2MATRICS = {
    "session": ["success_rate", "task_progress", "f1", "exp_version"],
    "turn": [
        "passrate",
        "f1",
        "para_f1",
        "oow_passrate",
        "oow_f1",
        "oow_para_f1",
        "exp_version",
    ],
}


def analyze_exp(configs: list, prefix="sessionOOW_", exp_mode: str = "session"):
    results = []
    for format, dataset, model in configs:
        exp_version = f"{prefix}{dataset}_{format}_{model}"
        print(f">> exp_version: {exp_version}")

        cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
        cfg.exp_version = exp_version
        cfg.exp_mode = exp_mode  # fix
        cfg.workflow_dataset = dataset.upper()
        cfg.workflow_type = format if (not format.startswith("pdl")) else "pdl"
        cfg.judge_log_to = None  # not to wandb

        analyzer = Analyzer(cfg)
        out = analyzer.analyze()
        if out is not None:
            out["exp_version"] = exp_version
            results.append(out)
    results_df = pd.DataFrame(results)  # .set_index('exp_version')
    results_df.sort_values(by=["exp_version"], inplace=True)
    seleted_df = results_df[MODE2MATRICS[exp_mode]].set_index("exp_version")
    return seleted_df


if __name__ == "__main__":
    # models = ['gpt-4o', 'gpt-4o-mini']  # "Qwen2-72B",
    models = ["Qwen2-72B"]
    selected_formats = ["text", "code", "flowchart", "pdl-pdl"]
    selected_datasets = ["sgd", "pdl", "star"]
    configs = itertools.product(selected_formats, selected_datasets, models)

    # res = analyze_exp(configs, prefix="sessionOOW_")
    # res = analyze_exp(configs, prefix="")
    res = analyze_exp(configs, prefix="turn_", exp_mode="turn")
    print(res)
    print()
