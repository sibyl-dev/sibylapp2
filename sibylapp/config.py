BAR_LENGTH = 8
MAX_ENTITIES = 10

BASE_URL = "http://localhost:3000/api/v1/"

FLIP_COLORS = True  # If true, positive contributions will be red


def pred_format_func(pred):
    return "${:,.2f}".format(pred)
    # return "failure" if pred else "normal"
