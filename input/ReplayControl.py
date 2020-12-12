import yaml
import asyncio
import time

def load(filename):
    with open(r"replay/%s" % filename) as file:
        return yaml.load(file, Loader=yaml.FullLoader)
    return {}

def init_replay(switch_controller):
    Replay(switch_controller)

class Replay:
    def __init__(self, switch_controller):
        self.switch_controller = switch_controller
        self.recording = False
        self.replaying = False
        self.last_timestamp = None
        self.replay_data = []
        switch_controller.register_handler(self.replay, self.should_replay)
        switch_controller.register_handler(self.record, self.should_record)

    async def replay(self, **args):
        self.replaying = not self.replaying
        if self.replaying:
            replay = load(args.get('filename', 'replay.yaml'))
            print('Running replay!')
            for step in replay:
                if not self.replaying:
                    break
                sleep = step.get('sleep', step.get('wait'))
                if sleep:
                    await asyncio.sleep(sleep)
                await self.switch_controller.handle(**step)
            print('replay finished!')
            self.replaying = False

    async def should_replay(self, **args):
        return args.get('action') == 'replay' and args.get('release') is False

    async def record(self, **args):
        self.recording = not self.recording
        if self.recording is False:
            print('Saved recording')
            with open(r"replay/%s" % self.filename, "w") as file:
                yaml.dump(self.replay_data, file)
        else:
            print('Start recording')
            self.filename = args.get('filename', 'replay.yaml')
            self.replay_data = []
            self.last_timestamp = False

    async def should_record(self, **args):
        if self.recording and args.get('action') not in ('record', 'replay'):
            current_timestamp = time.time()
            if self.last_timestamp:
                diff = current_timestamp - self.last_timestamp
                args['sleep'] = diff
            self.last_timestamp = current_timestamp
            self.replay_data.append(args)
        return args.get('action') == 'record' and args.get('release') is False

