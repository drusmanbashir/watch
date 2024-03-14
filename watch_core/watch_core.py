import logging
import time
import os
from typing import Annotated, Optional

import vtk, qt
from slicer.util import VTKObservationMixin, mainWindow

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)

from slicer import vtkMRMLScalarVolumeNode


#
# watch_core
#

class watch_core(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "watch_core"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#watch_core">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # watch_core1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='watch_core',
        sampleName='watch_core1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'watch_core1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='watch_core1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='watch_core1'
    )

    # watch_core2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='watch_core',
        sampleName='watch_core2',
        thumbnailFileName=os.path.join(iconsPath, 'watch_core2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='watch_core2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='watch_core2'
    )


#
# watch_coreParameterNode
#

@parameterNodeWrapper
class watch_coreParameterNode:
    """
    The parameters needed by module.

    inputVolume - The volume to threshold.
    imageThreshold - The value at which to threshold the input volume.
    invertThreshold - If true, will invert the threshold.
    thresholdedVolume - The output volume that will contain the thresholded volume.
    invertedVolume - The output volume that will contain the inverted thresholded volume.
    """
    inputVolume: vtkMRMLScalarVolumeNode
    imageThreshold: Annotated[float, WithinRange(-100, 500)] = 100
    invertThreshold: bool = False
    thresholdedVolume: vtkMRMLScalarVolumeNode
    invertedVolume: vtkMRMLScalarVolumeNode


#
# watch_coreWidget
#

class watch_coreWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._parameterNodeGuiTag = None
        self._updatingGUIFromParameterNode = False


    def setup(self) -> None:
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/watch_core.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = watch_coreLogic()

        # Connections
        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # Buttons
        self.ui.startButton.connect('clicked(bool)', self.onStartButton)
        self.ui.stopButton.connect('clicked(bool)', self.onStopButton)
        self.ui.resetButton.connect('clicked(bool)', self.onResetButton)
        # self.ui.saveButton.connect('clicked(bool)',self.onSaveButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

        self.set_layout()


    def set_layout(self):
        customLay = """
        <layout type="vertical" split="true">

          <item>
          <view class="vtkMRMLSliceNode" singletontag="Red">
            <property name="orientation" action="default">Coronal</property>
            <property name="viewlabel" action="default">R</property>
            <property name="viewcolor" action="default">#F34A33</property>
          </view>
          </item>
                    <item>
          <view class="vtkMRMLSliceNode" singletontag="Green">
            <property name="orientation" action="default">Axial</property>
            <property name="viewlabel" action="default">A</property>
            <property name="viewcolor" action="default">#6EB04A</property>
          </view>
          </item>
        </layout>
        """

        # Built-in layout IDs are all below 100, so you can choose any large random number
        # for your custom layout ID.
        customLayoutId = 532

        layoutManager = slicer.app.layoutManager()
        layoutManager.layoutLogic().GetLayoutNode().AddLayoutDescription(customLayoutId, customLay)

        # Switch to the new custom layout
        layoutManager.setLayout(customLayoutId)
        viewToolBar = mainWindow().findChild("QToolBar", "ViewToolBar")
        layoutMenu = viewToolBar.widgetForAction(viewToolBar.actions()[0]).menu()
        layoutSwitchActionParent = layoutMenu  # use `layoutMenu` to add inside layout list, use `viewToolBar` to add next the standard layout list
        layoutSwitchAction = layoutSwitchActionParent.addAction("My view")  # add inside layout list
        layoutSwitchAction.setData(customLayoutId)
        layoutSwitchAction.setIcon(qt.QIcon(":Icons/Go.png"))
        layoutSwitchAction.setToolTip("Comparison")

    def cleanup(self) -> None:
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self) -> None:
        """
        Called each time the user opens this module.
        """

        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self) -> None:
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI will be updated when the user enters into the module)
        if self._parameterNode:
            self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
            self._parameterNodeGuiTag = None
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)

    def onSceneStartClose(self, caller, event) -> None:
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event) -> None:
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self) -> None:
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.inputVolume:
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.inputVolume = firstVolumeNode

    def setParameterNode(self, inputParameterNode: Optional[watch_coreParameterNode]) -> None:
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """
        if self._parameterNode is not None and self.hasObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode):
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

        #
        # if self._parameterNode:
        #     self._parameterNode.disconnectGui(self._parameterNodeGuiTag)
        #     self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        # self._parameterNode = inputParameterNode
        # if self._parameterNode:
        #     # Note: in the .ui file, a Qt dynamic property called "SlicerParameterName" is set on each
        #     # ui element that needs connection.
        #     self._parameterNodeGuiTag = self._parameterNode.connectGui(self.ui)
        #     self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self._checkCanApply)
        #     self._checkCanApply()


    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # # Update node selectors and sliders
        # self.ui.scanASelector.setCurrentNode(self._parameterNode.GetNodeReference("ScanA"))
        # self.ui.scanBSelector.setCurrentNode(self._parameterNode.GetNodeReference("ScanB"))
        #
        # # Update buttons states and tooltips
        # if self._parameterNode.GetNodeReference("ScanA"):
        #     self.ui.segButton.enabled = True
        #     self.ui.emSegButton.enabled = True
        #     self.ui.labelButton.enabled = True
        # if self._parameterNode.GetNodeReference("ScanA") and self._parameterNode.GetNodeReference("ScanB"):
        #     self.ui.segRegButton.toolTip = "Compute output volume"
        #     self.ui.segRegButton.enabled = True
        # else:
        #     self.ui.segRegButton.toolTip = "Select input and output volume nodes"
        #     self.ui.segRegButton.enabled = False
        #
        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False


    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).

        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # lm = slicer.app.layoutManager()
        # red = lm.sliceWidget("Red").sliceView().mrmlSliceNode()
        # sliceLogic = slicer.app.applicationLogic().GetSliceLogic(red)
        # compositeNode = sliceLogic.GetSliceCompositeNode()
        # id = compositeNode.GetBackgroundVolumeID()
        # vol = slicer.mrmlScene.GetNodeByID(id)
        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        # self._parameterNode.SetNodeReferenceID("ScanA", self.ui.inputSelector.currentNodeID)
        # self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)

        self._parameterNode.EndModify(wasModified)

    def _checkCanApply(self, caller=None, event=None) -> None:
        if self._parameterNode and self._parameterNode.inputVolume and self._parameterNode.thresholdedVolume:
            self.ui.applyButton.toolTip = "Compute output volume"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input and output volume nodes"
            self.ui.applyButton.enabled = False

    def onStartButton(self) -> None:
        """
        Run processing when user clicks "Apply" button.
        """
        self.ui.stopButton.setEnabled(True)
        self.ui.resetButton.setEnabled(True)
        self.ui.startButton.setEnabled(False)
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
                               self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)

            # Compute inverted output (if needed)
            if self.ui.invertedOutputSelector.currentNode():
                # If additional output volume is selected then result with inverted threshold is written there
                self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
                                   self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)

    def onResetButton(self):
        self.ui.resetButton.setEnabled(False)
        self.ui.stopButton.setEnabled(False)
        self.ui.startButton.setEnabled(True)
        self.logic.reset()

    def onStopButton(self):
        self.ui.startButton.setEnabled(True)
        self.ui.resetButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.logic.stop()
#
    def onSaveButton(self):
        pass
# watch_coreLogic
#

class watch_coreLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self) -> None:
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)
        self.reset()

    def getParameterNode(self):
        return watch_coreParameterNode(super().getParameterNode())

    def reset(self):
        self.startTime =0
        self.startTime=0
        if hasattr(self,"ida"):
            nd = slicer.mrmlScene.GetNodeByID(self.ida)
            slicer.mrmlScene.RemoveNode(nd)

    def stop(self):
        self.stopTime = time.time()
        mn = slicer.mrmlScene.GetNodeByID(self.ida)
        mn.SetControlPointLabelFormat(str(self.stopTime-self.startTime))


    def process(self,
                inputVolume: vtkMRMLScalarVolumeNode,
                outputVolume: vtkMRMLScalarVolumeNode,
                imageThreshold: float,
                invert: bool = False,
                showResult: bool = True) -> None:
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume:
            raise ValueError("Input volume is invalid")

        inputVolume.GetScalarVolumeDisplayNode().AutoWindowLevelOff()
        inputVolume.GetScalarVolumeDisplayNode().SetWindowLevel(350,50)
        self.startTime = time.time()
        logging.info('Processing started')

        mn = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsFiducialNode')
        mn_name = inputVolume.GetName()+"_rad"
        mn.SetName(mn_name)
        self.ida = mn.GetID()
        self.hideOtherFiducials(self.ida)

    def hideOtherFiducials(self,nodeID):
        fids = slicer.mrmlScene.GetNodesByClass('vtkMRMLMarkupsFiducialNode')
        for fid in fids:
            id = fid.GetID()
            if id != nodeID:
                disp = fid.GetDisplayNode()
                disp.SetVisibility(False)




if __name__ == '__main__':
    w = slicer.qSlicerMarkupsPlaceWidget()
    w.setMRMLScene(slicer.mrmlScene)
    markupsNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsCurveNode')
    w.setCurrentNode(slicer.mrmlScene.GetNodeByID(markupsNode.GetID()))
    w.buttonsVisible = False
    w.placeButton().show()
    w.show()

#
# watch_coreTest
#
