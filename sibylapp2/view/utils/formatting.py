import pandas as pd

from sibylapp2.view.utils import helpers


def format_single_contributions_df(df, show_number=False):
    df["Contribution Value"] = df["Contribution"].copy()
    df["Contribution"] = helpers.generate_bars(df["Contribution"], show_number=show_number)
    return df


def format_two_contributions_to_view(
    df1,
    df2,
    features_df,
    lsuffix="_1",
    rsuffix="_2",
    show_number=False,
    show_contribution=False,
):
    original_df = format_single_contributions_df(df1, show_number=show_number)
    other_df = format_single_contributions_df(df2, show_number=show_number)
    compare_df = pd.concat([features_df, original_df], axis="columns")

    compare_df = compare_df.join(
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

    compare_df = compare_df.drop(
        [
            f"Contribution Value{lsuffix}",
            f"Contribution Value{rsuffix}",
        ],
        axis="columns",
    )

    if not show_contribution:
        compare_df = compare_df.drop(
            [
                f"Contribution{lsuffix}",
                f"Contribution{rsuffix}",
            ],
            axis="columns",
        )
    return compare_df
