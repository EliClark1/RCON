import asyncio

import discord

class Controls():
	def __init__(self, ctx, content, reactions, timeout=30, timeout_func=None):
		self.ctx = ctx
		self.content = content
		self.reactions = reactions #reactions should be a dict where the keys are unicode emotes and the values are functions
		self.timeout = timeout
		self.timeout_func = timeout_func

		self.message = None
	
	async def send(self):
		if isinstance(self.content, discord.Embed):
			self.message = await self.ctx.send(embed=self.content)
		else:
			self.message = await self.ctx.send(self.content)
		
		if self.timeout_func == None:
			self.timeout_func = await self.message.delete()

		for reaction in self.reactions:
			await self.message.add_reaction(reaction)

		await self.main_loop()
		return self.message

	async def main_loop(self):
		while True:
			def check(reaction, user):
				return str(reaction.emoji) in self.reactions and user.id == self.ctx.author.id and reaction.message.id == self.message.id

			try:
				reaction = await self.ctx.bot.wait_for("reaction_add", check=check, timeout=self.timeout)
			except(asyncio.TimeoutError):
				try:
					for i in self.reactions:
						await self.message.remove_reaction(i, self.ctx.bot.user)
				except(discord.errors.NotFound):
					return
					
				if self.timeout_func.__code__.co_argcount == 1:
					await self.timeout_func(self.message)
				else:
					await self.timeout_func()

				return
			else:
				func = self.reactions[str(reaction[0].emoji)]

				if func.__code__.co_argcount == 1:
					await func(self.message)
				else:
					await func()

				await self.message.remove_reaction(reaction[0].emoji, self.ctx.author)
				
class Paginator():
	def __init__(self, ctx, pages, timeout=30, timeout_func=None):
		self.ctx = ctx
		self.pages = pages
		self.timeout = timeout
		self.timeout_func = timeout_func
		
		self.index = 0
		self.message = None
		self.reactions = ["⬅", "➡"]

	async def send(self):
		if isinstance(self.pages[0], discord.Embed):
			self.message = await self.ctx.send(embed=self.pages[0])
		else:
			self.message = await self.ctx.send(self.pages[0])

		for reaction in self.reactions:
			await self.message.add_reaction(reaction)

		await self.main_loop()
		return self.message

	async def main_loop(self):
		while True:
			def check(reaction, user):
				return str(reaction.emoji) in self.reactions and user.id == self.ctx.author.id and reaction.message.id == self.message.id

			try:
				reaction = await self.ctx.bot.wait_for("reaction_add", check=check, timeout=self.timeout)
			except(asyncio.TimeoutError):
				try:
					for i in self.reactions:
						await self.message.remove_reaction(i, self.ctx.bot.user)
				except(discord.errors.NotFound):
					return

				if self.timeout_func != None:
					if self.timeout_func.__code__.co_argcount == 1:
						await self.timeout_func(self.message)
					else:
						await self.timeout_func()

				return
			else:
				if str(reaction[0].emoji) == self.reactions[0]:
					if self.index > 0:
						new_page = self.pages[self.index - 1]
						self.index -= 1
					else:
						new_page = None
				else:
					if self.index < len(self.pages) - 1:
						new_page = self.pages[self.index + 1]
						self.index += 1
					else:
						new_page = None

				if new_page != None:
					if isinstance(new_page, discord.Embed):
						await self.message.edit(embed=new_page)
					else:
						await self.message.edit(content=new_page)

				await self.message.remove_reaction(reaction[0].emoji, self.ctx.author)