'''
def start_test_view(request, test_link):
    # 1. Look up the test using the unique link
    # test = find Test where link == test_link

    # 2. Mark test as started if not already
    if test.status == "pending":
        test.status = "in_progress"
        test.started_at = current_time
        save test

    # 3. Retrieve the first stimulus for this test
    first_stimulus = get stimulus with order_index == 1 for this test

    # 4. Return JSON containing the first stimulus sequence and type
    return { "stimulus": first_stimulus }

def get_next_stimulus_view(request, test_id, current_order):
    # 1. Find the next stimulus in sequence
    next_stimulus = find stimulus where test_id == test_id 
                     and order_index == current_order + 1

    # 2. If no more stimuli, signal completion
    if next_stimulus does not exist:
        return { "done": True }

    # 3. Return the next stimulus
    return { "stimulus": next_stimulus }

def record_response_view(request):
    # 1. Extract data from AJAX request
    stimulus_id = request.data["stimulus_id"]
    clicked_symbol = request.data["symbol"]
    latency = request.data["latency_ms"]
    click_order = request.data["click_order"]

    # 2. Determine correctness
    stimulus = find Stimulus by stimulus_id
    is_correct = check if clicked_symbol is correct for this click_order

    # 3. Save response
    create Response(
        stimulus_id = stimulus_id,
        clicked_symbol = clicked_symbol,
        latency_ms = latency,
        click_order = click_order,
        is_correct = is_correct,
        timestamp = now
    )
    return { "saved": True }


def complete_test_view(request, test_id):
    # 1. Retrieve all responses for this test
    responses = get all Responses where stimulus.test_id == test_id

    # 2. Compute totals
    num_latency = sum latencies for numeric stimuli
    mix_latency = sum latencies for mixed stimuli
    num_correct = count correct numeric responses
    mix_correct = count correct mixed responses

    # 3. Create Test_Data summary
    create Test_Data(
        test_id = test_id,
        date_completed = now,
        num_total_latency = num_latency,
        mix_total_latency = mix_latency,
        numeric_correct = num_correct,
        mixed_correct = mix_correct
    )

    # 4. Mark test as completed
    test.status = "completed"
    test.completed_at = now
    # save test

    return { "completed": True }
'''