import { useCart } from "../context/CartContext";
function Itemcard({ item }) {
  const { addToCart } = useCart();
  return (
    <div className="item-card">

      <div className="item-card-image">
        <img src={item.image} alt={item.name} />
      </div>

      <div className="item-card-body">
        <h3 className="item-name">{item.name}</h3>
        <p className="item-desc">{item.description}</p>
      </div>

      <div className="item-card-footer">
        <span className="item-price">₹{item.price.toFixed(2)}</span>
        <span className="item-meta">{item.category}</span>
        <button
          className="btn btn-primary btn-sm"
          onClick={() => addToCart(item)}
        >
          Add to Cart
        </button>
      </div>

    </div>
  );
}

export default Itemcard;