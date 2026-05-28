import { Link } from "react-router-dom";
import items from "../data/items";
import Itemcard from "../components/Item_card";
import { useState} from "react";

function Home() {
  const [search, setsearch] = useState("");
  const [category, setCategory] = useState("All");
  const [price, setPrice] = useState("All");
  const searchedItems = items.filter((item) => {
    const matchesSearch = item.name
      .toLowerCase()
      .includes(search.toLowerCase());

  const matchesCategory = category === "All" || item.category === category;

  const matchesPrice =
    price === "All" ||
    (price === "under20" && item.price < 20) ||
    (price === "20to40" && item.price >= 20 && item.price <= 40) ||
    (price === "over40" && item.price > 40);

  return matchesSearch && matchesCategory && matchesPrice;
});
  const categories = ["All", ...new Set(items.map((item) => item.category))];
  const priceRanges = [
  { label: "All prices", value: "All" },
  { label: "Below ₹20", value: "under20" },
  { label: "₹20 - ₹40", value: "20to40" },
  { label: "Over ₹40", value: "over40" },
];
  return (
    <main className="page home-page">
      <section className="home-hero">
        <div>
          <p className="hero-eyebrow">Curated marketplace</p>
          <h1 className="hero-title">
            Discover premium products that feel made for you.
          </h1>
          <p className="hero-copy">
            Shop everyday favorites across home, tech, fitness, and lifestyle.
            Every item is selected for quality, value, and real usefulness.
          </p>
          <div className="hero-actions">
            <Link to="/contact" className="btn btn-ghost">
              Contact Us
            </Link>
          </div>
        </div>
      </section>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setsearch(e.target.value)}
          className="search-input"
        />
      </div>
      <div className="filters">
  

  <div className="filter-group">
    <label className="filter-label">Category</label>
    <select
      className="filter-select"
      value={category}
      onChange={(e) => setCategory(e.target.value)}
    >
      {categories.map((cat) => (
        <option key={cat} value={cat}>
          {cat === "All" ? "All categories" : cat}
        </option>
      ))}
    </select>
  </div>
  <div className="filter-group">
    <label className="filter-label">Price</label>
    <select
      className="filter-select"
      value={price}
      onChange={(e) => setPrice(e.target.value)}
    >
      {priceRanges.map((range) => (
        <option key={range.value} value={range.value}>
          {range.label}
        </option>
      ))}
    </select>
  </div>
</div>
      

      <section className="item-grid">
        {searchedItems.length > 0 ? (
          searchedItems.map((item) => (
            <Itemcard key={item.id} item={item} />
          ))
        ) : (
          <p className="empty-state">No items found for "{search}"</p>
        )}
      </section>
    </main>
  );
}

export default Home;
