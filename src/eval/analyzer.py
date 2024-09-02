import collections
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Analyzer:
    df: pd.DataFrame = None
    output_dir: str = "."
    def __init__(self, df: pd.DataFrame, output_dir: str) -> None:
        df["num_rounds"] = df["judge_result"].apply(lambda x: len(x["detailed"]))
        df['overall_score'] = df['judge_result'].apply(lambda x: x["overall"]["score"])
        self.df = df
        self.output_dir = output_dir

    def stat_num_rounds(self):
        avg_conv_turns = self.df["num_rounds"].mean()
        print(f"avg num rounds: {avg_conv_turns:.2f}")
        
        vc_num_rounds = self.df["num_rounds"].value_counts().sort_index().reset_index()
        plt.figure(figsize=(10, 6))
        sns.barplot(x='num_rounds', y='count', data=vc_num_rounds, palette='Blues_d', hue='num_rounds', legend=False)
        # plt.bar(vc_num_rounds['num_rounds'].values, vc_num_rounds['count'].values, color='blue')
        plt.title('Number of Rounds Distribution')
        plt.xlabel('Number of Rounds')
        plt.ylabel('Count')
        plt.savefig(f"{self.output_dir}/stat_num_rounds.png")
        print(f"Saved to {self.output_dir}/stat_num_rounds.png")
        return vc_num_rounds

    def stat_scores_overall(self, th=4, ofn="stat_scores_overall.png"):
        mean_score = self.df["overall_score"].mean()
        passrate = sum(self.df["overall_score"] >= th) / len(self.df)
        print(f"Mean score: {mean_score:.2f}\nPassrate: {passrate:.2f}")
        
        df_scores = self.df['overall_score'].value_counts().sort_index().reset_index()

        # 合并数据到一个DataFrame
        data = []
        for score, count in df_scores.values:
            data.append([score, count, 'GPT'])
        df_scores_dist = pd.DataFrame(data, columns=['Score', 'Count', 'Source'])
        # 使用seaborn绘制条形图
        plt.figure(figsize=(10, 6))
        sns.barplot(x='Score', y='Count', hue='Source', data=df_scores_dist)
        plt.title('Comparison of Scores between GPT and Human')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/{ofn}")
        print(f"Saved to {self.output_dir}/{ofn}")
        return df_scores

    def stat_error_types(self, ofn="stat_error_types.png"):
        cnt = collections.Counter()
        for idx, row in self.df.iterrows():
            # print(f"{row['workflow_name']} - {row['workflow_id']}")
            for round_id, round_eval in row['judge_result']["detailed"].items():
                if not round_eval["errors"]: continue
                try:
                    for error_type, error_reason in round_eval["errors"].items():
                        # print(f"  {round_id}: {error_type} {error_reason}")
                        cnt[error_type] += 1
                except Exception as e:
                    print(round_eval["errors"])

        data = []
        for error_type, count in sorted(cnt.items(), key=lambda x: x[1], reverse=True):
            data.append([error_type, count, 'GPT'])
        df = pd.DataFrame(data, columns=['Error Type', 'Count', 'Source'])
        plt.figure(figsize=(12, 6))
        sns.barplot(x='Error Type', y='Count', hue='Source', data=df)
        plt.title('Comparison of Error Types between GPT and Human')
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/{ofn}")
        print(f"Saved to {self.output_dir}/{ofn}")
        return cnt

    def stat_grouped_passrate(self, th=4):
        # df["workflow_name", "overall_score"]
        def calculate_ratio(group):
            total = len(group)
            above_number = len(group[group['overall_score'] >= th])
            return above_number / total
        ratios = self.df.groupby('workflow_name').apply(calculate_ratio).reset_index()
        ratios.columns = ['workflow_name', 'ratio']
        return ratios