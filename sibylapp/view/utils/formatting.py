from sibylapp.compute.context import get_term
from sibylapp.view.utils import helpers


def format_single_contributions_df(df, show_number=False):
    formatted_df = df.rename(
        columns={
            "category": "Category",
            "Feature Value": "%s Value" % get_term("Feature"),
        }
    )
    formatted_df = formatted_df[
        ["Category", "Feature", "%s Value" % get_term("Feature"), "Contribution"]
    ]
    formatted_df["Contribution Value"] = formatted_df["Contribution"].copy()
    formatted_df["Contribution"] = helpers.generate_bars(
        formatted_df["Contribution"], show_number=show_number
    )
    return formatted_df
