from aligned import feature_view, Int64, String, FileSource, EventTimestamp, Bool, Float

loan_source = FileSource.parquet_at("data/loan_table.parquet", mapping_keys={
    "loan_amnt": "loan_amount"
})

ownership_values = ['RENT', 'OWN', 'MORTGAGE', 'OTHER']
loan_intent_values = [
    "PERSONAL", "EDUCATION", 'MEDICAL', 'VENTURE', 'HOMEIMPROVEMENT', 'DEBTCONSOLIDATION'
]


@feature_view(
    name="loan",
    description="The granted loans",
    batch_source=loan_source
)
class Loan:

    loan_id = String().as_entity()

    event_timestamp = EventTimestamp()

    loan_status = Bool().description("If the loan was granted or not")

    person_age = Int64()
    person_income = Int64()

    person_home_ownership = String().accepted_values(ownership_values)
    person_home_ownership_ordinal = person_home_ownership.ordinal_categories(ownership_values)

    person_emp_length = Float().description(
        "The number of months the person has been employed in the current job"
    )

    loan_intent = String().accepted_values(loan_intent_values)
    loan_intent_ordinal = loan_intent.ordinal_categories(loan_intent_values)

    loan_amount = Int64()
    loan_int_rate = Float().description("The interest rate of the loan")
