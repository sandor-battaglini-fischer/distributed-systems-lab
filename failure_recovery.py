import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from scipy.stats import gmean

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

def load_and_preprocess_data(path):
    df = pd.read_csv(path)
    status_lst = ['investigating', 'identified', 'monitoring', 'resolved', 'postmortem', 'start']
    for status in status_lst:
        df[f'{status}_timestamp'] = pd.to_datetime(df[f'{status}_timestamp'])
    
    # Rename columns to match what we expect for the rest of the analysis
    df = df.rename(columns={'API': 'API-OpenAI', 'ChatGPT': 'ChatGPT', 'Labs': 'DALL·E', 'Playground': 'Playground', 
                            'api.anthropic.com': 'API-Anthropic', 'claude.ai': 'Claude', 'console.anthropic.com': 'Console', 
                            'Character.AI': 'Character.AI'})
    return df

def filter_corner_cases(df):
    count_lst = [0] * 5
    corner_cases = pd.DataFrame()
    for index, record in df.iterrows():
        if record['investigating_timestamp'] > record['identified_timestamp']:
            count_lst[0] += 1
            corner_cases = pd.concat([corner_cases, record], axis=0)
        if record['identified_timestamp'] > record['monitoring_timestamp']:
            count_lst[1] += 1
            corner_cases = pd.concat([corner_cases, record], axis=0)
        if record['monitoring_timestamp'] > record['resolved_timestamp']:
            count_lst[2] += 1
            corner_cases = pd.concat([corner_cases, record], axis=0)
        if record['resolved_timestamp'] > record['postmortem_timestamp']:
            count_lst[3] += 1
            corner_cases = pd.concat([corner_cases, record], axis=0)
    print(count_lst)
    
    corner_cases = corner_cases.T
    return df.drop(corner_cases.index).reset_index(drop=True), corner_cases

def generate_status_count_table(df):
    count_dict = {}
    for index, record in df.iterrows():
        flags = ''.join(['S1' if record['investigating_flag'] == 1 else '',
                         'S2' if record['identified_flag'] == 1 else '',
                         'S3' if record['monitoring_flag'] == 1 else '',
                         'S4' if record['resolved_flag'] == 1 else '',
                         'S5' if record['postmortem_flag'] == 1 else ''])
        count_dict[flags] = count_dict.get(flags, 0) + 1

    sum_all = sum(count_dict.values())
    count_dict = dict(sorted(count_dict.items(), key=lambda item: item[1], reverse=True))

    count_df = pd.DataFrame(count_dict.items(), columns=['case', 'count'])
    count_df['percentage'] = count_df['count'] / sum_all
    count_df['percentage'] = count_df['percentage'].map(lambda x: '{:.2%}'.format(x))

    # Add row of sum_all to the last row
    sum_all_row = pd.DataFrame({'case': 'sum_all', 'count': sum_all, 'percentage': '100.00%'}, index=[0])
    count_df = pd.concat([count_df, sum_all_row], axis=0)
    return count_df

def generate_service_status_table(df, service_lst):
    dfs = {service: df[df[service] == 1] for service in service_lst}
    count_dict_lst = {}

    for service in service_lst:
        count_dict = {}
        for index, record in dfs[service].iterrows():
            flags = ''.join(['S1' if record['investigating_flag'] == 1 else '',
                             'S2' if record['identified_flag'] == 1 else '',
                             'S3' if record['monitoring_flag'] == 1 else '',
                             'S4' if record['resolved_flag'] == 1 else '',
                             'S5' if record['postmortem_flag'] == 1 else ''])
            count_dict[flags] = count_dict.get(flags, 0) + 1

        count_dict = dict(sorted(count_dict.items(), key=lambda item: item[1], reverse=True))
        count_df = pd.DataFrame(count_dict.items(), columns=['case', f'{service}'])
        count_dict_lst[service] = count_df

    case_df = count_dict_lst[service_lst[0]]
    for service in service_lst[1:]:
        case_df = pd.merge(case_df, count_dict_lst[service], on='case', how='outer')

    case_df = case_df.fillna(0)
    case_df['sum'] = case_df.iloc[:, 1:].sum(axis=1)
    case_df = case_df.sort_values(by='sum', ascending=False).reset_index(drop=True).set_index('case').T
    return case_df

def generate_service_percentage_table(case_df):
    case_df['sum_all'] = case_df.sum(axis=1)
    for column in case_df.columns:
        case_df[column] = case_df[column] / case_df['sum_all']
    case_df = case_df.drop(columns='sum_all').drop(index='sum').reset_index().rename(columns={'index': 'service'})
    return case_df.round(4)

def generate_stacked_bar_plot(case_df):
    fig, ax = plt.subplots(figsize=(16, 10))
    barWidth = 0.85
    bottom = [0] * len(case_df)
    colors = sns.color_palette('tab10', n_colors=len(case_df.columns[1:]))

    for column in case_df.columns[1:]:
        ax.bar(case_df['service'], case_df[column], bottom=bottom, label=column, color=colors.pop(0), width=barWidth)
        for index, value in enumerate(case_df[column]):
            if value > 0:
                ax.text(index, bottom[index] + value / 2, f'{value:.2%}', ha='center', va='center', color='white', fontsize=26)
        bottom = [sum(x) for x in zip(bottom, case_df[column])]

    labels = [r'\textbf{S1-S3-S4}', r'\textbf{S1-S4}', r'\textbf{S1-S2-S3-S4}', r'\textbf{S2-S3-S4}', r'\textbf{S1-S2-S4}', r'\textbf{S2-S4}', r'\textbf{S4}', r'\textbf{S3-S4}', r'\textbf{All-with-S5}']
    reversed_labels = labels[::-1]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed_labels, title=r'\textbf{Status Cases}', bbox_to_anchor=(1.01, 1.0), loc='upper left')
    ax.set_xlabel(r'\textbf{Service}', fontsize=30)
    ax.set_yticklabels([r'\textbf{0\%}', r'\textbf{20\%}', r'\textbf{40\%}', r'\textbf{60\%}', r'\textbf{80\%}', r'\textbf{100\%}'], fontsize=28)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('figures/stacked_bar_plot.png')

    
if __name__ == '__main__':
    # Main execution starts here
    path = 'data/clean/incident/2024-08-31/incident_stages.csv'
    df = load_and_preprocess_data(path)

    # Filtering corner cases
    df, corner_cases = filter_corner_cases(df)

    # Generate and print the count table
    count_df = generate_status_count_table(df)
    print(count_df)

    # Generate incident status count by service
    service_lst = ['API-OpenAI', 'ChatGPT', 'DALL·E', 'Playground', 'API-Anthropic', 'Claude', 'Console', 'Character.AI']
    case_df = generate_service_status_table(df, service_lst)
    print(case_df)

    # Generate percentage table
    case_percentage_df = generate_service_percentage_table(case_df)
    print(case_percentage_df)

    # Generate stacked bar plot
    generate_stacked_bar_plot(case_percentage_df)