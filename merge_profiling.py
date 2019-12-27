"""Script used for profiling pandas merges to produce call graphs for blog article."""
import cProfile
import pandas
import numpy

def generate_dataframes(
    N: int, set_index: bool, type_def: str, duplicates: float, sorted: bool
):
    numpy.random.seed(11)
    if duplicates > 0:
        sample = int((1 - duplicates) * N) + 1
        array_1 = numpy.random.choice(sample, N, replace=True)
    else:
        array_1 = numpy.arange(N)
        numpy.random.shuffle(array_1)  # shuffle works in-place

    df_1 = pandas.DataFrame(array_1, columns=["A"])
    df_1["B"] = df_1["A"] * 2

    array_2 = array_1.copy()
    numpy.random.shuffle(array_2)
    df_2 = pandas.DataFrame(array_2, columns=["A"])
    df_2["B"] = df_2["A"] * 2

    if type_def == "datetime":
        df_1["A"] = pandas.to_datetime(df_1["A"])
        df_2["A"] = pandas.to_datetime(df_2["A"])
    else:
        df_1["A"] = df_1["A"].astype(type_def)
        df_2["A"] = df_2["A"].astype(type_def)

    if set_index:
        df_1 = df_1.set_index("A")
        df_2 = df_2.set_index("A")

    if sorted:
        if set_index:
            df_1 = df_1.sort_index(ascending=True)
            df_2 = df_2.sort_index(ascending=True)
        else:
            df_1 = df_1.sort_values("A", ascending=True)
            df_2 = df_2.sort_values("A", ascending=True)

    return df_1, df_2


def profile(
    df_1: pandas.DataFrame, df_2: pandas.DataFrame, indexed: bool, output_name: str
):
    if indexed:
        cProfile.run(
            'df_1.merge(df_2, how="left", left_index=True, right_index=True)',
            output_name,
        )
    else:
        cProfile.run(
            'df_1.merge(df_2, how="left", left_on="A", right_on="A")', output_name
        )


def run_merge(
    df_1: pandas.DataFrame, df_2: pandas.DataFrame, indexed: bool, output_name: str
):
    if indexed:
        df_1.merge(df_2, how="left", left_index=True, right_index=True)
    else:
        df_1.merge(df_2, how="left", left_on="A", right_on="A")


if __name__ == "__main__":
    cases = {
        "case_0": (1_000_000, False, "int", 0, False),
        "case_1": (1_000_000, True, "int", 0, False),
        "case_2": (1_000_000, False, "str", 0, False),
        "case_3": (1_000_000, True, "str", 0, False),
        "case_4": (1_000_000, False, "category", 0, False),
        "case_5": (1_000_000, True, "category", 0, False),
        "case_6": (1_000_000, True, "int", 0.2, False),
        "case_7": (1_000_000, True, "int", 0, True),
    }

    n_rows, indexed, dtype, duplicates, sorted = cases["case_5"]
    df_1, df_2 = generate_dataframes(n_rows, indexed, dtype, duplicates, sorted)
    run_merge(df_1, df_2, indexed, "")
    raise Exception

    for case, args in cases.items():
        n_rows, indexed, dtype, duplicates, sorted = args
        df_1, df_2 = generate_dataframes(n_rows, indexed, dtype, duplicates, sorted)
        profile(df_1, df_2, indexed, f"{case}.cprof")
