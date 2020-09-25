class Commander:
    def __init__(self, bot):
        self.bot = bot
        self.train_commands = []
        self.build_commands = []

    def set_commander(self, manager):
        manager.commander = self

    def issue_train_command(self, builder, to_build):
        command_tuple = (builder, to_build)
        self.train_commands.append(command_tuple)
        builder.train(to_build)

    def issue_build_command(self, builder, to_build, location):
        command_tuple = (builder, to_build)
        self.build_commands.append(command_tuple)
        builder.build(to_build, location)
