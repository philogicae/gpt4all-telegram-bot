import os
import sys
from subprocess import Popen, PIPE
from rich import print


class GPT4All():
    def __init__(self, model_path, config=None):
        self.bot = None
        self.config = config if config else {}
        self.executable_path = os.path.abspath('gpt4all-pywrap-linux-x86_64')
        self.model_path = model_path
        print(f'Exec: {self.executable_path}')
        print(f'Model: {self.model_path}')
        print(f'Config: {self.config}')

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def open(self):
        if self.bot:
            self.close()
        args = [self.executable_path, '--model', self.model_path]
        for k, v in self.config.items():
            args.append(f"--{k}")
            args.append(str(v))
        self.bot = Popen(args, stdin=PIPE, stdout=PIPE)
        self._parse_to_prompt(write_to_stdout=False)

    def close(self):
        self.bot.kill()
        self.bot = None

    def _parse_to_prompt(self, write_to_stdout=True):
        bot_says = ['']
        point = b''
        bot = self.bot
        while True:
            point += bot.stdout.read(1)
            try:
                character = point.decode("utf-8")
                if character == "\f":  # We've replaced the delimiter character with this.
                    return "\n".join(bot_says)
                if character == "\n":
                    bot_says.append('')
                    if write_to_stdout:
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                else:
                    bot_says[-1] += character
                    if write_to_stdout:
                        sys.stdout.write(character)
                        sys.stdout.flush()
                point = b''
            except UnicodeDecodeError:
                if len(point) > 4:
                    point = b''

    def prompt(self, prompt, write_to_stdout=False):
        if not self.bot:
            self.open()
        self.bot.stdin.write(prompt.encode('utf-8'))
        self.bot.stdin.write(b"\n")
        self.bot.stdin.flush()
        return_value = self._parse_to_prompt(write_to_stdout)
        if not self.bot:
            self.close()
        return return_value
