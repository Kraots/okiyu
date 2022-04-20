import random

from disnake.ext import commands, tasks

import utils

from main import Okiyu


class Tasks(commands.Cog):
    def __init__(self, bot: Okiyu):
        self.bot = bot
        self.send_random_question.start()

    @tasks.loop(hours=3)
    async def send_random_question(self):
        guild = self.bot.get_guild(938115625073639425)
        channel = guild.get_channel(938115789553299456)
        entry: utils.Constants = await utils.Constants.get()
        questions = entry.random_questions
        for i in range(9):
            random.shuffle(questions)
        question: str = random.choice(questions)
        await channel.send(question)

    @send_random_question.before_loop
    async def before_rand_q(self):
        await self.bot.wait_until_ready()


def setup(bot: Okiyu):
    bot.remove_cog(Tasks(bot))
