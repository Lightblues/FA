""" collect analyer results """
import itertools
import pandas as pd
from flowagent import Config, DataManager, Judger, Analyzer

if __name__ == '__main__':
    results = []
    model = "Qwen2-72B"
    selected_formats = ['text', 'code', 'flowchart', 'pdl-pdl']
    selected_datasets = ['sgd', 'pdl', 'star']
    for format, dataset in itertools.product(selected_formats, selected_datasets):
        exp_version = f"turn_{dataset}_{format}_{model}"
        print(f">> rejudging: {exp_version}")
        
        cfg = Config.from_yaml(DataManager.normalize_config_name("default.yaml"))
        cfg.judge_force_rejudge = True  # force rejudge
        cfg.exp_version = exp_version
        cfg.exp_mode = "turn"
        cfg.workflow_dataset = dataset.upper()
        cfg.workflow_type = format if (not format.startswith("pdl")) else 'pdl'
        cfg.judge_log_to = None # not to wandb

        analyzer = Analyzer(cfg)
        out = analyzer.analyze()
        out['exp_version'] = exp_version
        results.append(out)
    results_df = pd.DataFrame(results) #.set_index('exp_version')
    results_df.sort_values(by=['exp_version'], inplace=True)
    seleted_df = results_df[['passrate', 'f1', 'oow_passrate', 'exp_version']].set_index('exp_version')
    print(seleted_df)
