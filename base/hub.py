class Hub:
    """

    """

    def __init__(self, bot):
        self.bot = bot
        self.client = None

    def debug_draw(self) -> None:
        # left hand side top
        self.client = self.bot.client
        self.client.debug_text_screen(
                f"Need Rax : {self.bot.evaluator.should_build_rax()} ",  # Top Left
                pos=(0.2, 0.1),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"self.bases : {self.bot.bases}",  # Mid Left
                pos=(0.2, 0.13),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"Main is walled : {self.bot.bases[0].is_walled(choke=self.bot.bases[0].chokes[0])} ",
                # Bottom Left
                pos=(0.2, 0.16),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"Main is morphing : {self.bot.bases[0].is_morphing}",  # Left Bottom
                pos=(0.2, 0.19),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"morphing bases  : {self.bot.map_manager.bases.morphing_bases}",  # Left Bottom
                pos=(0.2, 0.23),
                size=13,
                color=(0, 255, 255),
        )

        self.client.debug_text_screen(
                f"base is orbital  : {self.bot.bases[0].is_orbital}",  # Left Bottom
                pos=(0.2, 0.26),
                size=13,
                color=(0, 255, 255),
        )

        # left hand side, bottom
        self.client.debug_text_screen(
                f"Main is morphing : {self.bot.bases[0].is_morphing}",  # Left Bottom
                pos=(0.2, 0.7),
                size=13,
                color=(0, 255, 255),
        )

        # right hand side
        self.client.debug_text_screen(
                f"iteration: {self.bot.iteration}",
                pos=(0.7, 0.1),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"Right Mid:",
                pos=(0.7, 0.13),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"Right 3 ",
                pos=(0.7, 0.16),
                size=13,
                color=(0, 255, 255),
        )

        self.client.debug_text_screen(
                f"Right 4 ",
                pos=(0.7, 0.19),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"Scv count: {self.bot.supply_workers}",  # Right 5
                pos=(0.7, 0.22),
                size=13,
                color=(0, 255, 255),
        )

        self.client.debug_text_screen(
                f"Mineral collection rate: {self.bot.state.score.collection_rate_minerals}",
                pos=(0.7, 0.25),
                size=13,
                color=(0, 255, 255),
        )

        self.client.debug_text_screen(
                f"Vespene collection rate: {self.bot.state.score.collection_rate_vespene}",
                pos=(0.7, 0.28),
                size=13,
                color=(0, 255, 255),
        )
