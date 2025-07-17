import json
import pathlib
from dataclasses import dataclass, field
from importlib.metadata import version
from typing import Dict, List, get_type_hints

import pandas as pd

from ..util import MonotonicTimer


@dataclass
class MCMCData:
    """Dataclass containing all of the MCMC results.

    This enables lighter-weight "save" behavior

    Note:
        `Optional[foo]` must be used rather than `from __future__ import annotations` and `foo | None` in python 3.9 due to use of `get_type_hints`
    """

    contexts: List[str] = field(default_factory=list)
    """List of contexts passed in to and returned by run_MCMC, stored in topological order
    """

    accept_samples_context: List[List[float]] = field(default_factory=list)
    """A list of accepted samples from the MCMC process.

    The number of accepted samples is important.
        
    Formerly `StartPage.ACCEPT`
    """

    accept_samples_phi: List[List[float]] = field(default_factory=list)
    """Accepted group boundaries from MCMC simulation
    
    Formerly `StartPage.PHI_ACCEPT`
    """

    A: int = field(default=0)
    """The newer limit for the Cal BP range to be considered considered during MCMC, denoting the most recent time.

    Formerly `StartPage.A`
    """

    P: int = field(default=0)
    """The older limit for the Cal BP range to be considered considered during MCMC

    Formerly `StartPage.P`
    """

    all_samples_context: List[List[float]] = field(default_factory=list)
    """A list of lists containing all samples for contexts from MCMC, including rejected samples.

    I.e. accept_samples_context is a subset of this.

    Formerly `StartPage.ALL_SAMPS_CONT`
    """

    all_samples_phi: List[List[float]] = field(default_factory=list)
    """A list of lists, containing all samples for group boundaries from MCMC, including rejected samples.

    I.e. accept_samples_phi is a subset of this.

    Formerly `StartPage.ALL_SAMPS_PHI`
    """

    accept_group_limits: Dict[str, List[float]] = field(default_factory=dict)
    """A dictionary of group limits from accepted phi samples. Produced in `phase_labels`. 

    Formerly `StartPage.resultsdict`
    """

    all_group_limits: Dict[str, List[float]] = field(default_factory=dict)
    """A dictionary of all_results? returned by MCMC_func, which is used to find the phase lengths during node finding on the results page.
    
    Formerly `StartPage.all_results_dict`
    """

    def save_results_dataframes(self, path: pathlib.Path, group_df: pd.DataFrame) -> None:
        """Save some MCMC data to disk, separately from the serialised version of this class

        Formerly part of StartPage.save_state_1

        Parameters:
            path (pathlib.Path): The path to the directory in which files should be created
            group_df (pd.DataFrame): A pandas dataframe containing context group information.

        Todo:
            - Check if `full_results_df` include the first 10000 elements or not?
        """

        # Output the some of all_group_limits
        df = pd.DataFrame()
        for i in self.all_group_limits.keys():
            df[i] = self.all_group_limits[i][10000:]
        full_results_df_path = path / "full_results_df"
        df.to_csv(full_results_df_path, index=False)

        # List containing the the group for each context, in order of topologically sorted contexts.
        key_ref = [list(group_df["Group"])[list(group_df["context"]).index(i)] for i in self.contexts]
        df1 = pd.DataFrame(key_ref)
        df1.to_csv(path / "key_ref.csv", index=False)

        # Output the context labels in topologically sorted order
        df2 = pd.DataFrame(self.contexts)
        df2.to_csv(path / "context_no.csv", index=False)

    def to_json(self, pretty: bool = False) -> str:
        """Serialise this object to JSON

        Parameters:
            pretty (bool): If the json should be prettified or not.

        Return:
            JSON string representing the MCMCData instance
        """

        # Create a dictionary contianing a subset of this instance's member variables, converted to formats which can be json serialised.
        data = {}

        for k, v in self.__dict__.items():
            if isinstance(v, tuple([str, int, float, list, dict, tuple])):
                data[k] = v
            else:
                data[k] = str(v)

        indent = 2 if pretty else None
        return json.dumps({"polychron_version": version("polychron"), "mcmc_data": data}, indent=indent)

    def save(self, path: pathlib.Path, group_df: pd.DataFrame, verbose: bool = False) -> None:
        """Save the current state of this file to the specified path

        Parameters:
            path: The directory in which the files will be saved.
            group_df: A pandas dataframe containing context group information
            verbose: If verbose output should be used

        Raises:
            RuntimeError: If the provided path is not a directory
            Exception: If other exceptions are raised during saving of files to disk
        """

        # Ensure that the parent directory exists
        if path.is_dir():
            try:
                timer_save = MonotonicTimer().start()

                # Get the json representation of the object
                timer_to_json = MonotonicTimer().start()
                json_s = self.to_json(pretty=True)
                timer_to_json.stop()

                timer_json_write = MonotonicTimer().start()
                json_path = path / "polychron_mcmc_data.json"
                with open(json_path, "w") as f:
                    f.write(json_s)
                timer_json_write.stop()

                timer_files = MonotonicTimer().start()
                # Also save the individual MCMC ouput files into the working directory
                self.save_results_dataframes(path, group_df)
                timer_files.stop()

                # Stop the timer and report timing if verbose
                timer_save.stop()
                if verbose:
                    print("Timing - MCMCData.save:")
                    print(f"  total:      {timer_save.elapsed(): .6f}s")
                    print(f"  to_json:    {timer_to_json.elapsed(): .6f}s")
                    print(f"  json_write: {timer_json_write.elapsed(): .6f}s")
                    print(f"  files:      {timer_files.elapsed(): .6f}s")

            except Exception as e:
                raise e
        else:
            raise RuntimeError(f"'{path}' is not a directory, unable to save \"polychron_mcmc_data.json\"")

    @classmethod
    def load_from_disk(cls, json_path: pathlib.Path) -> "MCMCData":
        """Get an instance of the MCMCData from serialised json on disk.

        Parameters:
            json_path: Path to json file to load it from

        Returns:
            MCMCData instance

        Raises:
            RuntimeError: If the json_path is not an existing file; or the 'polychron_version' key is missing from the json file'; or the 'mcmc_data' key is missing from the json file
            json.JSONDecodeError: If the json_path does not point to a valid json file
        """
        import sys

        # Ensure the file exists
        if not json_path.is_file():
            raise RuntimeError(f"Error loading MCMCData from path, '{json_path}' is not a file")

        # Attempt to open the json file, building an instance
        with open(json_path, "r") as f:
            data = json.load(f)
            # Raise an excpetion if required keys are missing
            if "polychron_version" not in data:
                raise RuntimeError("Required key 'polychron_version' missing from '{json_path}'")
            if "mcmc_data" not in data:
                raise RuntimeError("Required key 'mcmc_data' missing from '{json_path}'")

            mcmc_data = data["mcmc_data"]

            # Any polychron-version specific handling of data
            polychron_version = data["polychron_version"]
            if polychron_version == "0.2.0":
                pass

            # Convert certain values back based on the hint for the data type.
            cls_type_hints = get_type_hints(cls)
            # Also build a list of keys to remove
            unexpected_keys = []
            for k in mcmc_data:
                if k in cls_type_hints:
                    if mcmc_data[k] is None:
                        pass
                else:
                    # If the key is not in the typehints, it will cause the ctor to trigger a runtime assertion, so remove it.
                    print(f"Warning: unexpected MCMCData member '{k}' during deserialisation", file=sys.stderr)
                    unexpected_keys.append(k)

            # Remove any unexpected keys
            for k in unexpected_keys:
                del mcmc_data[k]

        # Create an instance of the Model
        obj: MCMCData = cls(**mcmc_data)

        # Return the instance
        return obj
