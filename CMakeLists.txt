#Cura plug-in to read SVG files as toolpaths.
#Copyright (C) 2019 Ghostkeeper
#This plug-in is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#This plug-in is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for details.
#You should have received a copy of the GNU Affero General Public License along with this plug-in. If not, see <https://gnu.org/licenses/>.

project(3DRM)
cmake_minimum_required(VERSION 3.10.2) #Oldest version it's been tested with.

#Project metadata.
set(3DRM_SUPPORTED_SDKS "8.0.0" CACHE STRING "List of supported Cura SDK versions.")



#Installation.
configure_file("${CMAKE_CURRENT_SOURCE_DIR}/plugin.json.in" plugin.json)
set(installed_files
	__init__.py
	EncryptedFileReader.py
)
set(installed_paths "")
foreach(f IN LISTS installed_files)
	list(APPEND installed_paths ${CMAKE_CURRENT_SOURCE_DIR}/${f})
endforeach()
list(APPEND installed_paths ${CMAKE_CURRENT_BINARY_DIR}/plugin.json)

# Create the libbib directory
#file(MAKE_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/build/libbib)
#
# Run the pip install command
#execute_process(
#    COMMAND pip install cryptography --no-binary cryptography --target=${CMAKE_CURRENT_SOURCE_DIR}/build/libbib
#    RESULT_VARIABLE PIP_INSTALL_RESULT
#)
#
#if(PIP_INSTALL_RESULT EQUAL 0)
#    message(STATUS "Cryptography package installed successfully.")
#else()
#    message(FATAL_ERROR "Failed to install the cryptography package.")
#endif()



#Find out where to install this thing.
if(WIN32)
	set(cura_directory "$ENV{APPDATA}\\cura")
elseif(APPLE)
	set(cura_directory "$ENV{HOME}/Library/Application Support/cura")
else()
	set(cura_directory "$ENV{HOME}/.local/share/cura")
endif()
#Figure out the latest Cura release that's installed.
file(GLOB versions RELATIVE "${cura_directory}" "${cura_directory}/*")
set(latest_version 2.0)
foreach(version ${versions})
	if(IS_DIRECTORY "${cura_directory}/${version}")
		if(${version} VERSION_GREATER ${latest_version})
			set(latest_version ${version})
		endif()
	endif()
endforeach()
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
	set(CMAKE_INSTALL_PREFIX "${cura_directory}/${latest_version}/plugins" CACHE PATH "Location of the Cura plug-ins folder to install this plug-in to." FORCE)
endif()
install(FILES ${installed_paths} DESTINATION 3DRM)




add_custom_target(pack COMMAND "") #Packs for all supported SDK versions.
foreach(sdk_version ${3DRM_SUPPORTED_SDKS})
	#file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/build/libbib" DESTINATION pack${sdk_version}/files/plugins/3DRM)
	file(COPY ${installed_paths} DESTINATION pack${sdk_version}/files/plugins/3DRM)
	file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/cmake/[Content_Types].xml" DESTINATION pack${sdk_version})
	file(COPY "${CMAKE_CURRENT_SOURCE_DIR}/cmake/_rels" DESTINATION pack${sdk_version})
	configure_file("${CMAKE_CURRENT_SOURCE_DIR}/cmake/package.json.in" pack${sdk_version}/package.json)
	set(packaged_files
		package.json
		[Content_Types].xml
		_rels
		files
	)
	add_custom_target(pack${sdk_version}
		COMMAND "${CMAKE_COMMAND}" -E tar cfv ../3DRM1.0.0-sdk${sdk_version}.curapackage --format=zip ${packaged_files}
		WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/pack${sdk_version}
	)
	add_dependencies(pack pack${sdk_version})
endforeach()

#Let CPack find it.
include(InstallRequiredSystemLibraries)
set(CPACK_PACKAGE_VERSION_MAJOR 1)
set(CPACK_PACKAGE_VERSION_MINOR 0)
set(CPACK_PACKAGE_VERSION_PATCH 0)
set(CPACK_PACKAGE_NAME 3DRM)
set(CPACK_GENERATOR ZIP)
include(CPack)
