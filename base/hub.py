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
                f"Top Left ",  # Top Left
                pos=(0.2, 0.1),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"Mid Left ",  # Mid Left
                pos=(0.2, 0.13),
                size=13,
                color=(0, 255, 255),
        )
        self.client.debug_text_screen(
                f"Bottom Left ",  # Bottom Left
                pos=(0.2, 0.16),
                size=13,
                color=(0, 255, 255),
        )

        # left hand side, bottom
        self.client.debug_text_screen(
                f"Left Bottom ",  # Left Bottom
                pos=(0.2, 0.7),
                size=13,
                color=(0, 255, 255),
        )

        # right hand side
        self.client.debug_text_screen(
                f"Right Top",
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
