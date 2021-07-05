import sys
import pandas as pd

from oemoflex.model.datapackage import EnergyDataPackage
from oemoflex.tools.helpers import load_yaml


def update_with_checks(old, new):
    # Check if some data would get lost
    if not new.index.isin(old.index).all():
        raise Warning("Index of new data is not in the index of old data.")

    try:
        # Check if it overwrites by setting errors = 'raise'
        old.update(new, errors="raise")
    except ValueError:
        raise Warning("Update would overwrite existing data.")


if __name__ == "__main__":
    scenario_specs = sys.argv[1]

    edp_path = sys.argv[2]

    scenario_specs = load_yaml(scenario_specs)

    # setup default structure
    edp = EnergyDataPackage.from_csv_dir(edp_path)

    # Stack
    edp.stack_components()

    path_scalars = scenario_specs["path_scalars"]

    scalars = pd.read_csv(path_scalars, index_col=[0, 1])["var_value"]

    update_with_checks(edp.data["component"], scalars)

    edp.unstack_components()

    # save to csv
    edp.to_csv_dir(edp_path)
