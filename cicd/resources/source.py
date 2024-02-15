from __future__ import annotations

import os
import requests
import xmltodict

from cicd.utils.log import get_logger
from cicd.utils.utility import get_config

logger = get_logger(__name__)


class Source:
    """
       Represents a source in MDM.
       Args:
           source_id : ID of source
           file_name : The xml file that needs to be the body of the request
           account_id : Boomi Account ID (defined in config file as env variable)
           base64_credentials : Credentials (defined in config file as env variable)
           endpoint_url : Boomi End Point (defined in config file as env variable)
       """

    def __init__(self, source_id: str, config_file_path: str, file_name=None, account_id: str = None,
                 base64_credentials: str = None, endpoint_url: str = None,
                 ):
        config = get_config(config_file_path)
        self.environment = os.environ["ENV"]
        self.file_name = file_name
        self.source_id = source_id
        if account_id is None:
            self.account_id = config[self.environment]["account_id"]
        if base64_credentials is None:
            self.base64_credentials = config[self.environment]["base64_credentials"]
            self.headers = {"Authorization": "Basic %s" % self.base64_credentials, "Content-Type": "application/xml"}
        if endpoint_url is None:
            self.endpoint_url = config[self.environment]["endpoint_url"]

    def _list_sources(self):
        """
            Lists Existing Source in MDM
            returns: source_ids
        """
        url = f"{self.endpoint_url}/{self.account_id}/sources"
        response = requests.get(url=url, headers=self.headers)
        if response.status_code == 200:
            source_list_summary = response.text
            data_dict = xmltodict.parse(source_list_summary)
            # Access sourceId values
            source_ids = [account_source['mdm:sourceId'] for account_source in
                          data_dict['mdm:AccountSources']['mdm:AccountSource']]
            return source_ids

    def create_source(self):

        """
            Creates Source in MDM
        """
        source_ids = self._list_sources()
        if self.source_id in source_ids:
            raise RuntimeError("Source with this ID already present")

        url = f"{self.endpoint_url}/{self.account_id}/sources/create"
        with open(self.file_name, 'rb') as payload:
            create_source_xml_data = payload.read()
            print(create_source_xml_data)
        response = requests.post(url=url, headers=self.headers, data=create_source_xml_data)
        if response.status_code == 200:
            logger.info("Source created successfully!")
        else:
            logger.error(f"Failed to create source.{response.content}")
            raise RuntimeError("Response is not 200 Exiting")

    def update_source(self):

        """
            Updates Source in MDM
        """
        source_ids = self._list_sources()

        if self.source_id not in source_ids:
            raise RuntimeError("Source with this ID is not Present, Please create a new source")

        url = f"{self.endpoint_url}/{self.account_id}/sources/{self.source_id}"
        with open(self.file_name, 'rb') as payload:
            xml_data = payload.read()
            print(xml_data)
            response = requests.put(url=url, headers=self.headers, data=xml_data)

        if response.status_code == 200:
            logger.info("Source updated successfully!")
        else:
            logger.error(f"Failed to update source.{response.content}")
            raise RuntimeError("Response is not 200 Exiting")

    def delete_source(self):

        """
            Deletes Source in MDM
        """
        source_ids = self._list_sources()

        if self.source_id not in source_ids:
            raise RuntimeError("Source with this ID does not exist")

        url = f"{self.endpoint_url}/{self.account_id}/sources/{self.source_id}"
        response = requests.delete(url=url, headers=self.headers)

        if response.status_code == 200:
            logger.info("Source Deleted successfully!")
        else:
            logger.error(f"Failed to Delete source.{response.content}")
            raise RuntimeError("Response is not 200 Exiting")
