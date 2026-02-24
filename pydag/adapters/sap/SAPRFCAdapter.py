#from pyrfc import Connection


class SAPRFCAdapter:
    def __init__(
        self,
        user,
        password,
        ashost,
        sysnr,
        client,
        lang="EN"
    ):
        self.conn = Connection(
            user=user,
            passwd=password,
            ashost=ashost,
            sysnr=sysnr,
            client=client,
            lang=lang
        )

    def call(self, function_name, **params):
        return self.conn.call(function_name, **params)

    def close(self):
        self.conn.close()