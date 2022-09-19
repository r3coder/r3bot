import interactions
#############################

import os
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#############################

bot = interactions.Client(TOKEN)


@bot.event
async def on_ready():
    print("Quit!")

@bot.command(
    name="test_command",
    description="테스트 커맨드입니다."
)
async def test_command(ctx):
    await ctx.send("안녕")

@bot.command(
    name="say_something",
    description="say something!",
    scope=GUILD,
    options = [
        interactions.Option(
            name="text",
            description="What you want to say",
            type=interactions.OptionType.STRING,
            required=True,
        ),
    ],
)
async def my_first_command(ctx: interactions.CommandContext, text: str):
    await ctx.send(text, embeds=interactions.Embed(title="안녕", description="안녕하세요"))


@bot.command(name="send-button", description="Send a button")
async def send_button(ctx: interactions.CommandContext):
    button1 = interactions.Button(style=1, custom_id="button1", label="Click for Modal")
    button2 = interactions.Button(style=1, custom_id="button2", label="Click for Modal")
    button3 = interactions.Button(style=1, custom_id="button3", label="Click for Modal")
    await ctx.send("Click the button below to send a modal!", components=[button1, button2, button3])


@bot.command(name="send-modal", description="Send a modal")
async def send_modal(ctx: interactions.CommandContext):
    modal2323 = interactions.Modal(
        custom_id="modal",
        title="Modal Title",
        components=[
            interactions.TextInput(
                style=interactions.TextStyleType.SHORT,
                custom_id="text-input-1",
                label="Short text input",
            ),
            interactions.TextInput(
                style=interactions.TextStyleType.PARAGRAPH,
                custom_id="text-input-2",
                label="Paragraph text input",
            ),
        ],
    )
    await ctx.popup(modal2323)

@bot.modal("modal")
async def modal222(ctx: interactions.CommandContext, short: str, paragraph: str):
    await ctx.send(f'You said, "{short}" and "{paragraph}"')




bot.start()