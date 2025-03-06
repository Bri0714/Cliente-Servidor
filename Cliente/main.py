import flet as ft
from Vista.vista import ClienteVista

def main(page: ft.Page):
    page.title = "Gestión de Clientes"
    cliente_vista = ClienteVista(page)
    page.on_close = lambda e: (
        cliente_vista.controlador.liberar_tarjeta(cliente_vista.controlador.tarjeta_actual)
        if cliente_vista.controlador.tarjeta_actual is not None
        else None
    )

ft.app(target=main)
