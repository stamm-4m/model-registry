"""seek.py

FAIRDOM-SEEK base class


AUTHOR:
    Brett Metcalfe (0000-0002-5873-9815)
    Laboratory of Systems and Synthetic Biology, Wageningen University & Research,
    Wageningen, The Netherlands


FUNDED BY:
    The authors disclose receipt of the following financial support for the research,
    authorship, and publication of this article: European Union's Horizon 2020 research
    and innovation programme projects ‘RI services to promote deep digitalization of
    Industrial Biotechnology - towards smart biomanufacturing’ (BIOINDUSTRY 4.0, grant
    agreement n° 101094287 [https://doi.org/10.3030/101094287]).


REQUIREMENTS:
    requests
    json
    os
    getpass
    abc
    pathlib
    time
    datetime


CONTAINS:
    var:
        None

    func:
        None

    classes:
        seek


"""

# ------------------------------
#       PACKAGES
# ------------------------------
import getpass
import json
from datetime import datetime
from pathlib import Path

import requests

# ------------------------------
#       VARIABLES
# ------------------------------


# ------------------------------
#       FUNCTIONS
# ------------------------------


# ------------------------------
#       CLASSES
# ------------------------------
class seek:
    def __init__(
        self,
        base_url: str,
        token: str = None,
    ) -> None:
        """init: Initialise base class

        INPUT:
            None

        OUTPUT:
            None

        """

        # -----------------------
        # User defined variables
        self.filepath: str = ""
        self.metadata: dict = {}
        self.metadata_dump: str = ""
        self.description: str = ""
        self.token_: str = token
        # self.session = None

        # ----------------------
        # Required variables
        self.base_url: str = base_url
        # self.headers = {}

        # ----------------------
        # BACKUP
        self.backup_filepath: str = ""

    def pretty_print_(self, dictionary_, indent_=4):
        """pretty_print_: Pretty print dict

        INPUT:
            dictionary_ = dictionary to print
            indent_     = amount of indent, default : 4

        OUTPUT:
            None, printed dictionary

        REQUIREMENTS:
            import json

        """
        print("\n\n")
        print(
            json.dumps(
                dictionary_,
                # sort_keys   =True,
                indent=indent_,
                # separators=(',', ': ')
            )
        )
        print("\n\n")

    def start_session(
        self,
        headers_: dict = {
            "Content-type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
            "Accept-Charset": "ISO-8859-1",
        },
    ) -> None:
        """start_session: Start requests session

        INPUT:
            headers_ = request header (dict, default: {
                            "Content-type": "application/vnd.api+json",
                            "Accept": "application/vnd.api+json",
                            "Accept-Charset": "ISO-8859-1"
                        })

        OUTPUT:
            None

        """
        self.session = requests.Session()

        if self.token_ is None:
            self.session.headers.update(headers_)
            self.session.auth = (input("Username:"), getpass.getpass("Password"))

        else:
            headers_["Authorization"] = "Token " + self.token_
            self.session.headers.update(headers_)

    def json_for_resource(
        self,
        type_: str,
        id_: int | None,
        header_={
            "Content-type": "application/vnd.api+json",
            "Accept": "application/vnd.api+json",
            "Accept-Charset": "ISO-8859-1",
        },
    ):
        """json_for_resource: JSON for resource

        INPUT:
            type_   = SEEK type
            id_     = SEEK ID
            header_ = Request header

        OUTPUT:
            r.json() =

        """
        if self.token_ is not None:
            header_["Authorization"] = "Token " + self.token_
            # print(header_)

        if id_ is not None:
            r = self.session.get(
                self.base_url + "/" + type_ + "/" + str(id_), headers=header_
            )

        else:
            r = self.session.get(self.base_url + "/" + type_, headers=header_)

        # -----------------
        # If response is not 200
        if r.status_code != 200:
            output_ = r.json()
            print(output_)

        r.raise_for_status()

        return r.json()

    def make_dir(self, path_: str = "user/", inc_timestamp: bool = False) -> str:
        """make_dir: Make a directory

        INPUT:
            path_  = base file path (str)
            inc_timestamp = whether to include a timestamp in the dir folder (bool)

        OUTPUT:
            upload_dir = make new dir

        """
        # --------------
        # MAKE path
        if inc_timestamp:
            upload_dir = Path(f"{path_}{datetime.now().strftime('%Y-%m-%d')}/")

        else:
            upload_dir = Path(f"{path_}")

        upload_dir = upload_dir.resolve().absolute()

        # --------------
        # MAKE dir
        upload_dir.mkdir(exist_ok=True)

        # --------------
        # SET var
        return upload_dir

    def make_backup_dir(
        self, backup_path_: str = "backup/", inc_timestamp_: bool = False
    ) -> None:
        """make_backup_dir: Make a backup directory

        INPUT:
            path_  = base file path (str)
            inc_timestamp = whether to include a timestamp in the dir folder (bool)

        OUTPUT:
            None, make new dir
                  modify self.backup_filepath


        """
        self.backup_filepath = self.make_dir(
            path_=backup_path_, inc_timestamp=inc_timestamp_
        )

    def download_resource(self):
        """
        Docstring for download_resource

        :param self: Description
        """
        pass

    def get_known_assets(
        self,
        seek_url_for_asset="projects",
        store_info=False,
    ):
        """FIND ASSET IN SEEK
        INPUT:
            asset_to_find       = a list of assets to find
            seek_url_for_asset  = the addition to the URL of the SEEK instance for the asset. Default: 'projects'
            store_info          = Store the results of the query or not. Default: False
            #~return_what         = decide what to return as output either 'name', 'id', or 'url'



        OUTPUT:
            output_             = the output
            [OPTIONAL] output_dict = if store_info is True then return a dictionary of dictionaries where
                                    an assets name is the key, and the values are 'name', 'id', 'url'

        REQUIREMENTS:
            import requests
            import json

        """
        ##########################
        # QUERY SEEK INSTANCE
        result = self.json_for_resource(type_=seek_url_for_asset, id_=None)
        # url_ = self.base_url + seek_url_for_asset, token_ = self.token_, use_authorization = True, print_output_ = True )

        ##########################
        # SEARCH QUERY

        output_dict = {}
        output_ = []

        if store_info:
            for idx in range(len(result["data"])):
                name_value = result["data"][idx]["attributes"]["title"]
                id_value = result["data"][idx]["id"]
                url_value = result["data"][idx]["links"]["self"]

                output_dict[name_value] = {
                    "name": name_value,
                    "id": id_value,
                    "url": url_value,
                }

            return output_dict

    def find_asset_in_seek(
        self,
        asset_to_find,
        seek_url_for_asset="projects",
        store_info=False,
        # return_what = 'id', #include = False,  #include_ = None,
    ):
        """FIND ASSET IN SEEK
        INPUT:
            asset_to_find       = a list of assets to find
            seek_url_for_asset  = the addition to the URL of the SEEK instance for the asset. Default: 'projects'
            store_info          = Store the results of the query or not. Default: False
            #~return_what         = decide what to return as output either 'name', 'id', or 'url'



        OUTPUT:
            output_             = the output
            [OPTIONAL] output_dict = if store_info is True then return a dictionary of dictionaries where
                                    an assets name is the key, and the values are 'name', 'id', 'url'

        REQUIREMENTS:
            import requests
            import json

        """
        ##########################
        # QUERY SEEK INSTANCE
        result = self.json_for_resource(type_=seek_url_for_asset, id_=None)
        # url_ = self.base_url + seek_url_for_asset, token_ = self.token_, use_authorization = True, print_output_ = True )

        ##########################
        # SEARCH QUERY

        output_dict = {}
        output_ = []

        if store_info:
            for idx in range(len(result["data"])):
                name_value = result["data"][idx]["attributes"]["title"]
                id_value = result["data"][idx]["id"]
                url_value = result["data"][idx]["links"]["self"]

                output_dict[name_value] = {
                    "name": name_value,
                    "id": id_value,
                    "url": url_value,
                }

            for individual in asset_to_find:
                for key in output_dict.keys():
                    if individual == key:
                        output_.append(output_dict[key]["id"])
                        break

            return output_, output_dict, result

        else:
            for individual in asset_to_find:
                for idx in range(len(result["data"])):
                    if individual == result["data"][idx]["attributes"]["title"]:
                        output_.append(result["data"][idx]["id"])
                        break

            return output_, output_dict, result

    def switch_dict_keys(
        self, dictionary_: dict, new_idx_key: str | float | int = "id"
    ):
        """switch_dict_keys: Rearrange a dictionary

        INPUT:
            dictionary_ = dict to rearrange
            new_idx_key = the new index key, note if this isnt unique it will overwrite

        OUTPUT:
            new_dict = the arranged dictionary



        """
        new_dict_: dict = {}

        for key_ in dictionary_:
            tmp_ = {}
            new_key = None

            for key_key_ in dictionary_[key_]:
                if key_key_ == new_idx_key:
                    new_key = dictionary_[key_][key_key_]
                    tmp_[key_key_] = dictionary_[key_][key_key_]

                else:
                    tmp_[key_key_] = dictionary_[key_][key_key_]

            new_dict_[new_key] = tmp_

        return new_dict_
