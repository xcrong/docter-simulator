import flet as ft

class Data:
    def __init__(self) -> None:
        self.counter = 0

d = Data()

def main(page: ft.Page):

    page.snack_bar = ft.SnackBar(
        content=ft.Text("Hello, world!"),
        action="Alright!",
    )

    def on_click(e):
        page.snack_bar = ft.SnackBar(ft.Text(f"Hello {d.counter}"))
        page.snack_bar.open = True
        d.counter += 1
        page.update()


    def try_to_close_app_bar(e):
        print(page.appbar)
        page.appbar = None
        page.update()

    page.add(ft.ElevatedButton("Open SnackBar", on_click=on_click))


    the_app_bar = ft.AppBar(
        title=ft.Icon(ft.icons.LOCAL_HOSPITAL_OUTLINED),
        actions=[
            ft.IconButton(ft.icons.SUNNY,on_click=try_to_close_app_bar),
            ft.IconButton(ft.icons.MOOD)
        ]
    )
    page.appbar = the_app_bar

    page.update()

ft.app(target=main)