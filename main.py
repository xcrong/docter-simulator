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
import flet as ft
import openai
import webbrowser

from bot import prompts, request_para
from info import notification, home_message

import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.getLogger("flet").setLevel(logging.WARN)


openai.api_key = os.getenv("OHMYGPT_API_KEY")
openai.api_base = os.getenv("OHMYGPT_API_BASE_CN")

# PAGE_WIDTH = 700
WIDTH_PERCENT = 0.7
PAGE_PLATFORM = ""


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
    def get_respond(user_message, human_records: list, bot_records, p_index):
        l1 = [{"role": "user", "content": x} for x in human_records]
        l2 = [{"role": "assistant", "content": x} for x in bot_records]

        exist_message_ls = [x for pair in zip(l1, l2) for x in pair]

        messages = (
            [{"role": "system", "content": prompts[p_index]}]
            + exist_message_ls
            + [{"role": "user", "content": user_message}]
        )
        logging.debug(messages)
        try:
            result = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, stream=True, **request_para
            )
            for chunck in result:
                if chunck["choices"][0]["finish_reason"] != None:
                    data = "[DONE]"
                else:
                    try:
                        data = chunck["choices"][0]["delta"]["content"]
                        yield data
                        # t += data
                    except:
                        # print(chunck['choices'][0]['delta']['role'])
                        pass
        except Exception as e:
            yield str(e)


def main(page: ft.Page):
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Tab" and new_message.value == "":
            new_message.value = "您好，请问怎么称呼您？我是医生"
            page.update()
            new_message.focus()

        if e.ctrl and e.key == "B":
            show_or_hidden_nav_rail(None)
            page.update()

        if e.ctrl and e.key == "J":
            new_message.focus()

    def on_click_nav_rail_leading(e):
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
        page.update()

    def change_theme(e):
        print()

        now_theme_mode = page.client_storage.get("theme_mode")
        if now_theme_mode == "dark":
            page.theme_mode = "light"
            page.client_storage.set("theme_mode", "light")

        elif now_theme_mode == "light":
            page.theme_mode = "dark"
            page.client_storage.set("theme_mode", "dark")

        page.update()
        logging.debug(
            f"_____________ set themo_mode to: {page.client_storage.get('theme_mode')}"
        )

    def close_dlg(e):
        settings_dlg_modal.open = False
        page.update()

    def about_setting(e):
        print("start settings")
        page.dialog = settings_dlg_modal
        settings_dlg_modal.open = True
        page.update()

    def add_and_remove_an_blank_message(e):
        """
        当对话过长时，点击输入框，可以自动将聊天记录
        滚动到最下方
        """
        m = ft.Text("")
        chat.controls.append(m)
        chat.update()
        time.sleep(0.01)
        chat.controls.pop()
        chat.update()

    def store_and_load_nav_rail_visible_status():
        if page.client_storage.contains_key("nav_rail_visible_status"):
            status = page.client_storage.get("nav_rail_visible_status")
            nav_rail.visible = status
            if status:
                show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_LEFT
            else:
                show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_RIGHT
        else:
            page.client_storage.set("nav_rail_visible_status", nav_rail.visible)
        page.update()

    def show_or_hidden_nav_rail(e):
        if nav_rail.visible:
            nav_rail.visible = False
            show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_RIGHT
            page.client_storage.set("nav_rail_visible_status", nav_rail.visible)
        else:
            nav_rail.visible = True
            show_ro_hidden_nav_rail_button.icon = ft.icons.KEYBOARD_ARROW_LEFT
            page.client_storage.set("nav_rail_visible_status", nav_rail.visible)
        page.update()

    def add_notification():
        if len(page.client_storage.get("p")[nav_rail.selected_index]) == 0:
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
            chat.update()

    def get_last_five_turn_messages():
        records = page.client_storage.get("p")[nav_rail.selected_index]
        if len(records) > 20:
            records = records[-20:]
            human_ls = [x[1] for x in records if x[0] == "Human"]
            bot_ls = [x[1] for x in records if x[0] == "Patient"]
            return (human_ls, bot_ls)
        else:
            human_ls = [x[1] for x in records if x[0] == "Human"]
            bot_ls = [x[1] for x in records if x[0] == "Patient"]
            return (human_ls, bot_ls)

    def steam_build_bot_message(respond, user_message):
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
                    content=ft.Text(get_initials("Patient")),
                    color=ft.colors.WHITE,
                    bgcolor=get_avatar_color("Patient"),
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
        chat.update()

        for x in respond:
            stream_message.value += x
            stream_message.update()
            # 如果使用OhmyGPT的话，必须使用暂停一下，才能有 伪流式输出
            time.sleep(0.03)

        add_and_remove_an_blank_message(None)  # to scroll to the bottom

        # 需要让 Human 在 bot之上， 以防消息的顺序出现错乱
        # 之所以放在此处，是因为：为了流式输出消息，必须在流式输出完成后才能更新 bot 的记录
        update_local_record("Human", user_message, "user_message")
        update_local_record("Patient", stream_message.value, "bot_message")

    def up_width_info(e):
        global PAGE_WIDTH
        PAGE_WIDTH = page.width
        if not page.client_storage.contains_key("page_width"):
            page.client_storage.set("page_width", page.width)
        logging.debug(f"Now Page Width: {page.width}")
        page.update()

    def switch_to_px(e):
        new_message.visible = True
        clear_record_btn.visible = True
        send_message_btn.visible = True

        chat.controls.clear()
        for record in page.client_storage.get("p")[nav_rail.selected_index]:
            on_message(Message(*record))

        add_notification()
        page.update()

    def clear_record_click(e):
        record = page.client_storage.get("p")
        record[nav_rail.selected_index] = []
        page.client_storage.set("p", record)
        chat.controls.clear()
        chat.update()
        # logging.debug(
        #     f"清除了索引为{nav_rail.selected_index}的记录,现在是：{page.client_storage.get('p')}"
        # )
        add_notification()

    def get_respond(user_message):
        bot_respond = Bot.get_respond(
            user_message, *get_last_five_turn_messages(), nav_rail.selected_index
        )
        return bot_respond

    def update_local_record(user_type, user_message, message_type):
        record: list = page.client_storage.get("p")
        record[nav_rail.selected_index].append((user_type, user_message, message_type))
        logging.debug(
            f"Add {user_type} {user_message} {message_type} to index {nav_rail.selected_index}"
        )
        logging.debug(f"现在是：{page.client_storage.get('p')}")
        page.client_storage.set("p", record)

    def send_message_click(e):
        if new_message.value != "":
            # 在响应前清除，防止重复输入
            user_message = new_message.value
            new_message.value = ""
            new_message.focus()

            # 如果是当前会话中的第一条消息，就删除公告
            if len(chat.controls) == 1:
                chat.controls = []
                chat.update()

            on_message(
                Message(
                    page.session.get("user_name"),
                    user_message,
                    message_type="user_message",
                )
            )

            bot_respend = get_respond(user_message)
            steam_build_bot_message(bot_respend, user_message)
            page.update()

    def on_message(message: Message):
        logging.debug(
            f"__________________________ {page.platform}: {page.width} ___________________________"
        )
        if message.message_type == "user_message":
            m = UserMessage(message, page.width)
        elif message.message_type == "bot_message":
            m = BotMessage(message)
        elif message.message_type == "login_message":
            m = ft.Text(message.text, italic=True, color=ft.colors.BLACK45, size=12)
        chat.controls.append(m)
        page.update()

    #### —————————————————— 页面相关属性设置 ———————————————————————— ###
    page.title = "Doctor Emulator"
    page.on_resize = up_width_info
    page.on_keyboard_event = on_keyboard
    page.horizontal_alignment = "stretch"

    page.session.set("user_name", "Human")
    page.session.set("bot_name", "Patient")
    page.theme = ft.Theme(use_material3=True)

    if page.client_storage.contains_key("theme_mode"):
        page.theme_mode = page.client_storage.get("theme_mode")
        logging.debug(
            f"________________在LocalStorage中发现theme_mode, 已设置为{page.client_storage.get('theme_mode')}"
        )
    else:
        page.client_storage.set("theme_mode", "light")
        logging.debug(
            f"________________在LocalStorage中未发现theme_mode, 已设置为{page.client_storage.get('theme_mode')}"
        )

    # AlertDialog for Setting
    settings_dlg_modal = ft.AlertDialog(
        modal=True,
        title=ft.Text("设置"),
        content=ft.Column(
            [
                ft.Text("本站病人纯属虚构，\n与现实中的人物无任何联系，\n请在使用过程中遵守法律法规", color="red"),
                ft.ElevatedButton(text="Change Theme", on_click=change_theme),
                # ft.ElevatedButton(
                #     text="清除所有信息",
                #     tooltip="包括本地存储的聊天记录、主题状态、导航栏状态等",
                #     on_click=lambda _: page.client_storage.clear(),
                # ),
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
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_message_click,
        on_focus=add_and_remove_an_blank_message,
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

    page.add(
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
                                clear_record_btn,
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
    page.update()

    # 当完成页面布局是，立马更新页面宽度
    # 以防生成的消息为预设的状态
    up_width_info(None)

    # 如果页面的宽大于高，则将导航栏设置为默认显示
    if page.width > page.height:
        nav_rail.visible = True
        page.update()

    # ****************** 下面部分，尽量集中和 page.client_storage 相关的配置

    if page.client_storage.contains_key("tip_input"):
        pass
    else:
        new_message.value = "您好，请问怎么称呼您？我是医生XX"
        page.client_storage.set("tip_input", False)

    #### ----------  如果读取不到已经存在聊天的记录，就初始化记录列表，以供存储和读取    ----------- #####
    if page.client_storage.contains_key("p"):
        for record in page.client_storage.get("p")[nav_rail.selected_index]:
            on_message(Message(*record))
    else:
        page.client_storage.set("p", [[] for _ in range(len(nav_rail.destinations))])

    logging.debug(f"页面开始加载时：{page.client_storage.get('p')}")
    # 如果动态添加预设prompt之bot数量，可能会导致聊天记录丢失
    # 因为原有聊天记录的列表长度与增加后不相符，所以需要解决
    # 这里扩展聊天记录列表的长度，应该可以解决
    if len(page.client_storage.get("p")) < len(nav_rail.destinations):
        p = page.client_storage.get("p")
        n = len(nav_rail.destinations) - len(p)
        p += [[] for _ in range(n)]
        page.client_storage.set("p", p)

    ### ----------- some functions will be execute in after the UI was built ------------- #####
    # add Notification
    add_notification()

    # 为了防止误加载通知，智能放在加载通知后面
    # 如果是第一次访问，则展示首页信息
    if not page.client_storage.contains_key("first_visitor"):
        page.client_storage.set("first_visitor", True)
    if page.client_storage.get("first_visitor"):
        on_click_nav_rail_leading(None)
        page.client_storage.set("first_visitor", False)

    store_and_load_nav_rail_visible_status()


ft.app(target=main, view=ft.WEB_BROWSER, host="0.0.0.0", port=8550, assets_dir="assets")
