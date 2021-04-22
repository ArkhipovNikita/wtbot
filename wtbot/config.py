from pydantic import BaseSettings


class Settings(BaseSettings):
    target_uri: str = "https://cgifederal.secure.force.com"
    captcha_img_id: str = (
        "loginPage:SiteTemplate:siteLogin:loginComponent:loginForm:theId"
    )
    captcha_not_loaded: str = "data:image;base64,"
    chrome_driver: str
    media_root: str
