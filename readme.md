# The Wiki Game AI

This is a Python script that plays "The Wiki Game" using Pyppeteer and gpt4free. The goal of the game is to navigate from one Wikipedia page to another by clicking on links on each page, with the goal of reaching a target page. If a link is not available, the script prompts the language model to suggest a link to click. The script uses asyncio to handle the asynchronous nature of the web browser.

## Requirements

- Python 3.7 or later
- Pyppeteer
- gpt4free

## Installation

1. Clone the repository:
`git clone https://github.com/ncky/wiki-game-ai.git`
2. Install the dependencies:
`pip install pyppeteer gpt4free`

## Usage

To start the game, run:
`python main.py`

The script will open a web browser and navigate to "The Wiki Game" website. Once the game starts, it will attempt to navigate from the starting page to the target page by clicking on links on each Wikipedia page. If a link is not available, the script will prompt the language model to suggest a link to click.

The game will end once the target page is reached or if no more links are available to click. The starting page, target page, and links clicked during the game will be printed to the console.
