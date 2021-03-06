from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Raven.picklerick import PickleRick


class Commander:
    def __init__(self, bot: "PickleRick"):
        self.bot = bot
        self.train_commands = []
        self.build_commands = []
        self.build_book = {}  # tag : to build
        self.train_book = {}  # tag : to train

    def set_commander(self, manager):
        manager.commander = self

    def issue_train_command(self, trainer, to_train):
        trainer.train(to_train)
        return
        # command_tuple = (trainer, to_train)
        # if trainer.tag in self.train_book.keys():
        #     # logger.info(f"{trainer}, {trainer.tag}")
        #     # will need to account for reactor later
        #     return
        # else:
        #     self.train_commands.append(command_tuple)
        #     trainer.train(to_train)
        #     self.train_book[trainer.tag] = to_train

    def issue_build_command(self, builder, to_build, location):
        builder.build(to_build, location)
        return
        # command_tuple = (builder, to_build)
        #
        # # self.bot.worker_manager.
        # if builder.tag in self.build_book.keys():
        #     return
        # else:
        #     self.build_commands.append(command_tuple)
        #     builder.build(to_build, location)
        #     self.build_book[builder.tag] = to_build
