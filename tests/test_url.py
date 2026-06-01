from app.url_analyzer import analyze
def test_ip(): assert analyze("http://192.168.1.1/login")["score"] > 0
def test_brand(): assert any("Brand" in r for r in analyze("http://paypal.fake.tld")["reasons"])
