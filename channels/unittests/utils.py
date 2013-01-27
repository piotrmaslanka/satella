from tempfile import NamedTemporaryFile
from os import unlink

class get_dummy_cert(object):
    """
    Return a file name with a dummy certificate.

    Uses __enter__/__exit__ protocol. This is
    actually part of Satella's public API.

    Example:

        with get_dummy_cert() as dcname:
            ssl.wrap_socket(sock, certfile=dcname)

    """

    def __enter__(self):
        k = NamedTemporaryFile(delete=False)
        k.write("""-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDNOMhd2VoDs4lI
mUP9wirFMF8jWTpy6UHDwCzConkSI5hxO+uxPSbcL9sOdSYqTO4Ee+xZHbUJfh85
zyX/y5LAD+NTN/bHH2lMI7Nn4obRIZBcZIVZ4rB+lkoAsUfZ4tgxySJaCTB4Xsng
60L9PYLXVsTme+T0Yc//HUtuhh2MlblTEqauQDHzxBQJmIdgIvW2M8fLxZkpASCC
ycSnfk+6UIjxl0cjUdvW5ZgfzkC0i/Y7rhFhnfXV317Lid7stohoLk1rphX3rROs
Vy+CnRsBZggMWDKOLHWJJB2F4QaBjt66dgcZk2YTzEHnUzWVDAT4EG164s1iM3iV
orIvFdyPAgMBAAECggEAC5upob1YnRr7qfKZaPIhrzO0PfCfIL7W7HajUYMVLBR9
W/JSu5zE5PGEB4ZS2VOupuxHiybmBZpvs7pm4Ngn/dsoNZ3VxJ+fOiJO1JJ4o72t
R7yb2mC7MP3ZQ77DXKy7I93HpqYcasKZ0rIcAO0IyJts2ciqQ7SAqmKC0MafR0Na
2gJTHkzyFzFtbuy/GXn8FfOVv1ST82QxZcs6KmhdwKW7pgMAf8dxohonVN2/MV8+
AWTBTt9R3Tu3qdhLjNhG8XrImJ/hhFSDmjT4DR+lzErJOfpA6witqf/Bopxm67za
4HCwByCbhj3CA1yhoy0xEqyewWiE3+G2BxObWqSqGQKBgQDwEYVzXLf0yr9T4OMP
Hm8HAd04vsVWZRHInXpAYGcn0AspglT2kzqOTA/cSs2xQbrgbysi7IB5VdvGL+Pq
tbF+5FsHUC78dpiRS4QGGHWHxIAkJDnBXPnuaSTXIFDaYY2Abg2p6FiOixF6s0FI
Cee7hcrz7fFdCly3jNwHYyovowKBgQDa10IgAgqYK3gI/c+kKZh6NQRUs8FCj3DG
C4ag0vdgv9XkUiP2dOLKOW36VCIwEgkidjRuuZPwnkpjZONAK24FUbUouq5n3v9h
zUa/ePQzdTWd93xedRway18VnbSHjIMEki/XgfwF0FLlgwdK/jR/mPch+3ykLaw4
YdFXbPa+JQKBgF8DcD/SSHQ38jVuYi9Pqj2pvTaCOnQRGFLAEOx9uxYEvwY0sQ/O
AXTkIbrcWEB5dU7ycK4n0Ek1dAAiYCA6vP8tveFNGOuOvJ90tdH7yDhtyxGCzOD8
vWZgctY50gY8adaUuA+xB6uS2t4nKAUs9mw/ba3RVJ+wRDXZKBQ8aSvlAoGBAMqZ
WHWLjkVckO86Ev63J5uT86N7GyNE6rHev8+qIC1ozFtplDO5+LAhROjo9RGt0Nkf
t+D+W7D6yoGESEMDMgMopt/DHG27bJEd2y6uit4M2AubsH8+SjugJjI744NOGYmk
0Tfh9fFn8SbcDGdoOjAa7EiAq97PDc7Q+F7I2RIlAoGBAJmvZMCRTpmmEIfyY4ez
1IvJuU0X8ZmWBvKL/R9KuW4HlCu6FKAqXFOSeA1HwRo7hozeEw2us3wZm6epPwtm
vqdZYlaeTydaGMre3kXBEE0dB176A6lWP4QUZhCzrIHURkWgF1MtG4AZ/Pnm1ZYK
4Pv3BDAtAZQN9w0yDRFD/T18
-----END PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
MIIEATCCAumgAwIBAgIJAO/JNhPcfseNMA0GCSqGSIb3DQEBBQUAMIGWMQswCQYD
VQQGEwJQTDESMBAGA1UECAwJTmV2ZXJsYW5kMRUwEwYDVQQHDAxEZWZhdWx0IENp
dHkxHDAaBgNVBAoME0RlZmF1bHQgQ29tcGFueSBMdGQxGDAWBgNVBAMMD1VuaXQg
VGVzdCBDZXJ0LjEkMCIGCSqGSIb3DQEJARYVc29tZXRoaW5nQGV4YW1wbGUuY29t
MB4XDTEzMDEyNzIyMzk1NFoXDTE0MDEyNzIyMzk1NFowgZYxCzAJBgNVBAYTAlBM
MRIwEAYDVQQIDAlOZXZlcmxhbmQxFTATBgNVBAcMDERlZmF1bHQgQ2l0eTEcMBoG
A1UECgwTRGVmYXVsdCBDb21wYW55IEx0ZDEYMBYGA1UEAwwPVW5pdCBUZXN0IENl
cnQuMSQwIgYJKoZIhvcNAQkBFhVzb21ldGhpbmdAZXhhbXBsZS5jb20wggEiMA0G
CSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDNOMhd2VoDs4lImUP9wirFMF8jWTpy
6UHDwCzConkSI5hxO+uxPSbcL9sOdSYqTO4Ee+xZHbUJfh85zyX/y5LAD+NTN/bH
H2lMI7Nn4obRIZBcZIVZ4rB+lkoAsUfZ4tgxySJaCTB4Xsng60L9PYLXVsTme+T0
Yc//HUtuhh2MlblTEqauQDHzxBQJmIdgIvW2M8fLxZkpASCCycSnfk+6UIjxl0cj
UdvW5ZgfzkC0i/Y7rhFhnfXV317Lid7stohoLk1rphX3rROsVy+CnRsBZggMWDKO
LHWJJB2F4QaBjt66dgcZk2YTzEHnUzWVDAT4EG164s1iM3iVorIvFdyPAgMBAAGj
UDBOMB0GA1UdDgQWBBR+XRiQ7I/+W2sX0dQUEY7SL4dM3TAfBgNVHSMEGDAWgBR+
XRiQ7I/+W2sX0dQUEY7SL4dM3TAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBBQUA
A4IBAQCA0L2PYHWJib3xsxmB6oHLCtVgUdcsTW8GUgzBXLkxDziygnyy1BcnlH8I
53W+3le/HMODEiHsJ305D4e1uwSNKrEF/jVLPT4Dh9nKkYobQLAV0jRG7lPqB26g
gxAdT0P1E+FW1Uy/Z8dIw8L4lwRE8BQ9u5NmFIc8sfusGLOsp7eait99yeQ8LE2N
t7d0r9WU6xBhtByUdrQvVFAQZb4JdaTubz8LZ/3OicCFLcQ6nTDmxf/CqdeDMt7I
RO+r1owYY+LVpQWfE8872ALJ+YQne0i17XAsebNya/RInrjBKP/naFYG8bhkBr8K
4NpYdSm1IsLs7GtK6yXUk9M0iTOb
-----END CERTIFICATE-----""")
        self.name = k.name
        k.close()
        return self.name

    def __exit__(self, type, value, traceback):
        unlink(self.name)
        return False    # let all exceptions thru



# unittest that dummy!
import unittest
from os.path import exists

class GetDummyCertTest(unittest.TestCase):
    def test_it(self):
        with get_dummy_cert() as dcert:
            with open(dcert, 'rb') as x:
                s = x.read()

            self.assertEquals(s.startswith('-----BEGIN PRIVATE KEY-----'), True)
            self.assertEquals(s.endswith('-----END CERTIFICATE-----'), True)            

        self.assertEquals(exists(dcert), False)