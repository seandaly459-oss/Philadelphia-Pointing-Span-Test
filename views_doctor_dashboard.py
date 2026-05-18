'''
def doctor_dashboard_view(request):
    doctor = request.user

    # 1. Get all tests created by this doctor
    tests = find all Tests where doctor_id == doctor.id

    # 2. Compute dashboard metrics
    mean_age = average age of tests
    total_sessions = count tests with status == "completed"
    mean_latency = average of Test_Data latencies
    performance_by_age = group Test_Data by age bracket

    # 3. Return data to template
    return {
        "tests": tests,
        "mean_age": mean_age,
        "total_sessions": total_sessions,
        "mean_latency": mean_latency,
        "performance_by_age": performance_by_age
    }

def filter_tests_view(request):
    doctor = request.user
    filters = request.GET

    # 1. Start with all tests for this doctor
    queryset = Tests where doctor_id == doctor.id

    # 2. Apply filters
    if filters.age:
        queryset = queryset where age == filters.age

    if filters.start_date and filters.end_date:
        queryset = queryset where date_created between start_date and end_date

    if filters.status:
        queryset = queryset where status == filters.status

    # 3. Sort by alias (derived from test_id)
    if filters.sort_by_alias:
        queryset = sort queryset by hash(test_id)

    # 4. Return filtered list
    return { "tests": queryset }
'''