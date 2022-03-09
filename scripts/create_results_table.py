# coding: utf-8
r"""
Inputs
------
in_path : str
    ``results/{scenario}/postprocessed/scalars.csv``: path to scalar results.
out_path : str
    ``results/{scenario}/tables/``: target path for results tables.

Outputs
-------
.csv
    Tables showing results.

Description
-----------
"""
import os
import sys

import pandas as pd

import oemof_b3.tools.data_processing as dp


def unstack_var_name(df):
    _df = df.copy()

    _df = df.set_index(
        ["scenario", "name", "region", "carrier", "tech", "type", "var_name"]
    )

    return _df.unstack("var_name")


if __name__ == "__main__":
    in_path = sys.argv[1]  # input data
    out_path = sys.argv[2]

    scalars = pd.read_csv(os.path.join(in_path, "scalars.csv"))

    def create_production_table(scalars, carrier):
        VAR_NAMES = [
            "capacity",
            f"invest_out_{carrier}",
            f"flow_out_{carrier}",
            "storage_capacity",
            "invest",
            "loss",
        ]

        df = scalars.copy()

        # df = dp.aggregate_scalars(df, "region")

        df = dp.filter_df(df, "var_name", VAR_NAMES)

        df = unstack_var_name(df).loc[:, "var_value"]

        df = df.loc[~df[f"flow_out_{carrier}"].isna()]

        df.index = df.index.droplevel(["name", "scenario", "type"])

        df.loc[:, "FLH"] = df.loc[:, f"flow_out_{carrier}"] / df.loc[
            :, ["capacity", "invest"]
        ].sum(axis=1)

        return df

    def create_demand_table(scalars):
        df = scalars.copy()

        var_name = "flow_in_"

        # df = dp.aggregate_scalars(df, "region")

        df = df.loc[df["var_name"].str.contains(var_name)]

        df = dp.filter_df(df, "type", ["excess", "load"])

        df = df.set_index(["region", "carrier", "tech"])

        df = df.loc[:, ["var_name", "var_value"]]

        return df

    if not os.path.exists(out_path):
        os.makedirs(out_path)

    df = create_production_table(scalars, "electricity")
    dp.save_df(df, os.path.join(out_path, "production_table.csv"))

    df = create_demand_table(scalars)
    dp.save_df(df, os.path.join(out_path, "sink_table.csv"))
