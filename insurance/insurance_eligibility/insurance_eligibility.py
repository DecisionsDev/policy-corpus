from common.common.Policy import Policy


class InsuranceEligibilityPolicy(Policy):
    MIN_AGE = 18
    MAX_AGE_FOR_ADDITIONAL_ASSESSMENTS = 75
    MAX_VEHICLE_AGE = 20
    LICENSE_STATUS_VALID = True
    VEHICLE_USAGE_PERSONAL = 'personal'

    def __init__(self, credit_score_threshold=600):
        self.credit_score_threshold = credit_score_threshold
        pass

    def test_eligibility(self, info):
        applicant_age = info.get('applicant_age')
        has_valid_license = info.get('has_valid_license')
        vehicle_registered = info.get('vehicle_registered')
        vehicle_age = info.get('vehicle_age')
        clean_driving_record = info.get('clean_driving_record')
        prior_insurance_coverage = info.get('prior_insurance_coverage')
        resides_in_country = info.get('resides_in_country')
        credit_score = info.get('credit_score')
        vehicle_usage = info.get('vehicle_usage')
        minimum_liability_coverage = info.get('minimum_liability_coverage')

        if applicant_age < self.MIN_AGE:
            return False, "Applicant must be at least 18 years old."

        if applicant_age > self.MAX_AGE_FOR_ADDITIONAL_ASSESSMENTS:
            return False, "Applicants over 75 may require additional medical assessments or driving tests."

        if not has_valid_license:
            return False, "All drivers must hold a valid driver’s license."

        if not vehicle_registered:
            return False, "The vehicle must be registered in the name of the applicant or an immediate family member."

        if vehicle_age > self.MAX_VEHICLE_AGE:
            return False, "Vehicles older than 20 years may not be covered."

        if not clean_driving_record:
            return False, "The primary policyholder and all listed drivers must have a reasonably clean driving record."

        if not prior_insurance_coverage:
            return False, "Applicants must provide details of their prior insurance coverage."

        if not resides_in_country:
            return False, "The applicant must reside in the country or state where the policy is issued."

        if credit_score is not None and credit_score < self.credit_score_threshold:
            return False, "Poor credit history may result in higher premiums or impact eligibility."

        if vehicle_usage != self.VEHICLE_USAGE_PERSONAL:
            return False, "The vehicle must be used primarily for personal use."

        if not minimum_liability_coverage:
            return False, "The applicant must purchase at least the minimum liability coverage required by law."

        return True, "Eligible for insurance coverage."

# Example usage
applicant_info = {
    'applicant_age': 25,
    'has_valid_license': True,
    'vehicle_registered': True,
    'vehicle_age': 15,
    'clean_driving_record': True,
    'prior_insurance_coverage': True,
    'resides_in_country': True,
    'credit_score': 700,
    'vehicle_usage': 'personal',
    'minimum_liability_coverage': True,
}

policy = InsuranceEligibilityPolicy()
eligible, message = policy.test_eligibility(applicant_info)
print(f"Eligible: {eligible}, Message: {message}")
