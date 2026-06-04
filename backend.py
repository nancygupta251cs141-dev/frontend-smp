from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

#stored data
categories = [
    {"id": 1, "name": "Electronics"},
    {"id": 2, "name": "Clothing"},
]

products = [
    {"id": 1, "name": "Laptop", "price": 75000.0, "category_id": 1, "stock": 10},
    {"id": 2, "name": "T-Shirt", "price": 499.0, "category_id": 2, "stock": 50},
    {"id": 3, "name": "Headphones", "price": 2999.0, "category_id": 1, "stock": 20},
]

orders = []
cart= []

category_id_available = 3
product_id_available = 4
order_id_available = 1

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
def find_product(id: int):
    product = next((p for p in products if p["id"] == id), None)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found")
    return product

def find_category(id: int):
    category = next((c for c in categories if c["id"] == id), None)
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
def display_products():
    return {"products": products}

@app.get("/products/{id}")
def display_product_by_id(id: int):
    return {"product": find_product(id)}

@app.post("/products")
def create_product(product: Product):
    global product_id_available
    find_category(product.category_id)
    new_product = {
        "id": product_id_available,
        "name": product.name,
        "price": product.price,
        "category_id": product.category_id,
        "stock": product.stock
    }
    products.append(new_product)
    product_id_available += 1
    return {"message": "Product created"}

@app.put("/products/{id}")
def update_product(id: int, product: ProductUpdate):
    product_to_update = find_product(id)
    if product.name is not None:
        product_to_update["name"] = product.name
    if product.price is not None:
        product_to_update["price"] = product.price
    if product.category_id is not None:
        find_category(product.category_id)
        product_to_update["category_id"] = product.category_id
    if product.stock is not None:
        product_to_update["stock"] = product.stock
    return {"message": "Product updated"}

@app.delete("/products/{id}")
def delete_product(id: int):
    product = find_product(id)
    products.remove(product)
    return {"message": "Product deleted"}


#categories
@app.get("/categories")
def display_categories():
    return {"categories": categories}

@app.post("/categories")
def create_category(category: Category):
    global category_id_available
    new_category = {
        "id": category_id_available,
        "name": category.name
    }
    categories.append(new_category)
    category_id_available += 1
    return {"message": "Category created"}


#cart
@app.get("/cart")
def display_cart():
    return {"cart": cart}

@app.post("/cart/add/{id}")
def add_to_cart(id: int, quantity: int):
    product = find_product(id)
    if quantity < 1:
        raise HTTPException(status_code=400, detail="Quantity must be at least 1")
    if product["stock"] < quantity:
        raise HTTPException(status_code=400, detail=f"Only {product['stock']} units in stock")
    exists = next((item for item in cart if item["product_id"] == id), None)
    if exists:
        exists["quantity"] += quantity
    else:
        cart.append({"product_id": product["id"], "quantity": quantity})
    return {"message": "Product added to cart"}

@app.delete("/cart/remove/{id}")
def remove_from_cart(id: int, quantity: int = 1):
    product = find_product(id)
    cart_item = next((item for item in cart if item["product_id"] == id), None)
    if not cart_item:
        raise HTTPException(status_code=404, detail=f"Product with id {id} not found in the cart")
    cart.remove(cart_item)
    product["stock"] += quantity
    return {"message": "Product removed from cart"}

#orders
@app.post("/orders")
def create_order():
    global order_id_available
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")
    order_items = []
    total = 0.0
    for item in cart:
        product = next((p for p in products if p["id"] == item["product_id"]), None)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        if product["stock"] < item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for '{product['name']}'")
        subtotal = product["price"] * item["quantity"]
        total += subtotal
        order_items.append({
            "id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": item["quantity"],
            "subtotal": subtotal
        })
        product["stock"] -= item["quantity"]
    new_order = {
        "id": order_id_available,
        "items": order_items,
        "total": total,
        "status": "confirmed",
    }
    orders.append(new_order)
    order_id_available += 1
    cart.clear()
    return {"message": "Order created"}

@app.get("/orders")
def display_orders():
    return {"orders": orders}

@app.get("/orders/{id}")
def display_order_by_id(id: int):
    order = next((o for o in orders if o["id"] == id), None)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order with id {id} not found")
    return {"order": order}