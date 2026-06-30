#!/usr/bin/env python3

import typer

app = typer.Typer(help="Herramienta que permite cambiar la MAC del dispositivo.")


@app.command()
def main():
    pass


if __name__ == "__main__":
    app()
