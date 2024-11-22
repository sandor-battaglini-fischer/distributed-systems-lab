import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

# Modularized Functions
def load_and_preprocess_data(path, start_date, end_date):
    df = pd.read_csv(path)

    # Convert the status columns to datetime and make them timezone-aware
    status_lst = ['investigating', 'identified', 'monitoring', 'resolved', 'postmortem', 'start']
    for status in status_lst:
        df[f'{status}_timestamp'] = pd.to_datetime(df[f'{status}_timestamp'])

    # Filter data within the start and end dates (both are tz-aware)
    df = df[(df['investigating_timestamp'] >= start_date) & (df['postmortem_timestamp'] <= end_date)]

    # Print to debug the filtered data
    print("Filtered DataFrame:")
    print(df)
    print("Services present after filtering:")
    for service in df.columns:
        if service in ['API', 'ChatGPT', 'Labs', 'Playground', 'api.anthropic.com', 'claude.ai', 'console.anthropic.com', 'Character.AI']:
            print(f"{service}: {df[service].sum()} incidents")

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
    print(f"Corner cases counts: {count_lst}")

    df = df.drop(corner_cases.index).reset_index(drop=True)
    return df

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
    df = df[[*service_lst, 'investigating_flag', 'identified_flag', 'monitoring_flag', 'resolved_flag', 'postmortem_flag']]
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
                ax.text(index, bottom[index] + value / 2, f'{value:.2%}', ha='center', va='center', color='white', fontsize=14)
        bottom = [sum(x) for x in zip(bottom, case_df[column])]

    labels = [
        'S1-S3-S4', 'S1-S4', 'S1-S2-S3-S4', 
        'S2-S3-S4', 'S1-S2-S4', 'S2-S4',
        'S4', 'S3-S4', 'All-with-S5'
    ]
    reversed_labels = labels[::-1]
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(reversed(handles), reversed_labels, title='Status Cases', bbox_to_anchor=(1.01, 1.0), loc='upper left')
    ax.set_xlabel('Service', fontsize=20)
    ax.set_ylabel('Percentage', fontsize=20)

    y_tick_lst = ['0%', '20%', '40%', '60%', '80%', '100%']
    ax.set_yticklabels(y_tick_lst, fontsize=16)

    plt.xticks(fontsize=16)
    plt.tight_layout()
    plt.show()


# Single Function Wrapping All Functionality
def incident_status_count(start_date, end_date, service_lst):
    path = 'data/clean/incident/2024-08-31/incident_stages.csv'

    # Load and preprocess data
    df = load_and_preprocess_data(path, start_date, end_date)

    # Filter corner cases
    df = filter_corner_cases(df)

    # Generate and print the status count table
    count_df = generate_status_count_table(df)
    #print(count_df)

    # Generate incident status count by service
    case_df = generate_service_status_table(df, service_lst)
    #print(case_df)

    # Generate percentage table
    case_percentage_df = generate_service_percentage_table(case_df)
    #print(case_percentage_df)

    # Generate stacked bar plot
    generate_stacked_bar_plot(case_percentage_df)