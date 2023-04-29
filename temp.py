import os
import openai
import asyncio

openai.api_key = os.getenv("OHMYGPT_API_KEY")
openai.api_base = os.getenv("OHMYGPT_API_BASE_CN")


async def get_respond():
    messages = [{"role": "user", "content": "how are you"}]
    try:
        result = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo", messages=messages
        )
        return result['choices'][0]['message']['content']
    except Exception as e:
        return str(e)


async def main():
    result = await get_respond()
    print(result)
    print("ladjlfkajdlk")


asyncio.run(main())
