from halo import Halo
from ansible.plugins.callback import CallbackBase


class ProgressCallback(CallbackBase):
    def __init__(self):
        super(ProgressCallback, self).__init__()
        self.spinner = Halo(text="Initializing")
        self.spinner.start()

    def playbook_on_task_start(self, name, *args, **kwargs):
        self.spinner.text = name

    def warn(self, message):
        self.spinner.warn(message)

    def success(self, message):
        self.spinner.succeed(message)

    def failure(self, message):
        self.spinner.fail(message)
