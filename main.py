import flet as ft
import os
import yaml

def main(page: ft.Page):
    yaml_data = dict()
    current_path = os.getcwd()

    page.snack_bar = ft.SnackBar(
        content=ft.Text("Copied to clipboard!"),
    )

    left = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,
        height=600
    )
    left_c = ft.Container(
        left,
        col={"sm": 8},
    )

    prefix = ft.TextField(
        label="Prefix",
        hint_text="high quality sticker logo of",
    )
    
    subjects = ft.TextField(
        label="Paste here the subjects, one per line",
        hint_text="a monkey\na dog\na cat",
        multiline=True,
        max_lines=13
    )

    suffix = ft.TextField(
        label="Suffix",
        hint_text="vibrant illustration, stencil, flat white background",
    )

    def load_settings(e, autoload=False):
        load_from_file = False
        if os.path.isfile(current_path+'/promptmaker.yml'):
            with open(current_path+"/promptmaker.yml", 'r') as stream:
                yaml_data = yaml.safe_load(stream)
                load_from_file = True
        try:
            yaml_prefix = yaml_data['settings']['prefix']
            prefix.value = yaml_prefix
        except:
            prefix.value = "illustration of"
        try:
            yaml_suffix = yaml_data['settings']['suffix']
            suffix.value = yaml_suffix
        except:
            suffix.value = "black and white, coloring book style --ar 2:3"
        if load_from_file:
            page.snack_bar.content = ft.Text("Settings loaded!")
        else:
            page.snack_bar.content = ft.Text("Settings file missing!")
        if not autoload:
            page.snack_bar.open = True
            page.update()

    load_settings(None, True)

    def save_settings(e):
        yaml_data = dict()
        yaml_data['settings'] = dict()
        yaml_data['settings']['prefix'] = prefix.value
        yaml_data['settings']['suffix'] = suffix.value
        with open(current_path+"/promptmaker.yml", 'w') as stream:
            stream.write(yaml.safe_dump(yaml_data))
        page.snack_bar.content = ft.Text("Settings saved!")
        page.snack_bar.open = True
        page.update()

    def to_clip(e):
        page.snack_bar.content = ft.Text("Copied to clipboard!")
        page.snack_bar.open = True
        page.set_clipboard(e.control.data)
        page.update()

    def populate_left(e):
        left.controls.append(
            ft.ResponsiveRow([
                ft.Container(
                    content=ft.Text("Click on a Generated Element to copy the text into the clipboard!"),
                    margin=0,
                    padding=2,
                    alignment=ft.alignment.center_left,
                )
            ])
        )
    populate_left(None)

    def generated_clear(e):
        left.controls.clear()
        populate_left(e)
        page.update()

    def generate_click(e):
        for subject_value in subjects.value.split('\n'):
            new_prompt = prefix.value + ' ' + subject_value + ', ' + suffix.value
            left.controls.append(
                ft.ResponsiveRow([
                    ft.Container(
                        content=ft.Text(new_prompt),
                        margin=0,
                        padding=2,
                        alignment=ft.alignment.center_left,
                        border_radius=0,
                        ink=True,
                        on_click=to_clip,
                        data=new_prompt,
                    )
                ])
            )
            # left.controls.append(ft.ResponsiveRow([
            #     ft.Column([ft.Text(new_prompt)]),
            #     ft.Column([ft.ElevatedButton("copy", on_click=to_clip, data=new_prompt)])
            # ]))
        page.update()

    def load_list(e):
        if os.path.isfile(current_path+'/last_list.txt'):
            with open(current_path+'/last_list.txt', 'r') as stream:
                subjects.value=stream.read()
            page.snack_bar.content = ft.Text("File loaded!")
        else:
            page.snack_bar.content = ft.Text("No file to load!")
        page.snack_bar.open = True
        page.update()

    def save_list(e):
        with open(current_path+'/last_list.txt', 'w') as stream:
            stream.write(subjects.value)
        page.snack_bar.content = ft.Text("File saved!")
        page.snack_bar.open = True
        page.update()


    right = ft.Column([
        prefix,
        subjects,
        suffix,
        ft.Row([
            ft.Column([
                ft.ElevatedButton("Generate", on_click=generate_click),
                ft.ElevatedButton("Clear", on_click=generated_clear),
                ft.ElevatedButton("Save Settings", on_click=save_settings),
            ]),
            ft.Column([
                ft.ElevatedButton("Load list", on_click=load_list),
                ft.ElevatedButton("Save list", on_click=save_list),
                ft.ElevatedButton("Load Settings", on_click=load_settings),
            ])
            ])
        ]
    )
    right_c = ft.Container(
        right,
        col={"sm": 4},
    )

    page.add(
        ft.ResponsiveRow(
            [
                left_c,
                right_c,
            ]
        )
    )

ft.app(target=main)