# API CONFIGURATIONS ==============================================================================
BASE_URL = "http://localhost:3000/api/v1/"
CERT = None

# APPLICATION-SPECIFIC CONFIGURATIONS =============================================================
FLIP_COLORS = True  # If true, positive contributions will be red


def pred_format_func(
    pred,
):  # Function to use to format the prediction values from model
    #return format_dollar(pred)  # See pre-written options below for defaults
    return format_boolean_name(pred, "failure", "normal")


# OTHER CONFIGURATIONS ============================================================================
BAR_LENGTH = 8  # Number of squares to use for contribution/importance bars
MAX_ENTITIES = (
    11  # Maximum number of entities to select from. Set this to None to use all
)
DATASET_SIZE = 1000  # Max number of entities to use for dataset-wide visualizations
LOAD_UPFRONT = False  # If true, run heavy computations on initial load, else greedily run as needed


# PRE-WRITTEN FORMAT FUNCTION OPTIONS =============================================================
def format_none(pred):
    return pred


def format_dollar(pred):
    return "${:,.2f}".format(pred)


def format_class_name(pred, class_names):
    return class_names[int(pred)]


def format_boolean_name(pred, pos_name, neg_name):
    return pos_name if pred else neg_name


def format_number(pred, decimals=2):
    return "{:,.{prec}f}".format(pred, prec=decimals)
