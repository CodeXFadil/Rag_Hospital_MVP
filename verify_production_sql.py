from agents.patient_data_agent import get_lab_statistics, find_extreme_lab_cases, filter_patients, get_db_session

session = get_db_session()
try:
    print("=== Production SQL Verification ===\n")

    # 1. Verification of Aggregations
    print("TEST 1: Lab Statistics (HbA1c)")
    hba1c_stats = get_lab_statistics("HbA1c", session=session)
    print(f"  Average: {hba1c_stats['average']}")
    print(f"  Max: {hba1c_stats['max']}")
    print(f"  Count: {hba1c_stats['count']}")
    
    # 2. Verification of Ranking
    print("\nTEST 2: Extreme Lab Cases (Top 3 Highest LDL)")
    high_ldl = find_extreme_lab_cases("LDL", top_n=3, order="desc", session=session)
    for i, case in enumerate(high_ldl, 1):
        print(f"  {i}. {case['name']} | LDL: {case['extracted_value']} | Meds: {case['medications']}")

    # 3. Verification of Multi-Condition JOIN Filtering
    print("\nTEST 3: Multi-table JOIN (Females > 50 with HbA1c > 8)")
    entities = {
        "gender": "female",
        "age_range": {"min": 50},
        "lab_filters": [{"marker": "HbA1c", "operator": ">", "value": 8}]
    }
    matches = filter_patients(entities, session=session)
    print(f"  Matches Found: {len(matches)}")
    for m in matches:
        print(f"  - {m['name']} (Age {m['age']}) | Filters: {m['lab_results']}")

finally:
    session.close()
