# generate_cert.py
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime

# Generate private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

# Generate certificate
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "ZA"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "KwaZulu-Natal"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, "Durban"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "DUT"),
    x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
])

cert = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    private_key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.utcnow()
).not_valid_after(
    datetime.datetime.utcnow() + datetime.timedelta(days=365)
).add_extension(
    x509.SubjectAlternativeName([
        x509.DNSName("localhost"),
        x509.DNSName("192.168.8.205"),
    ]),
    critical=False,
).sign(private_key, hashes.SHA256())

# Write certificate and key
with open("localhost.crt", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

with open("localhost.key", "wb") as f:
    f.write(private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ))

print("✅ Certificate generated successfully!")
print("📁 Files created: localhost.crt and localhost.key")