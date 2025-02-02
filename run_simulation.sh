# poetry run prosimos start-simulation \
#     --bpmn_path ./o2_evaluation/scenarios/purchasing_example/purchasing_example.bpmn \
#     --json_path ./o2_evaluation/scenarios/purchasing_example/purchasing_example_with_batch.json \
#     --total_cases 100 \
#     --log_out_path ./o2_evaluation/scenarios/purchasing_example/purchasing_example_with_batch_event_log.csv \
#     --stat_out_path ./o2_evaluation/scenarios/purchasing_example/purchasing_example_with_batch_stats.csv

# poetry run prosimos start-simulation \
#     --bpmn_path ./examples/two_tasks_batching/two_tasks_batching.bpmn \
#     --json_path ./examples/two_tasks_batching/two_tasks_batching.json \
#     --total_cases 100 \
#     --log_out_path ./examples/two_tasks_batching/two_tasks_batching_event_log.csv \
#     --stat_out_path ./examples/two_tasks_batching/two_tasks_batching_stats.csv \
#     --starting_at 2000-01-03T00:00:00Z

poetry run prosimos start-simulation \
    --bpmn_path ./o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017.bpmn \
    --json_path ./o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017_with_batching.json \
    --total_cases 100 \
    --log_out_path ./o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017_event_log.csv \
    --stat_out_path ./o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017_stats.csv \
    --starting_at 2000-01-03T00:00:00Z