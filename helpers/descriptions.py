

def get_graph_id(category_id):
    ids = {
        '24': 6,
        '2': 3,
        '1': 3,
        '-1': 1,
        '79': 11,
        '20': 5
    }

    if category_id in ids:
        return '.group_page_with_args', ids[category_id]

    return '.single_graph_page', category_id
