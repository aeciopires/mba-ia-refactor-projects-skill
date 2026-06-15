import os

SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "admin-key-change-me")

DISCOUNT_THRESHOLD_HIGH = 10_000
DISCOUNT_THRESHOLD_MID  = 5_000
DISCOUNT_THRESHOLD_LOW  = 1_000
DISCOUNT_RATE_HIGH = 0.10
DISCOUNT_RATE_MID  = 0.05
DISCOUNT_RATE_LOW  = 0.02

VALID_CATEGORIES = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
VALID_ORDER_STATUSES = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
