from aligned import Model
from examples.credit_scoring.credit_history import CreditHistory
from examples.credit_scoring.zipcode import Zipcode
from examples.credit_scoring.laon import Loan

class CreditScoring(Model):

    credit = CreditHistory()
    zipcode = Zipcode()
    loan = Loan()

    metadata = Model.metadata_with(
        name="credit_scoring",
        description="A model that do credit scoring",
        features=[
            credit.credit_card_due,
            credit.mortgage_due,
            credit.student_loan_due,
            credit.vehicle_loan_due,
            credit.hard_pulls,
            credit.missed_payments_1y,
            credit.missed_payments_2y,
            credit.missed_payments_6m,
            credit.bankruptcies,

            zipcode.city,
            zipcode.state,
            zipcode.is_primary_location,
            zipcode.tax_returns_filed,
            zipcode.total_wages,

            loan.person_age,
            loan.person_income,
            loan.person_emp_length,
            loan.person_home_ownership_ordinal,
            loan.loan_amount,
            loan.loan_int_rate,
            loan.loan_intent_ordinal
        ]
    )

    was_granted_loan = loan.loan_status.as_classification_target()