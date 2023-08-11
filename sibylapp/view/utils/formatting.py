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


def format_two_contributions_to_view(
    df1,
    df2,
    lsuffix="_1",
    rsuffix="_2",
    show_number=False,
    show_contribution=False,
):
    original_df = format_single_contributions_df(df1)
    other_df = format_single_contributions_df(df2)

    other_df = other_df.drop(["Category", "Feature"], axis="columns")
    compare_df = original_df.join(
        other_df,
        lsuffix=lsuffix,
        rsuffix=rsuffix,
    )
    compare_df["Contribution Change"] = (
        other_df["Contribution Value"] - original_df["Contribution Value"]
    )
    compare_df["Contribution Change Value"] = compare_df["Contribution Change"].copy()
    compare_df["Contribution Change"] = helpers.generate_bars(
        compare_df["Contribution Change"], show_number=show_number
    )

    if not show_contribution:
        compare_df = compare_df.drop(
            [
                f"Contribution{lsuffix}",
                f"Contribution{rsuffix}",
                f"Contribution Value{lsuffix}",
                f"Contribution Value{rsuffix}",
            ],
            axis="columns",
        )
    return compare_df
