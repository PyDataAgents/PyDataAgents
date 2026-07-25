import pytest
import resend
import configparser

def test_resend_simple_mail():

    config = configparser.ConfigParser()
    config.read("config.ini")
    if not config.has_section("RESEND"):
        pytest.skip("No [RESEND] section in config.ini")
        
    resend.api_key = config["RESEND"]["API_KEY"]

    r = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": config["RESEND"]["TEST_MAIL"],
        "subject": "Hello World",
        "html": "<p>Congrats on sending your <strong>first email</strong>!</p>"
    })
