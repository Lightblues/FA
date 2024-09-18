import collections
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

class Analyzer:
    df: pd.DataFrame = None
    output_dir: str = "."
    def __init__(self, df: pd.DataFrame, output_dir: str) -> None:
        df["num_turns"] = df["judge_result"].apply(lambda x: len(x["detailed"]))
        df['overall_score'] = df['judge_result'].apply(lambda x: x["overall"]["score"])
        self.df = df
        self.output_dir = output_dir

    def stat_num_turns(self, stat_dict: dict={}, ofn="stat_num_turns.png"):
        avg_conv_turns = self.df["num_turns"].mean()
        # print(f"avg num turns: {avg_conv_turns:.2f}")
        stat_dict["avg_num_turns"] = avg_conv_turns
        
        vc_num_turns = self.df["num_turns"].value_counts().sort_index().reset_index()
        plt.figure(figsize=(10, 6))
        sns.barplot(x='num_turns', y='count', data=vc_num_turns, palette='Blues_d', hue='num_turns', legend=False)
        # plt.bar(vc_num_turns['num_turns'].values, vc_num_turns['count'].values, color='blue')
        plt.title('Number of turns Distribution')
        plt.xlabel('Number of turns')
        plt.ylabel('Count')
        plt.savefig(f"{self.output_dir}/{ofn}")
        print(f"Saved to {self.output_dir}/{ofn}")
        return vc_num_turns

    def stat_scores_overall(self, th=4, stat_dict: dict={}, ofn="stat_scores_overall.png"):
        mean_score = self.df["overall_score"].mean()
        passrate = sum(self.df["overall_score"] >= th) / len(self.df)
        # print(f"Mean score: {mean_score:.2f}\nPassrate: {passrate:.2f}")
        stat_dict["mean_score"] = mean_score
        stat_dict["passrate"] = passrate
        
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
            for turn_id, turn_eval in row['judge_result']["detailed"].items():
                if not turn_eval["errors"]: continue
                try:
                    for error_type, error_reason in turn_eval["errors"].items():
                        # print(f"  {turn_id}: {error_type} {error_reason}")
                        cnt[error_type] += 1
                except Exception as e:
                    print(turn_eval["errors"])

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

    def stat_grouped_passrate(self, th=4) -> pd.DataFrame:
        # df["workflow_name", "overall_score"]
        def calculate_ratio(group):
            total = len(group)
            above_number = len(group[group['overall_score'] >= th])
            return above_number / total
        ratios = self.df.groupby('workflow_name').apply(calculate_ratio).reset_index()
        ratios.columns = ['workflow_name', 'passrate']
        return ratios
