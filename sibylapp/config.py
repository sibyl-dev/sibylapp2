# API CONFIGURATIONS ==============================================================================
BASE_URL = "https://dai-iberdrola-api.lids.mit.edu/api/v1"
CERT_PATHS = None

# APPLICATION-SPECIFIC CONFIGURATIONS =============================================================
FLIP_COLORS = True  # If true, positive contributions will be red


def pred_format_func(pred):  # Function to use to format the prediction values from model
    return "${:,.2f}".format(pred)
    # return "failure" if pred else "normal"


# OTHER CONFIGURATIONS ============================================================================
BAR_LENGTH = 8  # Number of squares to use for contribution/importance bars
MAX_ENTITIES = 10  # Maximum number of entities to select from. Set this to None to use all
