# (c) 2016, Jiri Tyr <jiri.tyr@gmail.com>
#
# This file is part of Config Encoder Filters (CEF)
#
# CEF is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CEF is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CEF.  If not, see <http://www.gnu.org/licenses/>.

"""
Config Encoder Filters
More information: https://github.com/jtyr/ansible-config_encoder_filters
"""

from __future__ import (absolute_import, division, print_function)
from ansible import errors
from copy import copy
import re
import json


# Required for Python 3 compatibility
try:
    basestring
except NameError:
    basestring = str


def updateInterfaceList(xml):

    updatedInterfaceList = []
    portalInputs = xml["portalInputs"]
    print("MKA UPDATE INTERFACE :: %s", portalInputs )
    networkInfoList = xml["networkInfoList"]
    for i in range(0, len(portalInputs)):
        interfaceName = portalInputs[i]["portName"] +  "." + portalInputs[i]["subInterfaceId"] 
        ipAddress = portalInputs[i]["ipAddress"]
        for j in range(0, len(networkInfoList)):
           networkName = networkInfoList[j]["name"]
           for k in range(0, len(networkInfoList[j]["interfaces"])): 
               tmpInterfaceName = networkInfoList[j]["interfaces"][k] 
               print("COMPARING  %s with :: %s", interfaceName, tmpInterfaceName )
               if ( interfaceName == tmpInterfaceName): 
                  updateInterfaceItem = {}
                  updateInterfaceItem["name"] = networkName 
                  updateInterfaceItem["ipAddress"] = ipAddress 
                  updatedInterfaceList.append(updateInterfaceItem)

    return updatedInterfaceList



def modifyInterfaceDetails(xml):

    origMessage = xml["origMsg"]
    interfaceList = xml["inputs"]
    print("MKA INTERFACE LIST :: %s", interfaceList)
#    stagingVariables = xml["origMsg"]["versanms.sdwan-device-workflow"]["stagingTemplateInfo"]["templateData"]["device-template-variable"]["variable-binding"]["attrs"]
    postStagingVariables = xml["origMsg"]["versanms.sdwan-device-workflow"]["postStagingTemplateInfo"]["templateData"]["device-template-variable"]["variable-binding"]["attrs"]
    print("MKA INTERFACE LIST2 :: %s", interfaceList)

    for i in range(0, len( postStagingVariables)):
        if ( postStagingVariables[i]["isAutogeneratable"] == 0 ):
            if(re.search("staticaddress", postStagingVariables[i]["name"])):	
                for k in range(0, len( interfaceList)):
                    networkName = interfaceList[k]["name"]
                    print("CHECKING FOR NETWORK :: %s", networkName)
	            if ( re.search(networkName, postStagingVariables[i]["name"])):
                        print("MATCHED NETWORK PATTERN")
		        postStagingVariables[i]["value"] =  interfaceList[k]["ipAddress"]

	
    origMessage["versanms.sdwan-device-workflow"]["postStagingTemplateInfo"]["templateData"]["device-template-variable"]["variable-binding"]["attrs"]= postStagingVariables 
    return origMessage



def modifySubInterfaceDetails(xml):

    inputs = xml["input"]
    interfaceInfo = xml["interfaceInfo"]
    subInterfaceList = interfaceInfo["vni"]["unit"]
    print("MKA INTERFACE INFO :: %s", interfaceInfo)

    for i in range(0, len(subInterfaceList)):
        if ( string(subInterfaceList[i].name) == inputs["subInterfaceId"] ):
           subInterfaceList[i]["family"]["inet"]["address"][0] = inputs["ipAddress"]
           print("MKA MATCHED IP ADDR :: %s", inputs["ipAddress"])
    

    print("MKA RESPONSE :: %s", subInterfaceList)
    print("MKA RESPONSE :: %s", interfaceInfo)
    return origMessage








class FilterModule(object):
    """Ansible encoder Jinja2 filters."""

    def filters(self):
        """Expose filters to ansible."""

        return {
            'modifyInterfaceDetails': modifyInterfaceDetails,
            'updateInterfaceList': updateInterfaceList,
            'modifySubInterfaceDetails': modifySubInterfaceDetails
        }
