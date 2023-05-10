def process_options(to_show, show_more, search, categories):
    return process_search(process_filter(process_show_more(to_show, show_more), categories), search)


def process_show_more(to_show, show_more):
    if not show_more:
        return to_show[0:10]
    return to_show


def process_search(to_show, search):
    if search is not None:
        to_show = to_show[to_show["Feature"].str.contains(search, case=False)]
    return to_show


def process_filter(to_show, categories):
    if len(categories) > 0:
        return to_show[to_show["Category"].isin(categories)]
    return to_show
