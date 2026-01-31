from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer



class BuddyBotAI:
    """
    Encapsulates ChatterBot logic for clean integration.
    """

    def __init__(self):
        self.bot = ChatBot(
            name = "BuddyBot",
            read_only = True,
            logic_adapters=[
                {
                    "import_path": "chatterbot.logic.BestMatch",
                    "default_response": "I'm not sure how to respond to that yet.",
                    "maximum_similarity_threshold": 0.75
                }
            ]
        )

        self.train_bot()

    def train_bot(self):
        """
        Train the bot using English conversational data.
        """
        trainer = ChatterBotCorpusTrainer(self.bot)
        trainer.train("chatterbot.corpus.english")

    def get_response(self, user_input: str) -> str:
        """
        Get AI-generated response.
        """
        return str(self.bot.get_response(user_input))