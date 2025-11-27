from http.cookies import SimpleCookie

class HttpContext:
    def __init__(self, headers: dict):
        self.ray = headers.get("cf-ray")

        # use authenticated email as user identity
        self.email = headers.get("cf-access-authenticated-user-email")

        cookie = SimpleCookie()
        cookie.load(headers.get("cookie", ""))
        # one cloudflare login session (may be multiple windows)
        self.session = cookie.get("CF_AppSession")

        # metadata
        self.agent = headers.get("user-agent")
        self.ip = headers.get("cf-connecting-ip")
        self.country = headers.get("cf-ipcountry")

    def json(self) -> dict:
        return {
            "email": self.email,
            "ray": self.ray,
            "session": self.session,
            "agent": self.agent,
            "ip": self.ip,
            "country": self.country
        }

    def __repr__(self):
        return f"HttpContext(email={self.email}, ray={self.ray}, agent={self.agent}, ip={self.ip}, country={self.country}, session={self.session})"

    def __str__(self):
        return repr(self)