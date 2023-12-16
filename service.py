import os
import sys

service_directory = os.path.dirname(__file__)
source_directory = os.path.abspath(service_directory)
os.chdir(source_directory)
venv_base = os.path.abspath(os.path.join(source_directory, "venv"))
print('Virtual Environment path:', venv_base)

sys.path.append(".")
old_os_path = os.environ['PATH']
os.environ['PATH'] = (
        os.path.join(venv_base, "Scripts") + os.pathsep +
        old_os_path
)
site_packages = os.path.join(venv_base, "Lib", "site-packages")
prev_sys_path = list(sys.path)


import site


site.addsitedir(site_packages)
sys.real_prefix = sys.prefix
sys.prefix = venv_base
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path
print("Success setup path ...")
print(sys.executable)


import servicemanager
import win32event
import win32service
import win32serviceutil
import win32api
import socket
from main import app
from typing import Optional
from abc import ABC, abstractmethod

sys.path.append(os.path.dirname(__name__))
sys.stdout = sys.stderr = open(os.devnull, 'w')


class BaseService(win32serviceutil.ServiceFramework, ABC):
    """Base class to create winservice in Python"""

    _svc_name_: str = 'baseService'
    _svc_display_name_: str = 'Base Python Service'
    _svc_description_: str = 'Base Python Service Description'
    _exe_name_: Optional[str] = None
    _exe_args_: Optional[str] = None

    @classmethod
    def parse_command_line(cls):
        """Parse the command line"""
        win32serviceutil.HandleCommandLine(cls)

    # Override the method in the subclass to do something just before
    # the service is stopped.
    @abstractmethod
    def stop(self):
        pass

    # Override the method in the subclass to do something at
    # the service initialization.
    @abstractmethod
    def start(self):
        pass

    # Override the method in the subclass to perform actual service task.
    @abstractmethod
    def service(self):
        pass

    def __init__(self, args):
        """Class constructor"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        # Create an event which we will use to wait on.
        # The "service stop" request will set this event.
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        """Called when the service is asked to stop"""
        # We may need to do something just before the service is stopped.
        self.stop()
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        # And set my event.
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Called when the service is asked to start. The method handles
        the service functionality.
        """
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)

        # We may do something at the service initialization.
        self.start()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        # Starts a worker loop waiting either for work to do or a notification
        # to stop, pause, etc.
        self.service()

    @staticmethod
    def logger(msg):
        """Called logger info message method from service manager"""
        servicemanager.LogInfoMsg(str(msg))

    @staticmethod
    def sleep(minute):
        win32api.Sleep((minute * 1000), True)


class FastAPIService(BaseService):
    _svc_name_ = "DEDP FastAPI"
    _svc_display_name_ = "DEDP FastAPI"
    _svc_description_ = "This is FastAPI application for call API"
    _exe_name_ = (
        "C:\\Users\\adf_ir\\Desktop\\app\\dedp-fastapi-on-premise"
        "\\venv\\Scripts\\pythonservice.exe"
    )

    def __init__(self, args):
        super().__init__(args)
        self.is_running: bool = False

    def start(self):
        self.is_running: bool = True

    def stop(self):
        self.is_running: bool = False

    def service(self):
        # This Function contains the actual logic, of Windows service
        # This is case, we are running our fastapi
        import uvicorn
        uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(FastAPIService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        FastAPIService.parse_command_line()
