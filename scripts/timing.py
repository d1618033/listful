import contextlib
import time


timing_information = []


def unique(items):
    found = set()
    result = []
    for item in items:
        if item in found:
            continue
        found.add(item)
        result.append(item)
    return result


@contextlib.contextmanager
def time_it(category, sub_category):
    start = time.time()
    yield
    finish = time.time()
    timing_information.append({'category': category, 'sub_category': sub_category, 'total': finish - start})



def time_listful(data):
    with time_it("listful", "init"):
        import listful
        items = listful.Listful(data, ["x", "y"])
    with time_it("listful", "filter:1"):
        items.filter(y=10).one_or_none()
    with time_it("listful", "filter:n"):
        for i in range(len(data)):
            items.filter(y=i*10).one_or_none()


def time_pandas(data):
    with time_it("pandas", "init"):
        import pandas
        df = pandas.DataFrame(data, columns=["x", "y"])
    with time_it("pandas", "filter:1"):
        df.loc[df.y == 10, :].to_dict('record')
    with time_it("pandas", "filter:n"):
        for i in range(len(data)):
            df.loc[df.y == (i*10), :].to_dict('record')



def time_pandas_with_index(data):
    with time_it("pandas_with_index", "init"):
        import pandas
        df = pandas.DataFrame(data, columns=["x", "y"])
        df.set_index("y", inplace=True)
    with time_it("pandas_with_index", "filter:1"):
        result = df.loc[10, :].to_dict()
        result['y'] = 10
    with time_it("pandas_with_index", f"filter:n"):
        for i in range(len(data)):
            result = df.loc[i * 10, :].to_dict()
            result['y'] = 20


def print_markdownrow(items):
    print('| ' + ' | '.join(items) + ' |')


def main():
    n = 10 ** 5
    data = [{"x": i, "y": 10 * i} for i in range(n)]
    time_listful(data)
    time_pandas(data)
    time_pandas_with_index(data)
    print_markdown()


def print_markdown():
    import listful
    info = listful.Listful(timing_information, fields=["category", "sub_category"])
    columns = unique(info.get_all_for_field("category"))
    rows = unique(info.get_all_for_field("sub_category"))
    print_markdownrow([' '] + columns)
    print_markdownrow(['---'] * (len(columns) + 1))
    for row in rows:
        print_markdownrow([row] + [
            '{:.2e}'.format(info.filter(category=column, sub_category=row).one_or_raise()['total'])
            for column in columns
        ])


if __name__ == '__main__':
    main()