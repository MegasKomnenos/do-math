"""Layer 3 assembly of the real ports; product entry points pass this bundle down."""
from .ports import Ports
from .git_process import GitProcess
from .parallel import ThreadCalls
from .system_clock import SystemClock
from .windows_job import WindowsJobs
from .http_transport import UrllibHttp
from .powershell_scheduler import PowerShellScheduler
from .local_host import LocalHost


def real_ports() -> Ports:
    return Ports(clock=SystemClock(), git_backend=GitProcess(), calls=ThreadCalls(), jobs=WindowsJobs(),
                 scheduler=PowerShellScheduler(), http=UrllibHttp(),
                 host=LocalHost())
