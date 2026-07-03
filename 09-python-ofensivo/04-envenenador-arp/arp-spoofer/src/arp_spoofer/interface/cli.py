#!/usr/bin/env python3

import typer

from arp_spoofer.core import scan

app = typer.Typer()


@app.command()
def main(
    target: str = typer.Option(
        ..., "-t", "--target", help="Host / Rango de IP a escanear"
    )
):
    scan(target)


if __name__ == "__main__":
    app()
