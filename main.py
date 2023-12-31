import time
from DrissionPage import ChromiumPage
from DrissionPage.chromium_element import ChromiumElement
from DrissionPage.commons.by import By
from DrissionPage.easy_set import set_headless
from DrissionPage.errors import ElementLossError


def check_logged_in():
    global page

    if page.ele((By.XPATH, '//a[@data-testid="signupButton"]')):
        print('Please sign in to Twitter and then re-run the script.')
        return False
    return True


def block_poster(post: ChromiumElement):
    global blocked
    global page

    # scroll the ad into view
    post.run_js('this.scrollIntoView(true)')
    page.scroll.up(150)   # in case we went too far
    # Get advertiser's handle for logging purposes
    ad_handle = post.ele((By.XPATH, '//div[@data-testid="User-Name"]')).ele((By.XPATH, '//a[@href]')).attr('href')
    # Now click the post menu (three dots)
    post.ele((By.XPATH, '//div[@data-testid="caret"]')).click()
    time.sleep(0.5)   #hol'up
    # Okay, now click block from the post menu
    menu = page.ele((By.XPATH, '//div[@data-testid="Dropdown"]'))
    menu.ele((By.XPATH, '//div[@data-testid="block"]')).click()
    # Yes, we are sure about blocking them.
    block = page.ele((By.XPATH, '//div[@data-testid="confirmationSheetDialog"]')).ele(
        (By.XPATH, '//div[@data-testid="confirmationSheetConfirm"]'))
    ad_handle = '@' + ad_handle.strip('https://twitter.com/')
    print(f'Blocked {ad_handle} - {blocked+1}')
    block.click()
    blocked += 1


def find_ads():
    global last_post
    global page

    posts = page.eles('tag:article', timeout=1)
    if len(posts) < 1:
        print('No posts found') 
        page.get('https://www.x.com')
        time.sleep(3)
        last_post = None
        return
    if last_post is not None:
        if last_post.inner_html == posts[-1].inner_html:
            print('Content stopped loading')
            page.get('https://www.x.com')
            time.sleep(3)
            last_post = None
            return
    last_post = posts[-1]
    for post in posts:
        ad = False
        try:
            spans = post.eles('tag:span')
        except ElementLossError:
            continue
        for span in spans:
            if span.inner_html == 'Ad':
                ad = True
        if ad:
            block_poster(post)


#amount = int(input('Block how many ads? '))
set_headless(False)
page = ChromiumPage()
page.get('https://www.x.com')
log_status = check_logged_in()   # Check if user is logged in
if not log_status:
    exit(0)
blocked = 0
last_post = None
#while blocked < amount:
while True:
    page.clear_cache(cookies=False)
    find_ads()
    page.scroll.down(750)
    time.sleep(0.5)
