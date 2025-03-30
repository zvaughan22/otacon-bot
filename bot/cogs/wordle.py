import discord
from discord.ext import commands
import aiohttp
import string

class TeamWordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.secret_word = None      # Current game's secret word
        self.guesses = []            # List of tuples: (guess, feedback)
        self.max_attempts = 6        # Maximum allowed guesses
        self.game_message = None     # The bot's message displaying the current game board

    async def fetch_secret_word(self):
        """
        Uses the Random Word API to fetch a random 5-letter word.
        Checks the candidate word against DictionaryAPI.dev to ensure it's valid.
        Attempts up to 5 times to get a valid word.
        """
        url = "https://random-word-api.herokuapp.com/word?number=1&length=5"
        max_attempts = 5
        attempt = 0

        async with aiohttp.ClientSession() as session:
            while attempt < max_attempts:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if isinstance(data, list) and data:
                            candidate = data[0].lower()
                            if await self.is_valid_word(candidate):
                                self.secret_word = candidate
                                print(f"New secret word set: {self.secret_word}")
                                return
                attempt += 1
        print("Failed to fetch a valid secret word from the Random Word API after multiple attempts.")

    async def is_valid_word(self, word: str) -> bool:
        """
        Validates the guessed or secret word using DictionaryAPI.dev.
        Returns True if the word exists.
        """
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return resp.status == 200

    def get_feedback(self, guess: str) -> str:
        """
        Compares the guess to the secret word and returns Wordle-style feedback.
        Green (🟩): correct letter in the correct spot.
        Yellow (🟨): letter is in the word but in a different spot.
        Gray (⬜): letter is not in the word.
        """
        secret = list(self.secret_word)
        guess_letters = list(guess)
        feedback = [""] * 5

        # First pass: mark correct letters (green)
        for i in range(5):
            if guess_letters[i] == secret[i]:
                feedback[i] = "🟩"
                secret[i] = None  # Mark this letter as used

        # Second pass: mark letters that are in the word but in the wrong position (yellow)
        for i in range(5):
            if feedback[i] == "":
                if guess_letters[i] in secret:
                    feedback[i] = "🟨"
                    secret[secret.index(guess_letters[i])] = None
                else:
                    feedback[i] = "⬜"
        return ''.join(feedback)

    async def update_game_board(self, ctx):
        """
        Builds the current game board text with all previous guesses, remaining attempts,
        and the letters that haven't been guessed yet.
        Deletes the previous board message (if any) for active games,
        but on game completion this message remains visible.
        """
        board_lines = ["**Current Board:**"]
        for guess, feedback in self.guesses:
            board_lines.append(f"`{feedback}`   (Guess: **{guess.upper()}**)")
        guesses_left = self.max_attempts - len(self.guesses)
        board_lines.append(f"Guesses left: **{guesses_left}**")

        # Compute remaining letters based on previous guesses.
        guessed_letters = set(letter for guess, _ in self.guesses for letter in guess)
        remaining_letters = sorted(set(string.ascii_lowercase) - guessed_letters)
        board_lines.append("Remaining letters: **" + " ".join(letter.upper() for letter in remaining_letters) + "**")
        
        board_text = "\n".join(board_lines)
        
        # For active games, delete previous board message if it exists.
        if self.secret_word is not None and self.game_message:
            try:
                await self.game_message.delete()
            except discord.NotFound:
                pass
            self.game_message = None
        
        # Send and store the new board message.
        self.game_message = await ctx.send(board_text)

    @commands.cooldown(rate=1, per=10, type=commands.BucketType.user)
    @commands.command(name="guess")
    async def guess(self, ctx, word: str):
        """
        Players submit their guess using: !guess <word>
        If no game is active, a new secret word is fetched.
        The bot then updates the game board with feedback from all guesses,
        indicates how many guesses are left, and shows the remaining unused letters.
        When the game ends, the final board message is not deleted so everyone can review the final guesses.
        """
        # Start a new game if no game is in progress.
        if self.secret_word is None:
            await self.fetch_secret_word()
            if not self.secret_word:
                await ctx.send("Sorry, I couldn't set a valid secret word right now. Try again later.")
                return
            self.guesses = []
            # Delete any board message from a previous active game (if any)
            if self.game_message:
                try:
                    await self.game_message.delete()
                except discord.NotFound:
                    pass
                self.game_message = None

        word = word.lower().strip()
        if len(word) != 5:
            await ctx.send("Your guess must be a 5-letter word.")
            return

        if not await self.is_valid_word(word):
            await ctx.send("That doesn't seem to be a valid English word.")
            return

        # Get feedback and store the guess.
        feedback = self.get_feedback(word)
        self.guesses.append((word, feedback))
        
        # Update the game board message.
        await self.update_game_board(ctx)

        # Check win condition.
        if word == self.secret_word:
            await ctx.send(f"Congratulations, team! The secret word was **{self.secret_word.upper()}**!")
            # Do not delete the final board message—allow players to review the final guesses.
            self.secret_word = None
            self.guesses = []
            self.game_message = None
            return

        # Check if the team has exhausted all guesses.
        if len(self.guesses) >= self.max_attempts:
            await ctx.send(f"Game over! You've used all attempts. The secret word was **{self.secret_word.upper()}**.")
            # Do not delete the final board message so the final guesses remain visible.
            self.secret_word = None
            self.guesses = []
            self.game_message = None

    @guess.error
    async def guess_error(self, ctx, error):
        """
        Error handler for the guess command.
        Informs users if they are sending guesses too quickly.
        """
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"You're guessing too fast. Try again in {error.retry_after:.1f} seconds.", delete_after=5)
        else:
            raise error

async def setup(bot):
    await bot.add_cog(TeamWordle(bot))
