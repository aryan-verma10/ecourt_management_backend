class ResponseConstants:
    '''
        Response Constants Defined here.
    '''
    INTERNAL_SERVER_ERROR = "Internal server error."
    CASE_NOT_FOUND = "Case not found."
    CASE_DATA_FETCHED_SUCCESSFULLY = "Case data fetched successfully."
    ALL_CASES_DATA_FETCHED_SUCCESSFULLY = "All cases data fetched successfully."
    DATA_ALREADY_EXIST = "Data already exist."
    DATABASE_ERROR = "Database error."
    NEW_CASE_CREATED_SUCCESSFULLY = "New case created successfully."
    NO_DATA_TO_UPDATE_PROVIDED = "No data to be updated is provided."
    CASE_DATA_UPDATED_SUCCESSFULLY = "Case data updated successfully."
    NO_CASES_FOUND = "No cases found."
    NEW_CASE_HEARING_ENTRY_ADDED_SUCCESSFULLY = "New case hearing entry added successfully."
    CASE_HEARING_NOT_FOUND = "Case hearing not found."
    CASE_HEARING_DATA_FETCHED_SUCCESSFULLY = "Hearing data fetched successfully."
    REQUEST_DATA_EMPTY = "Request data empty."
    CASE_HEARING_DATA_UPDATED_SUCCESSFULLY = "Case hearing updated successfully."
    CASE_HEARING_DELETED_SUCCESSFULLY = "Case hearing delete successfully."
    CASE_DETAILED_DATA_FETCHED_SUCCESSFULLY = "Case detailed data fetched successfuully."
    CASE_DELETED_SUCCESSFULLY = "Case deleted successfully."
    CASE_ORDER_ADDED_SUCCESSFULLY = "Case order added successfully."


class RedisConstants:
    '''
        Redis variable constants
    '''
    CASE_DETAILS = "case_details_case_id:"
    CASE_FULL_DETAILS_BY_CASE_NUMBER = "case_full_details:"
    ADMIN_CASE_HEARING_DETAILS_ADMIN = "admin_case_details_admin_case_hearing_id:"
    ADMIN_CASE_DETAILS_BY_ID = "admin_case_details_by_id:"