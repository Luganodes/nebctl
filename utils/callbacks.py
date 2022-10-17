from halo import Halo
from ansible.plugins.callback import CallbackBase


class ProgressCallback(CallbackBase):
    def __init__(self):
        super(ProgressCallback, self).__init__()
        self.spinner = Halo(text="Initializing")
        self.spinner.start()

    def playbook_on_task_start(self, name, *args, **kwargs):
        self.spinner.start()
        self.spinner.text = name

    def playbook_on_vars_prompt(self, varname, private=True, prompt=None, encrypt=None, confirm=False, salt_size=None, salt=None, default=None, unsafe=None):
        self.spinner.stop()

    def warn(self, message):
        self.spinner.warn(message)

    def success(self, message):
        self.spinner.succeed(message)

    def failure(self, message):
        self.spinner.fail(message)
