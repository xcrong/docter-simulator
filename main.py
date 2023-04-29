### ---- 2023/4/26 ---- ###

# ////////////////////////////////////////////////////////////////////
# //                          _ooOoo_                               //
# //                         o8888888o                              //
# //                         88" . "88                              //
# //                         (| ^_^ |)                              //
# //                         O\  =  /O                              //
# //                      ____/`---'\____                           //
# //                    .'  \\|     |//  `.                         //
# //                   /  \\|||  :  |||//  \                        //
# //                  /  _||||| -:- |||||-  \                       //
# //                  |   | \\\  -  /// |   |                       //
# //                  | \_|  ''\---/''  |   |                       //
# //                  \  .-\__  `-`  ___/-. /                       //
# //                ___`. .'  /--.--\  `. . ___                     //
# //              ."" '<  `.___\_<|>_/___.'  >'"".                  //
# //            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
# //            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
# //      ========`-.____`-.___\_____/___.-`____.-'========         //
# //                           `=---='                              //
# //      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
# //            佛祖保佑       永不宕机     永无BUG                    //
# ////////////////////////////////////////////////////////////////////


import os
import time
import asyncio
import flet as ft
import openai
import webbrowser

from bot import prompts, request_para
from info import notification, home_message

import logging

# logging.basicConfig(
#     level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
# )
# logging.getLogger("flet").setLevel(logging.WARN)


openai.api_key = os.getenv("OHMYGPT_API_KEY")
openai.api_base = os.getenv("OHMYGPT_API_BASE_CN")

# PAGE_WIDTH = 700
WIDTH_PERCENT = 0.7
PAGE_PLATFORM = ""

BOT_NAME = "Patient"
HUMAN_NAME = "Human"


class Message:
    def __init__(self, user_name: str, text: str, message_type: str):
        self.user_name = user_name
        self.text = text
        self.message_type = message_type


class BotMessage(ft.Row):
    def __init__(self, message: Message):
        super().__init__()
        self.vertical_alignment = "center"
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    # ft.Text(message.user_name, weight="bold"),
                    # ft.Text(message.text, selectable=False),
                    ft.Markdown(
                        message.text,
                        selectable=False,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        on_tap_link=lambda e: webbrowser.open(e.data),
                        # width=int(PAGE_WIDTH * WIDTH_PERCENT)
                    )
                ],
                width=int(PAGE_WIDTH * WIDTH_PERCENT),
                tight=True,
                spacing=5,
                alignment="start",
            ),
        ]
        self.alignment = "start"

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize()

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.PURPLE,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


class UserMessage(ft.Row):
    def __init__(self, message: Message, page_width):
        super().__init__()
        self.vertical_alignment = "center"
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user_name),
            ),
            ft.Column(
                [
                    ft.Markdown(
                        message.text,
                        selectable=False,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        on_tap_link=lambda e: webbrowser.open(e.data),
                        # width=int(PAGE_WIDTH * WIDTH_PERCENT)
                    ),
                ],
                width=int(page_width * WIDTH_PERCENT),
                tight=True,
                spacing=5,
                alignment="start",
            ),
        ]
        self.alignment = "start"

    def get_initials(self, user_name: str):
        return user_name[:1].capitalize()

    def get_avatar_color(self, user_name: str):
        colors_lookup = [
            ft.colors.BROWN,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


class Bot:
    async def get_respond(user_message, human_records: list, bot_records, p_index):
        l1 = [{"role": "user", "content": x} for x in human_records]
        l2 = [{"role": "assistant", "content": x} for x in bot_records]

        exist_message_ls = [x for pair in zip(l1, l2) for x in pair]

        messages = (
            [{"role": "system", "content": prompts[p_index]}]
            + exist_message_ls
            + [{"role": "user", "content": user_message}]
        )
        # try:
        #     result = await openai.ChatCompletion.acreate(
        #         model="gpt-3.5-turbo", messages=messages, stream=True, **request_para
        #     )
        #     for chunck in result:
        #         if chunck["choices"][0]["finish_reason"] != None:
        #             data = "[DONE]"
        #         else:
        #             try:
        #                 data = chunck["choices"][0]["delta"]["content"]
        #                 yield data
        #             except:
        #                 pass
        # except Exception as e:
        #     yield str(e)
        try:
            result = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo", messages=messages, stream=False, **request_para
            )
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return str(e)


async def main(page: ft.Page):
    async def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Tab" and new_message.value == "":
            new_message.value = "您好，请问怎么称呼您？我是医生"
            await page.update_async()
            await new_message.focus_async()

        if e.ctrl and e.key == "B":
            await show_or_hidden_nav_rail(None)
            await page.update_async()

        if e.ctrl and e.key == "J":
            await new_message.focus_async()

    async def on_click_nav_rail_leading(e):
        chat.controls = [
            ft.Column(
                [
                    ft.Markdown(
                        home_message,
                        selectable=False,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                        on_tap_link=lambda e: page.launch_url(e.data),
                    )
                ],
                alignment="center",
                width=int(PAGE_WIDTH * WIDTH_PERCENT),
            )
        ]
        new_message.visible = False
        clear_record_btn.visible = False
        send_message_btn.visible = False

        nav_rail.selected_index = None
        await page.update_async()

    async def change_theme(e):
        now_theme_mode = await page.client_storage.get_async("theme_mode")
        if now_theme_mode == "dark":
            page.theme_mode = "light"
            await page.client_storage.set_async("theme_mode", "light")

        elif now_theme_mode == "light":
            page.theme_mode = "dark"
            await page.client_storage.set_async("theme_mode", "dark")

        await page.update_async()

    async def close_dlg(e):
        settings_dlg_modal.open = False
        await page.update_async()

    async def about_setting(e):
        page.dialog = settings_dlg_modal
        settings_dlg_modal.open = True
        await page.update_async()

    async def new_message_textfield_on_blur(e):
        if page.height > page.width:
            page.appbar.visible = True
            await page.update_async()

    async def activate_new_message_textfiled(e):
        if page.height > page.width:
            """
            当对话过长时，点击输入框，可以自动将聊天记录
            滚动到最下方
            """
            m = ft.Text("")
            chat.controls.append(m)
            await chat.update_async()
            await asyncio.sleep(0.01)
            chat.controls.pop()
            await chat.update_async()

            # 因为只能设置一个事件，
            # 当输入设备的 高 大于 宽，激活输入框的时候，关闭测栏
            # 此功能智能放于此处
            if nav_rail:
                nav_rail.visible = False
                show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_RIGHT
                await page.update_async()

            page.appbar.visible = False
            await page.update_async()

    async def store_and_load_nav_rail_visible_status():
        if await page.client_storage.contains_key_async("nav_rail_visible_status"):
            status = await page.client_storage.get_async("nav_rail_visible_status")
            nav_rail.visible = status
            if status:
                show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_LEFT
            else:
                show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_RIGHT
        else:
            await page.client_storage.set_async(
                "nav_rail_visible_status", nav_rail.visible
            )
        await page.update_async()

    async def show_or_hidden_nav_rail(e):
        if nav_rail.visible:
            nav_rail.visible = False
            show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_RIGHT
            await page.client_storage.set_async(
                "nav_rail_visible_status", nav_rail.visible
            )
        else:
            nav_rail.visible = True
            show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_LEFT
            await page.client_storage.set_async(
                "nav_rail_visible_status", nav_rail.visible
            )
        await page.update_async()

    async def add_notification():
        records = await page.client_storage.get_async("p")
        if len(records[nav_rail.selected_index]) == 0:
            chat.controls.append(
                ft.Column(
                    [
                        ft.Markdown(
                            notification,
                            selectable=False,
                            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                            on_tap_link=lambda e: page.launch_url(e.data),
                        )
                    ],
                    alignment="center",
                    width=int(PAGE_WIDTH * WIDTH_PERCENT),
                )
            )
            await chat.update_async()

    async def get_last_five_turn_messages():
        # 最初设计为五轮对话，后来发现不够，就加到10轮
        # 函数名暂且不改了
        records = await page.client_storage.get_async("p")
        records = records[nav_rail.selected_index]
        if len(records) > 20:
            records = records[-20:]
            human_ls = [x[1] for x in records if x[0] == "Human"]
            bot_ls = [x[1] for x in records if x[0] == "Patient"]
            return (human_ls, bot_ls)
        else:
            human_ls = [x[1] for x in records if x[0] == "Human"]
            bot_ls = [x[1] for x in records if x[0] == "Patient"]
            return (human_ls, bot_ls)

    async def steam_build_bot_message(respond, user_message):
        def get_initials(user_name: str):
            return user_name[:1].capitalize()

        def get_avatar_color(user_name: str):
            colors_lookup = [
                ft.colors.PURPLE,
            ]
            return colors_lookup[hash(user_name) % len(colors_lookup)]

        stream_message = ft.Markdown(
            "",
            selectable=False,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: webbrowser.open(e.data),
            # width=int(PAGE_WIDTH * WIDTH_PERCENT),
        )

        bot_message_view = ft.Row(
            controls=[
                ft.CircleAvatar(
                    content=ft.Text(get_initials(BOT_NAME)),
                    color=ft.colors.WHITE,
                    bgcolor=get_avatar_color(BOT_NAME),
                ),
                ft.Column(
                    [
                        # ft.Text("Patient", weight="bold"),
                        stream_message,
                    ],
                    width=int(page.width * WIDTH_PERCENT),
                    tight=True,
                    spacing=5,
                    alignment="start",
                ),
            ],
            vertical_alignment="center",
            alignment="start",
        )
        chat.controls.append(bot_message_view)
        await chat.update_async()

        for x in respond:
            stream_message.value += x
            await stream_message.update_async()
            # 如果使用OhmyGPT的话，必须使用暂停一下，才能有 伪流式 输出
            await asyncio.sleep(0.04)

        await activate_new_message_textfiled(None)  # to scroll to the bottom

        # 需要让 Human 在 bot之上， 以防消息的顺序出现错乱
        # 之所以放在此处，是因为：为了流式输出消息，必须在流式输出完成后才能更新 bot 聊天的记录
        await update_local_record("Human", user_message, "user_message")
        await update_local_record("Patient", stream_message.value, "bot_message")

    async def up_width_info(e):
        global PAGE_WIDTH
        PAGE_WIDTH = page.width
        if not await page.client_storage.contains_key_async("page_width"):
            await page.client_storage.set_async("page_width", page.width)

        await page.update_async()

    async def switch_to_px(e):
        new_message.visible = True
        clear_record_btn.visible = True
        send_message_btn.visible = True

        # await chat.clean_async()
        chat.controls = []
        await page.update_async()

        records = await page.client_storage.get_async("p")
        for record in records[nav_rail.selected_index]:
            await on_message(Message(*record))

        await add_notification()
        await chat.update_async()

    async def clear_record_click(e):
        records = await page.client_storage.get_async("p")
        records[nav_rail.selected_index] = []
        await page.client_storage.set_async("p", records)
        await chat.clean_async()
        await chat.update_async()
        await add_notification()

    async def get_respond(user_message):
        recent_message = await get_last_five_turn_messages()
        bot_respond = await Bot.get_respond(
            user_message, *recent_message, nav_rail.selected_index
        )
        return bot_respond

    # async def get_respond(user_message):
    #     recent_message = await get_last_five_turn_messages()
    #     bot_respond = None
    #     async for respond in Bot.get_respond(
    #         user_message, *recent_message, nav_rail.selected_index
    #     ):
    #         bot_respond = respond
    #     return bot_respond

    async def update_local_record(user_type, user_message, message_type):
        record: list = await page.client_storage.get_async("p")
        record[nav_rail.selected_index].append((user_type, user_message, message_type))
        await page.client_storage.set_async("p", record)

    async def send_message_click(e):
        if new_message.value != "":
            # 在响应前清除，防止重复输入
            user_message = new_message.value
            new_message.value = ""
            await new_message.focus_async()

            # 如果是当前会话中的第一条消息，就删除公告
            if len(chat.controls) == 1:
                await chat.clean_async()
                await chat.update_async()

            await on_message(
                Message(
                    HUMAN_NAME,
                    user_message,
                    message_type="user_message",
                )
            )

            bot_respend = await get_respond(user_message)
            await steam_build_bot_message(bot_respend, user_message)
            await page.update_async()

    async def on_message(message: Message):
        if message.message_type == "user_message":
            m = UserMessage(message, page.width)
        elif message.message_type == "bot_message":
            m = BotMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.BLACK45, size=12)
        chat.controls.append(m)
        await page.update_async()

    #### —————————————————— 页面相关属性设置 ———————————————————————— ###
    page.title = "Doctor Emulator"
    page.on_resize = up_width_info
    page.on_keyboard_event = on_keyboard
    page.horizontal_alignment = "stretch"

    page.session.set("user_name", "Human")
    page.session.set("bot_name", "Patient")
    page.theme = ft.Theme(use_material3=True)

    if await page.client_storage.contains_key_async("theme_mode"):
        page.theme_mode = await page.client_storage.get_async("theme_mode")
    else:
        await page.client_storage.set_async("theme_mode", "light")

    page.appbar = ft.AppBar(
        title=ft.Row(
            [ft.Icon(ft.icons.LOCAL_HOSPITAL_OUTLINED), ft.Text("Doctor Simulator")]
        ),
        actions=[
            ft.IconButton(ft.icons.LIGHTBULB, on_click=change_theme, tooltip="点击改变主题"),
            ft.IconButton(
                ft.icons.DELETE, on_click=clear_record_click, tooltip="点击清除聊天记录"
            ),
        ],
        toolbar_height=40,
    )

    # AlertDialog for Setting
    settings_dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("设置"),
        content=ft.Column(
            [
                ft.Text("免责声明\n本站病人纯属虚构，\n与现实中的人物无任何联系，\n请在使用过程中遵守法律法规。", color="red"),
            ],
            alignment="center",
        ),
        actions=[
            ft.TextButton("Close", on_click=close_dlg),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e: print("....... close dlg ......"),
    )

    # Navigation Rail
    nav_rail = ft.NavigationRail(
        group_alignment=-0.5,
        leading=ft.IconButton(
            icon=ft.icons.HOME,
            tooltip="Home",
            on_click=on_click_nav_rail_leading,
        ),
        label_type=ft.NavigationRailLabelType.ALL,
        selected_index=0,
        destinations=[
            ft.NavigationRailDestination(icon=ft.icons.MAN, label="P1"),
            ft.NavigationRailDestination(icon=ft.icons.MAN, label="P2"),
            ft.NavigationRailDestination(icon=ft.icons.MAN, label="P3"),
        ],
        min_width=120,
        expand=1,
        on_change=switch_to_px,
        trailing=ft.IconButton(
            icon=ft.icons.SETTINGS_APPLICATIONS,
            tooltip="Settings",
            on_click=about_setting,
        ),
        visible=False,
    )

    # Chat messages
    chat = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )

    # A new message entry form
    new_message = ft.TextField(
        hint_text="您好，请问怎么称呼您？我是医生XX",
        # autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
        on_focus=activate_new_message_textfiled,
        on_blur=new_message_textfield_on_blur,
    )

    clear_record_btn = ft.IconButton(
        icon=ft.icons.DELETE,
        tooltip="Clear chat",
        on_click=clear_record_click,
    )

    send_message_btn = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        tooltip="Send message",
        on_click=send_message_click,
    )

    # the button on show or hidden navigation rail
    show_ro_hidden_nav_rail_button = ft.IconButton(
        icon=ft.icons.KEYBOARD_ARROW_RIGHT,
        tooltip="Show/Hidden Navigation Rail",
        on_click=show_or_hidden_nav_rail,
    )

    # Add everything to the page

    await page.add_async(
        ft.Row(
            [
                nav_rail,
                ft.VerticalDivider(width=1),
                ft.Column(
                    [
                        ft.Container(
                            content=chat,
                            border=ft.border.all(1, ft.colors.OUTLINE),
                            border_radius=5,
                            padding=10,
                            expand=True,
                        ),
                        ft.Row(
                            [
                                show_ro_hidden_nav_rail_button,
                                new_message,
                                send_message_btn,
                            ]
                        ),
                    ],
                    expand=9,
                ),
            ],
            expand=True,
        ),
    )
    await page.update_async()

    # 测试时清除 localStorage
    # await page.client_storage.clear_async()

    # 当完成页面布局是，立马更新页面宽度
    # 以防生成的消息为预设的状态
    await up_width_info(None)

    # 如果页面的宽大于高，则将导航栏设置为默认显示
    if page.width > page.height:
        nav_rail.visible = True
        await page.update_async()

    # 通常是为了移动端
    if page.width < page.height:
        new_message.hint_style = ft.TextStyle(size=14)
        await page.update_async()

    # ****************** 下面部分，尽量集中和 page.client_storage 相关的配置

    if await page.client_storage.contains_key_async("tip_input"):
        pass
    else:
        new_message.value = "您好，请问怎么称呼您？我是医生XX"
        await page.client_storage.set_async("tip_input", False)

    #### ----------  如果读取不到已经存在聊天的记录，就初始化记录列表，以供存储和读取    ----------- #####
    if await page.client_storage.contains_key_async("p"):
        records = await page.client_storage.get_async("p")
        for record in records[nav_rail.selected_index]:
            try:
                await on_message(Message(*record))
            except:
                await clear_record_click()
    else:
        await page.client_storage.set_async(
            "p", [[] for _ in range(len(nav_rail.destinations))]
        )

    # 如果动态添加预设prompt之bot数量，可能会导致聊天记录丢失
    # 因为原有聊天记录的列表长度与增加后不相符，所以需要解决
    # 这里扩展聊天记录列表的长度，应该可以解决
    if len(await page.client_storage.get_async("p")) < len(nav_rail.destinations):
        p = await page.client_storage.get_async("p")
        n = len(nav_rail.destinations) - len(p)
        p += [[] for _ in range(n)]
        await page.client_storage.set_async("p", p)

    ### ----------- some functions will be execute in after the UI was built ------------- #####
    # add Notification
    await add_notification()

    # 为了防止误加载通知，智能放在加载通知后面
    # 如果是第一次访问，则展示首页信息
    if not await page.client_storage.contains_key_async("first_visitor"):
        await page.client_storage.set_async("first_visitor", True)
    if await page.client_storage.get_async("first_visitor"):
        await on_click_nav_rail_leading(None)
        await page.client_storage.set_async("first_visitor", False)

    await store_and_load_nav_rail_visible_status()


ft.app(target=main, view=ft.WEB_BROWSER, host="0.0.0.0", port=8550, assets_dir="assets")
