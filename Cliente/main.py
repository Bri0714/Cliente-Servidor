import flet as ft
from Vista.vista import ClienteVista

def main(page: ft.Page):
    page.title = "Gestión de Clientes"
    ClienteVista(page)

ft.app(target=main)
