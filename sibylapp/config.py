# API CONFIGURATIONS ==============================================================================
BASE_URL = "http://localhost:3000/api/v1/"
CERT = None

# APPLICATION-SPECIFIC CONFIGURATIONS =============================================================
FLIP_COLORS = True  # If true, positive contributions will be red


def pred_format_func(pred):  # Function to use to format the prediction values from model
    return dollar_format(pred)  # See pre-written options below for defaults


# OTHER CONFIGURATIONS ============================================================================
BAR_LENGTH = 8  # Number of squares to use for contribution/importance bars
MAX_ENTITIES = 10  # Maximum number of entities to select from. Set this to None to use all


# PRE-WRITTEN FORMAT FUNCTION OPTIONS =============================================================
def no_format(pred):
    return pred


def dollar_format(pred):
    return "${:,.2f}".format(pred)


def class_name_format(pred, class_names):
    return class_names[int(pred)]


def boolean_name_format(pred, pos_name, neg_name):
    return pos_name if pred else neg_name

