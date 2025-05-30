import json
import pathlib
from dataclasses import dataclass, field
from importlib.metadata import version
from typing import Any, Dict, List, Optional, Tuple, get_type_hints

import pandas as pd

from ..Config import get_config
from ..util import MonotonicTimer


@dataclass
class MCMCData:
    """Dataclass containing all of the MCMC results.

    This enables lighter-weight "save" behaviour

    Todo:
        @todo - Rename variables to follow some convention. This will impact saving/loading so should be done sooner rather than later
        @todo - Better docstrings.
        @todo - more precise type-hints
    """

    CONTEXT_NO: List[Any] = field(default_factory=list)
    """List of contexts? passed in to and returned by run_MCMC. 

    In topological order
    @todo document it's contents
    @todo typehint
    @todo try and improve when it is set / read?"""

    ACCEPT: List[List[Any]] = field(default_factory=lambda: [[]])
    """An optional value returned from MCMC_func.
    A list of lists, where the minimum inner list length is used to dermine if more rounds of MCMC are required?
    
    Formerly StartPage.ACCEPT
    @todo - rename, rehome, typehint, docstring, maybe don't even store?
    """

    PHI_ACCEPT: Optional[Any] = field(default=None)
    """An optional value returned from MCMC_func. Appears unused.
    
    Formerly StartPage.PHI_ACCEPT
    @todo - rename, rehome, typehint, docstring, maybe don't even store?
    """

    A: int = field(default=0)
    """An integer set as a result from MCMC_func. Never actually read so doesn't need storing?

    Formerly StartPage.A
    @todo - rename, rehome, maybe don't even store?"""

    P: int = field(default=0)
    """An integer set as a result from MCMC_func. Never actually read so doesn't need storing?

    Formerly StartPage.P
    @todo - rename, rehome, maybe don't even store?"""

    ALL_SAMPS_CONT: Optional[Any] = field(default=None)
    """An optional value, initailised to None which is a MCMC_func ouptut, that is not used anywhere?

    Formerly StartPage.ALL_SAMPS_CONT
    @todo - rename, rehome, typehint, maybe don't even store?"""

    ALL_SAMPS_PHI: Optional[Any] = field(default=None)
    """An optional value, initailised to None which is a MCMC_func ouptut, that is not used anywhere?

    Formerly StartPage.ALL_SAMPS_PHI
    @todo - rename, rehome, typehint, maybe don't even store?"""

    resultsdict: Dict[Any, Any] = field(default_factory=dict)
    """A dictionary of results? returned by MCMC_func, which is used for plotting the mcmc results.
    
    Formerly StartPage.resultsdict
    @todo - rename, rehome, typehint, docstring
    """

    all_results_dict: Dict[Any, Any] = field(default_factory=dict)
    """A dictionary of all_results? returned by MCMC_func, which is used to find the phase lenghts during node finding on the results page.
    
    Formerly StartPage.all_results_dict
    @todo - rename, rehome, typehint, docstring
    """

    def save_results_dataframes(self, path: pathlib.Path, group_df: pd.DataFrame) -> None:
        """Save some MCMC data to disk, separately from the serialised version of this class

        Formerly part of StartPage.save_state_1

        Parameters:
            path (pathlib.Path): The path to the directory in which files should be created
            group_df (pd.DataFrame): A pandas dataframe containing context group information.

        Raises:
            Exception: Exceptions may be raised if errors occur during saving @todo (permissions etc)

        Todo:
            @todo - File extension(s)
            @todo - don't also include the same data in serialised version of this class?
            @todo - make the file names saved queryable so Model.save can discover them
            @todo - csv column names?
            @todo - key_ref.csv could be renamed

        """

        df = pd.DataFrame()
        for i in self.all_results_dict.keys():
            df[i] = self.all_results_dict[i][10000:]
        full_results_df_path = path / "full_results_df"
        df.to_csv(full_results_df_path)

        # List containing the the group for each context, in order of topologically sorted contexts.
        key_ref = [list(group_df["Group"])[list(group_df["context"]).index(i)] for i in self.CONTEXT_NO]
        df1 = pd.DataFrame(key_ref)
        df1.to_csv(path / "key_ref.csv")

        df2 = pd.DataFrame(self.CONTEXT_NO)
        df2.to_csv(path / "context_no.csv")

    def to_json(self, pretty: bool = False):
        """Serialise this object to JSON

        Parameters:
            pretty (bool): If the json should be prettified or not.

        Todo:
            - @todo decide which bits to exclude form saving/loading, and generate on reconstruction instead.
            - @todo - how to handle dataframes, Image.Image, files on disk, relative vs abs paths in the case a directory has been copied.
        """

        # Create a dictionary contianing a subset of this instance's member variables, converted to formats which can be json serialised.
        data = {}

        for k, v in self.__dict__.items():
            if v is None:
                # @todo - decide what to do for None values, include or not.
                data[k] = v
            elif isinstance(v, tuple([str, int, float, list, dict, tuple])):
                # @todo - may need to recurse into lists, dicts and tuples to make sure their members are all json serialiseable
                data[k] = v
            elif isinstance(v, pathlib.Path):
                data[k] = str(v)
            else:
                data[k] = str(v)

        indent = 2 if pretty else None
        return json.dumps({"polychron_version": version("polychron"), "mcmc_data": data}, indent=indent)

    def save(self, path: pathlib.Path, group_df: pd.DataFrame) -> None:
        """Save the current state of this file to the specified path

        Parameters:
            path (pathlib.Path ): The directory in which the files will be saved.
            group_df (pd.DataFrame): A pandas dataframe containing context group information

        Raises:
            Exception: @todo - document the specific exceptions which may be raised

        Todo:
            @todo Would be nicer if group_df didn't need to be passed in here?
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
                if get_config().verbose:
                    print("Timing - MCMCData.save:")
                    print(f"  total:      {timer_save.elapsed(): .6f}s")
                    print(f"  to_json:    {timer_to_json.elapsed(): .6f}s")
                    print(f"  json_write: {timer_json_write.elapsed(): .6f}s")
                    print(f"  files:      {timer_files.elapsed(): .6f}s")

            except Exception as e:
                raise Exception(f"@todo - an exeption occurred during MCMC saving:\n {e}")
        else:
            raise Exception(f"@todo - {path} does not exist")

    @classmethod
    def load_from_disk(cls, json_path: pathlib.Path) -> "MCMCData":
        """Get an instance of the MCMCData from serialised json on disk.

        Parameters:
            json_path: Path to json file to load it from

        Raises:
            Exception: @todo - docuemnt the specific exceptions which may be raised
        """

        # Ensure the file exists
        if not json_path.is_file():
            raise RuntimeError(f"Error loading from MCMCData from path '{json_path}' it is not a directory")

        # Attempt to open the json file, building an instance
        with open(json_path, "r") as f:
            data = json.load(f)
            # Raise an excpetion if required keys are missing
            if "polychron_version" not in data:
                # @todo - missing version might just mean we assume a current one?
                raise RuntimeError("@todo - bad json, missing version")
            if "mcmc_data" not in data:
                raise RuntimeError("@todo - bad json, missing mcmc_data")

            mcmc_data = data["mcmc_data"]

            # Any polychron-version specific handling of data
            polychron_version = data["polychron_version"]
            if polychron_version == "0.2.0":
                pass

            # Convert certain values back based on the hint for the data type.
            # @todo - improve this for some types?
            # @todo - discard keys we don't want to load before trying to convert them?
            cls_type_hints = get_type_hints(cls)
            # Also build a list of keys to remove
            unexpected_keys = []
            for k in mcmc_data:
                if k in cls_type_hints:
                    type_hint = cls_type_hints[k]
                    # If the values is None, do nothing. @todo - should this only be possible for Optionals?
                    if mcmc_data[k] is None:
                        pass
                    elif type_hint in [pathlib.Path, Optional[pathlib.Path]]:
                        mcmc_data[k] = pathlib.Path(mcmc_data[k])
                    elif type_hint in [Optional[List[Tuple[str, str]]]]:
                        # tuples are stored as lists in json, so must convert from a list of lists to a list of tuples
                        mcmc_data[k] = [tuple(sub) for sub in mcmc_data[k]]
                else:
                    # If the key is not in the typehints, it will cause the ctor to trigger a runtime assertion, so remove it.
                    # @todo - make this visible in the UI?
                    print(f"Warning: unexpected MCMCData member '{k}' during deserialisation")
                    unexpected_keys.append(k)

            # Remove any unexpected keys
            for k in unexpected_keys:
                del mcmc_data[k]

        # Create an instance of the Model
        obj: MCMCData = cls(**mcmc_data)

        # @todo - any post creation validation?

        # Return the instance
        return obj
