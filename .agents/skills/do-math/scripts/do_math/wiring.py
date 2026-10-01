"""Layer 3 assembly of the real ports; product entry points pass this bundle down."""
from .ports import Ports
from .git_process import GitProcess
from .parallel import ThreadCalls
from .system_clock import SystemClock
from .windows_job import WindowsJobs
from .http_transport import UrllibHttp
from .powershell_scheduler import PowerShellScheduler
from .local_host import LocalHost


def real_ports(*, environment) -> Ports:
    clock, jobs = SystemClock(), WindowsJobs()
    return Ports(clock=clock, git_backend=GitProcess(environment=environment), calls=ThreadCalls(), jobs=jobs,
                 scheduler=PowerShellScheduler(), http=UrllibHttp(),
                 host=LocalHost(jobs=jobs, clock=clock, environment=environment))
