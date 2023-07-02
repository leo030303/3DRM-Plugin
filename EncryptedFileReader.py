# Copyright (c) 2018 Ultimaker B.V.
# This example is released under the terms of the AGPLv3 or higher.

from UM.Application import Application #To pass to the parent constructor.
from UM.Mesh.MeshBuilder import MeshBuilder #To create a mesh to put in the scene.
from UM.Mesh.MeshReader import MeshReader #This is the plug-in object we need to implement if we want to create meshes. Otherwise extend from FileReader.
from UM.Math.Vector import Vector #Helper class required for MeshBuilder.
from UM.Scene.SceneNode import SceneNode #The result we must return when reading.
import requests
import base64
import numpy
import stl  # numpy-stl lib
import stl.mesh
import tempfile
from io import BytesIO
import webbrowser
from UM.Extension import Extension  # We're implementing a Cura extension.
from cura.CuraApplication import CuraApplication  # To get the setting version to load the correct definition file, and to create QML components.
try:
	from PyQt6.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QUrl  # To expose data to the GUI and adjust the size of setting tooltips.
except ImportError:  # Older version of Cura.
	from PyQt5.QtCore import pyqtSlot, pyqtProperty, pyqtSignal, QObject, QUrl  # In Cura 4.x, use Qt5 instead of Qt6.



class EncryptedFileReader(MeshReader, Extension, QObject):
    def __init__(self, parent=None) -> None:
        MeshReader.__init__(self)
        Extension.__init__(self)
        QObject.__init__(self, parent)
        self.setMenuName("3DRM")
        self.addMenuItem("3DRM Login", self.startBrowser)

        self._supported_extensions = [".leo"] #Sorry, you also have to specify it here.

    def _swapColumns(self, array, frm, to):
        array[:, [frm, to]] = array[:, [to, frm]]
    
    def startBrowser(self) -> None:
        """
        Opens the guide in the welcome page.
        """
        webbrowser.open('http://127.0.0.1:3000/')

    ##  Read the specified file.
    #
    #   \return A scene node that represents what's in the file.
    def read(self, file_name):

        builder = MeshBuilder() #To construct your own mesh, look at the methods provided by MeshBuilder.
        with open(file_name, 'r') as f:
            file_content = f.read()
        
        # Data that we will send in post request.
        
        # Data that we will send in post request.
        fileData = {'mySTL':file_content}
        
        # The POST request to our node server
        res = requests.post('http://127.0.0.1:3000/decrypt', data=fileData) 
        
        # Convert response data to json
        returned_data = res.json()
        
        result = returned_data['result'] 
        base64dec_str = base64.b64decode(result)
        #bytesTest = BytesIO(base64dec_str)
        #base64dec_bin = stl.mesh.Mesh.from_file(bytesTest, mode=stl.stl.Mode.AUTOMATIC)
        print(base64dec_str)
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(base64dec_str)
            loaded_data = stl.mesh.Mesh.from_file(tmp.name, mode=stl.stl.Mode.AUTOMATIC)

        #builder.addCube(10, 10, 10, Vector(0, 0, 0)) #Cube of 10 by 10 by 10.
        #builder.calculateNormals()
        
        vertices = numpy.resize(loaded_data.points.flatten(), (int(loaded_data.points.size / 3), 3))
        #vertices = numpy.resize(base64dec_bin.points.flatten(), (int(base64dec_bin.points.size / 3), 3))

        # Invert values of second column
        vertices[:, 1] *= -1

        # Swap column 1 and 2 (We have a different coordinate system)
        self._swapColumns(vertices, 1, 2)

        builder.addVertices(vertices)

        builder.calculateNormals(fast = True)
        builder.setFileName(file_name)
        #Put the mesh inside a scene node.
        result_node = SceneNode()
        result_node.setMeshData(builder.build())
        result_node.setName(file_name) #Typically the file name that the mesh originated from is a good name for the node.

        return result_node



  
