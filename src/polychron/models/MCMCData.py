import json
import pathlib
from dataclasses import dataclass, field
from importlib.metadata import version
from typing import Any, Dict, List, Optional, Tuple, get_type_hints


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
    """List of contexts? passed in to and returned by run_MCMC, 
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

    def save(self, path: pathlib.Path) -> None:
        """Save tthe current state of this file to the specified path

        Parameters:
            path (pathlib.Path ): The path at which the file will be saved

        Raises:
            Exception: @todo - docuemnt the specific exceptions which may be raised
        """
        import time

        time_start = time.monotonic()
        print(f"mcmc save {path}")

        # Ensure that the parent directory exists
        if path.parent.is_dir():
            try:
                # Get the json representation of the object
                json_s = self.to_json(pretty=True)
                print(f"MCMC json_s len: {len(json_s)}")

                with open(path, "w") as f:
                    f.write(json_s)

                time_end = time.monotonic()
                print(f"MCMC Saving time: {time_end - time_start}")
            except Exception as e:
                raise Exception(f"@todo - an exeption occurred during MCMC saving:\n {e}")
        else:
            raise Exception(f"@todo - {path.parent} does not exist")

    @classmethod
    def load_from_disk(cls, json_path: pathlib.Path) -> "MCMCData":
        """Get an instance of the MCMCData from serialised json on disk.

        Parameters:
            path: Path to json file to load it from

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
            # polychron_version = data["polychron_version"]
            # if polychron_version == "0.2.0":
            #     pass

            # Convert certain values back based on the hint for the data type.
            # @todo - improve this for some types?
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
                        # phase_rels needs to be returned to a tuple. @todo need to do this less specifically?
                        mcmc_data[k] = [tuple(sub) for sub in mcmc_data[k]]
                else:
                    # If the key is not in the typehints, it will cause the ctor to trigger a rutnime assertion, so remove it.
                    # @todo - make this visible in the UI?
                    print(f"Warning: unexected MCMCData member '{k}' during deserialisation")
                    unexpected_keys.append(k)

            # Remove any unexpected keys
            for k in unexpected_keys:
                del mcmc_data[k]

        # Create an instance of the Model
        obj: MCMCData = cls(**mcmc_data)

        # @todo - any post creation validation?

        # Return the instance
        return obj
