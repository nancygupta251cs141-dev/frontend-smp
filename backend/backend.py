from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

#database
DATABASE_URL = "postgresql://neondb_owner:npg_zT8omL4Vqrce@ep-super-cloud-aq2ape43-pooler.c-8.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300
)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class CategoryTable(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class ProductTable(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    category_id = Column(Integer)
    stock = Column(Integer)

class CartTable(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer)
    quantity = Column(Integer)

class OrderTable(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    total = Column(Float)
    status = Column(String)

class OrderItemTable(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer)
    product_id = Column(Integer)
    name = Column(String)
    price = Column(Float)
    quantity = Column(Integer)
    subtotal = Column(Float)

Base.metadata.create_all(engine)

#supplying connection to endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

#pydantic models
class Product(BaseModel):
    name: str
    price: float
    category_id: int
    stock: int = 0

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    category_id: Optional[int] = None
    stock: Optional[int] = None

class Category(BaseModel):
    name: str

#repeated functions
def find_product(id: int, db: Session):
    product = db.query(ProductTable).filter(ProductTable.id == id).first()
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    return product

def find_category(id: int, db: Session):
    category = db.query(CategoryTable).filter(CategoryTable.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail=f"Category with id {id} not found")
    return category

#main (root)
@app.get("/")
def read_root():
    return {"message": "Welcome to the E-commerce API"}

#endpoints

#products
@app.get("/products")
def display_products(db: Session = Depends(get_db)):
    products = db.query(ProductTable).all()
    return {"products": products}

@app.get("/products/{id}")
def display_product_by_id(id: int, db: Session = Depends(get_db)):
    return {"product": find_product(id, db)}

@app.post("/products")
def create_product(product: Product, db: Session = Depends(get_db)):
    find_category(product.category_id, db)
    new_product = ProductTable(
        name=product.name,
        price=product.price,
        category_id=product.category_id,
        stock=product.stock
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return {"message": "Product created"}

@app.put("/products/{id}")
def update_product(id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    product_to_update = find_product(id, db)
    if product.name is not None and product.name != "":
        product_to_update.name = product.name
    if product.price is not None:
        product_to_update.price = product.price
    if product.category_id is not None:
        find_category(product.category_id, db)
        product_to_update.category_id = product.category_id
    if product.stock is not None:
        product_to_update.stock = product.stock
    db.commit()
    return {"message": "Product updated"}

@app.delete("/products/{id}")
def delete_product(id: int, db: Session = Depends(get_db)):
    product = find_product(id, db)
    db.delete(product)
    db.commit()
    return {"message": "Product deleted"}


#categories
@app.get("/categories")
def display_categories(db: Session = Depends(get_db)):
    categories = db.query(CategoryTable).all()
    return {"categories": categories}

@app.post("/categories")
def create_category(category: Category, db: Session = Depends(get_db)):
    new_category = CategoryTable(name=category.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return {"message": "Category created"}

#cart
@app.get("/cart")
def display_cart(db: Session = Depends(get_db)):
    cart = db.query(CartTable).all()
    return {"cart": cart}

@app.post("/cart/add/{id}")
def add_to_cart(id: int, quantity: int, db: Session = Depends(get_db)):
    product = find_product(id, db)
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail=f"Only {product.stock} units in stock")
    exists = db.query(CartTable).filter(CartTable.product_id == id).first()
    if exists:
        exists.quantity += quantity
        db.commit()
    else:
        new_cart_item = CartTable(product_id=id, quantity=quantity)
        db.add(new_cart_item)
        db.commit()
    return {"message": "Product added to cart"}

@app.delete("/cart/remove/{id}")
def remove_from_cart(id: int, db: Session = Depends(get_db)):
    find_product(id, db)
    cart_item = db.query(CartTable).filter(CartTable.product_id == id).first()
    if not cart_item:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found in cart")
    db.delete(cart_item)
    db.commit()
    return {"message": "Product removed from cart"}

#orders
@app.post("/orders")
def create_order(db: Session = Depends(get_db)):
    cart = db.query(CartTable).all()
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    total = 0.0
    new_order = OrderTable(total=0.0, status="confirmed")
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    for item in cart:
        product = find_product(item.product_id, db)
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product.name}'")
        subtotal = product.price * item.quantity
        total += subtotal
        order_item = OrderItemTable(
            order_id=new_order.id,
            product_id=product.id,
            name=product.name,
            price=product.price,
            quantity=item.quantity,
            subtotal=subtotal
        )
        db.add(order_item)
        product.stock -= item.quantity
    new_order.total = total
    db.commit()
    for item in cart:
        db.delete(item)
    db.commit()
    return {"message": "Order created"}

@app.get("/orders")
def display_orders(db: Session = Depends(get_db)):
    orders = db.query(OrderTable).all()
    return {"orders": orders}

@app.get("/orders/{id}")
def display_order_by_id(id: int, db: Session = Depends(get_db)):
    order = db.query(OrderTable).filter(OrderTable.id == id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
    order_items = db.query(OrderItemTable).filter(OrderItemTable.order_id == id).all()
    return {"order": order, "items": order_items}