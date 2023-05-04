import asyncio
from pyppeteer import launch
from gpt4free import theb
import re
import random

async def get_game_info(page):
    # Get the starting point of the game
    starting_point = await page.querySelectorEval('body > app-root > app-group > div > div > div > div.container.my-4 > div > div.col-lg-6.mb-4.pb-6.wgg-round-challenge.box-background > div > div > div:nth-child(2) > div > div > div.col-12.wgg-article-link', 'el => el.textContent')

    # Get the ending point of the game
    ending_point = await page.querySelectorEval('body > app-root > app-group > div > div > div > div.container.my-4 > div > div.col-lg-6.mb-4.pb-6.wgg-round-challenge.box-background > div > div > div:nth-child(3) > div > div > div.col-12.wgg-article-link', 'el => el.textContent')

    return starting_point, ending_point

async def get_links(page):
    links = []
    link_elements = await page.querySelectorAll('a')
    for link_element in link_elements:
        is_visible = await page.evaluate('(element) => element.offsetParent !== null', link_element)
        is_html_element = await page.evaluate('(element) => element instanceof HTMLElement', link_element)
        if is_visible and is_html_element:
            href = await page.evaluate('(element) => element.getAttribute("href")', link_element)
            text = await page.evaluate('(element) => element.textContent', link_element)
            links.append({'href': href, 'text': text})
    return links

async def click_link_by_page_name(links, page, page_name):
    for link in links:
        if page_name in link['text'] and '/wiki/' in link['href']:
            href = link['href']
            print(f"Clicking \'{page_name}\' [{href}]")
            await page.click(f'a[href="{href}"]')
            return page_name
    print(f"Link not found({page_name})")
    return False

async def link_decider(links, current_page, ending_page):
    link_texts = ""

    for link in links:
        if (ending_page == link['text'] ):
            return ending_page['text']
        if len(link_texts.splitlines()) < 100: #only 100 options for ai
            if ('/wiki/' in link['href'] 
                and len(link['text']) > 1
                and not re.match(r'^\d+\.', link['text'])
                and not link['href'].startswith('#')
                and not link['href'].startswith('/wiki/File:')):
                link_texts += f"\"{link['text']}\"\n"
    
    print(f"asking ai about {len(link_texts.splitlines())} links..")
    #prompt an llm to decide for us
    prompt = f"we are playing a game where you need to navigate from one wikipedia page to another.\n\
            the current page we are on is \'{current_page}\', our goal page is \'{ending_page}\' \n\
            this is a list of links that you can choose from to try and get closer to the ending page:\n\
            {link_texts}\
            you must only respond with a link that is available on the current page.\n\
            your choice:"
    # print(prompt)
    response = ""
    # print("bot response")
    for token in theb.Completion.create(prompt=prompt):
        response += token
    print(f"response: {response}")
    selected_link = response
    matches = re.findall(r'"([^"]*)"', response)
    
    for match in matches:
        if match in link_texts.splitlines():
            selected_link = match
            print("re")
    
    for link in links: 
        if selected_link == link:
            return link
    
    return random.choice(links)['text'] #return random link if ai doesnt respond well
        
    
    

async def start_game():
    browser = await launch(headless=False)
    # Get the first page in the list of open pages in the browser
    page = (await browser.pages())[0]
    await page.goto('https://www.thewikigame.com/group')
    await page.waitForSelector('.btn-primary')

    await page.click('.btn-primary')

    # Wait for the real "Join Game" button to become available
    await page.waitForSelector('#playNowButton')
    
    # Get the game info before clicking the "Join Game" button
    starting_point, ending_point = await get_game_info(page)
    print(f"{starting_point} -> {ending_point}")

    # Click the "Join Game" button
    await page.click('#playNowButton')

    game_running = True
    current_page = starting_point
    while game_running:
        await page.waitForNavigation()
        try:
            await page.waitForSelector('app-round > h2')
        except:
            game_running = False
        # Get the links on the wiki page
        links = await get_links(page)
        print(f"links on page: {len(links)}")
        selected_link = await link_decider(links, current_page, ending_point)
        # Click on the ending point page
        current_page = await click_link_by_page_name(links, page, selected_link) #if link click fails, end the game
        if current_page is False:
            game_running = False
        
    input("Press Enter to exit...")
    await browser.close()
    
    return starting_point, ending_point, links

asyncio.get_event_loop().run_until_complete(start_game())