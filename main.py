import flet as ft
import os
import yaml
import functools

def notify_decorator(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        result = await func(*args, **kwargs)
        self = args[0]
        if hasattr(self.page, 'notify_message'):
            if self.page.notify_message:
                self.page.snack_bar.content = ft.Text(self.page.notify_message)
                self.page.snack_bar.open = True
                self.page.notify_message = None
                await self.page.update_async()
        return result
    return wrapper

class Subject(ft.UserControl):
    def __init__(self, content, subject_delete):
        super().__init__()
        self.content = content
        self.subject_delete = subject_delete
    
    def temp_func(self, e):
        return True
    
    async def delete_clicked(self, e):
        await self.subject_delete(self)

    async def copy_clicked(self, e):
        self.page.notify_message = "Copied to clipboard!"
        await self.page.set_clipboard_async(self.content)
        await self.update_async()

    @notify_decorator
    async def update_async(self):
        await super().update_async()

    def build(self):
        self.view = ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                    ft.Container(
                        content=ft.Text(self.content),
                        margin=0,
                        padding=2,
                        alignment=ft.alignment.center_left,
                        border_radius=0,
                        ink=True,
                        on_click=self.copy_clicked,
                        data=self.content,
                        col={"sm": 10},
                    ),
                    ft.Row([
                            ft.IconButton(
                                icon=ft.icons.COPY,
                                tooltip="Copy prompt",
                                on_click=self.copy_clicked,
                            ),
                            ft.IconButton(
                                ft.icons.DELETE_OUTLINE,
                                tooltip="Delete prompt",
                                on_click=self.delete_clicked,
                            )],
                        col={"sm": 2},
                    )
                ])
        return ft.Column(controls=[self.view])

class AiPrompt(ft.UserControl):
    yaml_data = dict()
    current_path = os.getcwd()
    settings_loaded = False

    @notify_decorator
    async def update_async(self):
        await super().update_async()

    async def temp_func(self, e):
        return True
    
    async def load_settings(self, e):
        self.page.notify_message = "Settings file missing!"
        if os.path.isfile(self.current_path+'/promptmaker.yml'):
            with open(self.current_path+"/promptmaker.yml", 'r') as stream:
                yaml_data = yaml.safe_load(stream)
                yaml_prefix = yaml_data['settings']['prefix']
                self.prefix.value = yaml_prefix
                yaml_suffix = yaml_data['settings']['suffix']
                self.suffix.value = yaml_suffix
                self.page.notify_message = "Settings loaded!"
        await self.update_async()

    async def save_settings(self, e):
        yaml_data = dict()
        yaml_data['settings'] = dict()
        yaml_data['settings']['prefix'] = self.prefix.value
        yaml_data['settings']['suffix'] = self.suffix.value
        with open(self.current_path+"/promptmaker.yml", 'w') as stream:
            stream.write(yaml.safe_dump(yaml_data))
        self.page.notify_message = "Settings saved!"
        await self.update_async()

    async def load_list(self, e):
        self.page.notify_message = "No file to load!"
        if os.path.isfile(self.current_path+'/last_list.txt'):
            with open(self.current_path+'/last_list.txt', 'r') as stream:
                self.subjects.value=stream.read()
            self.page.notify_message = "File loaded!"
        await self.update_async()

    async def save_list(self, e):
        with open(self.current_path+'/last_list.txt', 'w') as stream:
            stream.write(self.subjects.value)
        self.page.notify_message = "File saved!"
        await self.update_async()

    async def generate_clicked(self, e):
        if self.subjects.value:
            for subject_value in self.subjects.value.split('\n'):
                new_prompt = self.prefix.value + ' ' + subject_value + ', ' + self.suffix.value
                subject = Subject(new_prompt, self.subject_delete)
                self.left.controls.append(subject)
            await self.update_async()

    async def clear_clicked(self, e):
        self.left.controls.clear()
        self.page.notify_message = "Generated list cleared!"
        await self.update_async()

    async def subject_delete(self, subject):
        self.left.controls.remove(subject)
        self.page.notify_message = "Subject deleted!"
        await self.update_async()

    def build(self):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("AiPrompt"),
            open=True
        )

        self.left = ft.Column(
            scroll=ft.ScrollMode.ALWAYS,
            height=600
        )
        self.left_c = ft.Container(
            self.left,
            col={"sm": 8},
        )

        self.prefix = ft.TextField(
            label="Prefix",
            hint_text="high quality sticker logo of",
            value = "illustration of"
        )
        
        self.subjects = ft.TextField(
            label="Paste here the subjects, one per line",
            hint_text="a monkey\na dog\na cat",
            multiline=True,
            max_lines=13
        )

        self.suffix = ft.TextField(
            label="Suffix",
            hint_text="vibrant illustration, stencil, flat white background",
            value="black and white, coloring book style --ar 2:3"
        )
        
        self.right = ft.Column([
            self.prefix,
            self.subjects,
            self.suffix,
            ft.Row([
                ft.Column([
                    ft.ElevatedButton("Generate", on_click=self.generate_clicked),
                    ft.ElevatedButton("Clear", on_click=self.clear_clicked),
                    ft.ElevatedButton("Save Settings", on_click=self.save_settings),
                ]),
                ft.Column([
                    ft.ElevatedButton("Load list", on_click=self.load_list),
                    ft.ElevatedButton("Save list", on_click=self.save_list),
                    ft.ElevatedButton("Load Settings", on_click=self.load_settings),
                ])
                ])
            ]
        )
        self.right_c = ft.Container(
            self.right,
            col={"sm": 4},
        )

        return ft.Column([
                ft.Row([
                    ft.Text("AiPrompt", size=30, weight="bold")
                ]),
                ft.ResponsiveRow(
                    [
                        self.left_c,
                        self.right_c,
                    ]
                )
        ])

async def main(page: ft.Page):
    page.title = "AiPrompt"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE
    await page.add_async(AiPrompt())

ft.app(main)