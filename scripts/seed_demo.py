import os
import sys
from datetime import datetime, date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import text
from config.database import SessionLocal
from models.category import CategoryModel
from models.product import ProductModel
from models.client import ClientModel
from models.address import AddressModel
from models.bill import BillModel
from models.order import OrderModel
from models.order_detail import OrderDetailModel
from models.review import ReviewModel
from models.user import UserModel
from models.payment_method import PaymentMethodModel
from models.enums import DeliveryMethod, Status, PaymentType
from utils.security import hash_password


def reset_db(db):
    db.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url VARCHAR"))
    db.execute(
        text(
            "TRUNCATE TABLE order_details, orders, bills, reviews, addresses, billing_methods, products, categories, clients, users RESTART IDENTITY CASCADE;"
        )
    )
    db.commit()


def seed():
    db = SessionLocal()
    try:
        reset_db(db)

        admin = UserModel(
            email="admin@demo.com",
            name="Admin",
            lastname="Rebrum",
            password_hash=hash_password("admin123"),
            is_active=True,
            is_admin=True,
        )
        user1 = UserModel(
            email="lola@demo.com",
            name="Lola",
            lastname="Stone",
            country="Argentina",
            province="Buenos Aires",
            locality="Palermo",
            street="Honduras",
            postal_code="1414",
            extra_info="Depto 4B",
            password_hash=hash_password("demo1234"),
            is_active=True,
            is_admin=False,
        )
        user2 = UserModel(
            email="max@demo.com",
            name="Max",
            lastname="Crow",
            country="Argentina",
            province="Cordoba",
            locality="Centro",
            street="Belgrano",
            postal_code="5000",
            extra_info="Casa",
            password_hash=hash_password("demo1234"),
            is_active=True,
            is_admin=False,
        )
        db.add_all([admin, user1, user2])
        db.commit()
        db.refresh(admin)
        db.refresh(user1)
        db.refresh(user2)

        categories = [
            CategoryModel(name="Remeras"),
            CategoryModel(name="Buzos"),
            CategoryModel(name="Camperas"),
            CategoryModel(name="Pantalones"),
            CategoryModel(name="Accesorios"),
        ]
        db.add_all(categories)
        db.commit()
        for c in categories:
            db.refresh(c)

        products = [
            ProductModel(
                name="Remera Grunge Acid Wash",
                price=18999,
                stock=24,
                category_id=categories[0].id_key,
                image_url="https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Remera Oversize Nirvana",
                price=20999,
                stock=18,
                category_id=categories[0].id_key,
                image_url="https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Buzo Hoodie Destroyed",
                price=39999,
                stock=12,
                category_id=categories[1].id_key,
                image_url="https://images.unsplash.com/photo-1523381294911-8d3cead13475?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Buzo Grunge Patchwork",
                price=42999,
                stock=9,
                category_id=categories[1].id_key,
                image_url="https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Campera Denim Black",
                price=54999,
                stock=7,
                category_id=categories[2].id_key,
                image_url="https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Campera Militar Grunge",
                price=58999,
                stock=5,
                category_id=categories[2].id_key,
                image_url="https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Pantalon Cargo Black",
                price=45999,
                stock=10,
                category_id=categories[3].id_key,
                image_url="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Jean Roto Wide Leg",
                price=47999,
                stock=8,
                category_id=categories[3].id_key,
                image_url="https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Gorro Beanie Heavy",
                price=8999,
                stock=40,
                category_id=categories[4].id_key,
                image_url="https://images.unsplash.com/photo-1503341455253-b2e723bb3dbb?auto=format&fit=crop&w=1200&q=80",
            ),
            ProductModel(
                name="Cadena Metalica Grunge",
                price=12999,
                stock=30,
                category_id=categories[4].id_key,
                image_url="https://images.unsplash.com/photo-1512436991641-6745cdb1723f?auto=format&fit=crop&w=1200&q=80",
            ),
        ]
        db.add_all(products)
        db.commit()
        for p in products:
            db.refresh(p)

        client1 = ClientModel(name="Lola", lastname="Stone", email="lola@demo.com", telephone="+5491155551111")
        client2 = ClientModel(name="Max", lastname="Crow", email="max@demo.com", telephone="+5491155552222")
        db.add_all([client1, client2])
        db.commit()
        db.refresh(client1)
        db.refresh(client2)

        addresses = [
            AddressModel(
                street="Honduras",
                number="5100",
                city="Palermo",
                country="Argentina",
                province="Buenos Aires",
                postal_code="1414",
                client_id=client1.id_key,
            ),
            AddressModel(
                street="Belgrano",
                number="122",
                city="Centro",
                country="Argentina",
                province="Cordoba",
                postal_code="5000",
                client_id=client2.id_key,
            ),
        ]
        db.add_all(addresses)
        db.commit()

        bills = [
            BillModel(
                bill_number="RB-0001",
                discount=0,
                date=date.today(),
                total=87998,
                payment_type=PaymentType.CARD,
                client_id=client1.id_key,
            ),
            BillModel(
                bill_number="RB-0002",
                discount=1500,
                date=date.today(),
                total=52999,
                payment_type=PaymentType.DEBIT,
                client_id=client2.id_key,
            ),
        ]
        db.add_all(bills)
        db.commit()
        db.refresh(bills[0])
        db.refresh(bills[1])

        orders = [
            OrderModel(
                date=datetime.utcnow(),
                total=87998,
                delivery_method=DeliveryMethod.HOME_DELIVERY,
                status=Status.IN_PROGRESS,
                client_id=client1.id_key,
                bill_id=bills[0].id_key,
            ),
            OrderModel(
                date=datetime.utcnow(),
                total=52999,
                delivery_method=DeliveryMethod.DRIVE_THRU,
                status=Status.PENDING,
                client_id=client2.id_key,
                bill_id=bills[1].id_key,
            ),
        ]
        db.add_all(orders)
        db.commit()
        db.refresh(orders[0])
        db.refresh(orders[1])

        order_details = [
            OrderDetailModel(order_id=orders[0].id_key, product_id=products[0].id_key, quantity=2, price=18999),
            OrderDetailModel(order_id=orders[0].id_key, product_id=products[2].id_key, quantity=1, price=39999),
            OrderDetailModel(order_id=orders[1].id_key, product_id=products[4].id_key, quantity=1, price=54999),
        ]
        db.add_all(order_details)
        db.commit()

        payment_methods = [
            PaymentMethodModel(
                user_id=user1.id_key,
                brand="Visa",
                last4="4242",
                exp_month=11,
                exp_year=2028,
                is_default=True,
            ),
            PaymentMethodModel(
                user_id=user2.id_key,
                brand="Mastercard",
                last4="4444",
                exp_month=8,
                exp_year=2027,
                is_default=True,
            ),
        ]
        db.add_all(payment_methods)
        db.commit()

        reviews = [
            ReviewModel(
                rating=4.5,
                comment="Calidad buenisima, tela pesada y buen calce.",
                product_id=products[0].id_key,
                user_id=user1.id_key,
            ),
            ReviewModel(
                rating=5.0,
                comment="Se ve increible, super grunge y comoda.",
                product_id=products[2].id_key,
                user_id=user2.id_key,
            ),
        ]
        db.add_all(reviews)
        db.commit()

        print("Seed completado.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()

