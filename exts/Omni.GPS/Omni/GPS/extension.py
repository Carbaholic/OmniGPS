from logging import NullHandler
import omni.ext
import omni.ui as ui
import omni.kit.commands as commands
from pxr import Usd, Tf

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class MyExtension(omni.ext.IExt):

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):

        self._window = ui.Window("Telemetery", width=300, height=300)
        with self._window.frame:
            with ui.VStack():                
                usd_context = omni.usd.get_context()
                stage = usd_context.get_stage()
                
                ui.Label("Front Right Wheel Y Position", alignment=ui.Alignment.CENTER)
                                
                self.positionData = []
                self.positionData.append(0.0)
                self.positionPlot =  ui.Plot(ui.Type.LINE, 0.0, 2.0, *self.positionData, width=600, height=100, 
                    alignment=ui.Alignment.CENTER, style={"color": 0xFF0000FF})

                ui.Label("Front Right Wheel Y Velocity", alignment=ui.Alignment.CENTER)
                                
                self.velocityData = []
                self.velocityData.append(0.0)
                self.velocityPlot =  ui.Plot(ui.Type.LINE, -8.0, 8.0, *self.velocityData, width=600, height=100, 
                    alignment=ui.Alignment.CENTER, style={"color": 0xFF0000FF})

                ui.Label("Front Right Wheel Y Acceleration", alignment=ui.Alignment.CENTER)
                                
                self.accelerationData = []
                self.accelerationData.append(0.0)
                self.accelerationPlot =  ui.Plot(ui.Type.LINE, -400.0, 400.0, *self.accelerationData, width=600, height=100, 
                    alignment=ui.Alignment.CENTER, style={"color": 0xFF0000FF})

                self.previousPos = 0.0
                self.previousVelocity = 0.0

                self._stasge_listener = Tf.Notice.Register(
                    Usd.Notice.ObjectsChanged, self._notice_changed, stage)       

    def on_shutdown(self):
        print("[Omni.Telemetry] MyExtension shutdown")

    def _notice_changed(self, notice, stage):
        for p in notice.GetChangedInfoOnlyPaths():
            if p.GetPrimPath() == "/World/Vehicle/FrontRightWheel":
                                
                timeline = omni.timeline.get_timeline_interface()
                timecode = timeline.get_current_time() * timeline.get_time_codes_per_seconds()
                elapsedTime = 0.016667
                
                wheel = stage.GetPrimAtPath("/World/Vehicle/FrontRightWheel")
                pose = omni.usd.utils.get_world_transform_matrix(wheel, timecode)
                                
                nextPos = pose.ExtractTranslation()[1]

                if nextPos != self.previousPos:

                    nextVelocity = (nextPos - self.previousPos) / elapsedTime
                    yAcceleration = (nextVelocity - self.previousVelocity) / elapsedTime

                    self.previousPos = nextPos
                    self.previousVelocity = nextVelocity

                    self.positionData.append(nextPos)     
                    self.positionPlot.set_data(*self.positionData)

                    self.velocityData.append(nextVelocity)     
                    self.velocityPlot.set_data(*self.velocityData)

                    self.accelerationData.append(yAcceleration)     
                    self.accelerationPlot.set_data(*self.accelerationData)

    