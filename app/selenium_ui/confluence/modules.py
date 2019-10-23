import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from selenium_ui.conftest import AnyEc, application_url, generate_random_string, print_timing
from util.project_paths import CONFLUENCE_YML

timeout = 10

# TODO consider do not use conftest as utility class and do not import it in modules
APPLICATION_URL = application_url(CONFLUENCE_YML)


def _dismiss_popup(webdriver, *args):
    for elem in args:
        try:
            webdriver.execute_script(f"document.querySelector(\'{elem}\').click()")
        except:
            pass


def login(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):

        @print_timing
        def measure(webdriver, interaction):
            webdriver.get(f'{APPLICATION_URL}/login.action')
            _wait_until(webdriver, EC.visibility_of_element_located((By.ID, 'loginButton')), interaction)

        measure(webdriver, "selenium_login:open_login_page")

        user = random.choice(datasets["users"])
        webdriver.find_element_by_id('os_username').send_keys(user[0])
        webdriver.find_element_by_id('os_password').send_keys(user[1])

        def _setup_page_is_presented():
            elems = webdriver.find_elements_by_id('grow-intro-video-skip-button')
            return True if elems else False

        def _user_setup():
            _wait_until(webdriver, EC.element_to_be_clickable((By.ID, 'grow-intro-video-skip-button')),
                        interaction).click()
            _wait_until(webdriver, EC.element_to_be_clickable((By.CSS_SELECTOR, '.aui-button-link')),
                        interaction).click()
            spaces = _wait_until(webdriver, EC.visibility_of_any_elements_located(
                (By.CSS_SELECTOR, '.intro-find-spaces-space>.space-checkbox')), interaction)
            if spaces:
                spaces[0].click()
            _wait_until(webdriver, EC.element_to_be_clickable((By.CSS_SELECTOR, '.intro-find-spaces-button-continue')),
                        interaction).click()

        @print_timing
        def measure(webdriver, interaction):
            webdriver.find_element_by_id('loginButton').click()
            _wait_until(webdriver, EC.invisibility_of_element_located((By.ID, 'loginButton')),
                        interaction)
            if _setup_page_is_presented():
                _user_setup()
            WebDriverWait(webdriver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'list-container-all-updates')))

        measure(webdriver, "selenium_login:login_and_view_dashboard")  # waits for all updates

    measure(webdriver, 'selenium_login')

    _dismiss_popup(webdriver,
                   ".button-panel-button .set-timezone-button",
                   ".aui-button aui-button-link .skip-onboarding")


def view_page(webdriver, datasets):
    page = random.choice(datasets["pages"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/pages/viewpage.action?pageId={page}')
        WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.ID, 'title-text')))

    measure(webdriver, "selenium_view_page")


def view_blog(webdriver, datasets):
    blog = random.choice(datasets["blogs"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/pages/viewpage.action?pageId={blog}')
        WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.ID, 'title-text')))

    measure(webdriver, "selenium_view_blog")


def view_dashboard(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/dashboard.action#all-updates')
        WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, 'update-items')))

    measure(webdriver, "selenium_view_dashboard")


def create_page(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.find_element(By.ID, "quick-create-page-button").click()
        WebDriverWait(webdriver, timeout).until(EC.element_to_be_clickable((By.ID, "rte-button-publish")))

    measure(webdriver, "selenium_create_page:open_create_page_editor")

    _dismiss_popup(webdriver, "#closeDisDialog")
    populate_page_content(webdriver)

    @print_timing
    def measure(webdriver, interaction):
        webdriver.find_element_by_id("rte-button-publish").click()
        WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.ID, 'title-text')))

    measure(webdriver, "selenium_create_page:save_created_page")


def edit_page(webdriver, datasets):
    page = random.choice(datasets["pages"])[0]

    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/pages/editpage.action?pageId={page}')
        WebDriverWait(webdriver, timeout).until(EC.element_to_be_clickable((By.ID, "rte-button-publish")))

    measure(webdriver, "selenium_edit_page:open_create_page_editor")

    populate_page_content(webdriver)

    @print_timing
    def measure(webdriver, interaction):
        confirmation_button = "qed-publish-button"
        webdriver.find_element_by_id("rte-button-publish").click()
        if webdriver.find_elements_by_id(confirmation_button):
            if webdriver.find_element_by_id('qed-publish-button').is_displayed():
                webdriver.find_element_by_id('qed-publish-button').click()
        _wait_until(webdriver, EC.invisibility_of_element_located((By.ID, 'rte-spinner')), interaction)
        _wait_until(webdriver, AnyEc(EC.presence_of_element_located((By.ID, "title-text")),
                                     EC.presence_of_element_located((By.ID, confirmation_button))
                                     ), interaction)

    measure(webdriver, "selenium_edit_page:save_edited_page")


def create_comment(webdriver, datasets):
    view_page(webdriver, datasets)

    @print_timing
    def measure(webdriver, interaction):
        create_comment_button = webdriver.find_element(By.CSS_SELECTOR, ".quick-comment-prompt")
        webdriver.execute_script("arguments[0].scrollIntoView()", create_comment_button)
        # create_comment_button.click()
        webdriver.execute_script("document.querySelector('.quick-comment-prompt').click()")
        _wait_until(webdriver, EC.invisibility_of_element_located(create_comment_button), interaction)

        _wait_until(webdriver, EC.element_to_be_clickable((By.ID, 'rte-button-publish')), interaction)
        _wait_until(webdriver, EC.frame_to_be_available_and_switch_to_it((By.ID, 'wysiwygTextarea_ifr')), interaction)
        webdriver.find_element_by_id("tinymce").send_keys(f"This is page comment from date {time.time()}")
        webdriver.switch_to.parent_frame()

    measure(webdriver, 'selenium_create_comment:write_comment')

    @print_timing
    def measure(webdriver, interaction):
        webdriver.find_element_by_id("rte-button-publish").click()
        _wait_until(webdriver, EC.visibility_of_element_located((By.CSS_SELECTOR, '.quick-comment-prompt')),
                    interaction)

    measure(webdriver, "selenium_create_comment:save_comment")


def populate_page_content(webdriver):
    WebDriverWait(webdriver, timeout).until(EC.visibility_of_element_located((By.ID, 'content-title')))
    title = "Selenium - " + generate_random_string(10)

    webdriver.find_element_by_id("content-title").clear()
    webdriver.find_element_by_id("content-title").send_keys(title)
    WebDriverWait(webdriver, timeout).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "wysiwygTextarea_ifr")))
    webdriver.find_element_by_id("tinymce").send_keys(generate_random_string(30))
    webdriver.switch_to.parent_frame()


def log_out(webdriver, datasets):
    @print_timing
    def measure(webdriver, interaction):
        webdriver.get(f'{APPLICATION_URL}/logout.action')

    measure(webdriver, "selenium_log_out")


def _wait_until(webdriver, expected_condition, interaction, time_out=timeout):
    message = f"Interaction: {interaction}. "
    ec_type = type(expected_condition)
    if ec_type == AnyEc:
        conditions_text = ""
        for ecs in expected_condition.ecs:
            conditions_text = conditions_text + " " + f"Condition: {str(ecs)} Locator: {ecs.locator}\n"

        message += f"Timed out after {time_out} sec waiting for one of the conditions: \n{conditions_text}"

    elif ec_type == EC.invisibility_of_element_located:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.target}")

    elif ec_type == EC.frame_to_be_available_and_switch_to_it:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.frame_locator}")

    else:
        message += (f"Timed out after {time_out} sec waiting for {str(expected_condition)}. \n"
                    f"Locator: {expected_condition.locator}")

    return WebDriverWait(webdriver, time_out).until(expected_condition, message=message)
