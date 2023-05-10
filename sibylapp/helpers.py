import time


def process_show_more(to_show_, show_more_):
    if not show_more_:
        return to_show_[0:10]
    return to_show_


def process_search(to_show_, search_):
    if search_ is not None:
        to_show_ = to_show_[to_show_.index.str.contains(search_, case=False)]
    return to_show_
