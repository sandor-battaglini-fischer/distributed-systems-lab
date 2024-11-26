# Import necessary libraries
import pandas as pd
from datetime import datetime
from chaos_analytical import *
import pytz

# Define timezone
timezone = pytz.UTC

# Convert start_date and end_date to timezone-aware
start_date = timezone.localize(datetime(2024, 6, 1))
end_date = timezone.localize(datetime(2024, 8, 31))


service_list = [
    'API-OpenAI', 'ChatGPT', 'DALL·E', 'Playground',
    'API-Anthropic', 'Claude', 'Console', 'Character.AI'
]
def run_all_plots():
    df = load_and_preprocess_data('server/static/data/incident_stages.csv', start_date, end_date)
    df = filter_corner_cases(df)

    plot_mttr_percentages(start_date, end_date, service_list)
    plot_mttr_ecdf(start_date, end_date, service_list)
    plot_mtbf_ecdf_provider(start_date, end_date, service_list)
    calculate_and_plot_mttr_percentages(start_date, end_date, service_list)
    box_plot_mttr_by_service(start_date, end_date, service_list)
    plot_mtbf_ecdf_by_service(start_date, end_date, service_list)
    plot_mtbf_boxplot_by_service(start_date, end_date, service_list)
    plot_incident_counts_by_day_of_week(start_date, end_date, service_list)

if __name__ == '__main__':
    run_all_plots()