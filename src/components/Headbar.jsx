import { Link } from "react-router-dom";
import { useTheme } from "../context/ThemeContext";

const NAV_ITEMS = [
  { label: "Shop", to: "/" },
  { label: "Collections", to: "/collections" },
  { label: "About", to: "/about" },
  { label: "Contact", to: "/contact" },
];

function Headbar() {
  const { darkMode, toggleTheme } = useTheme();
  return (
    <header className="header">
      <div className="header-brand">
        <span className="brand-mark">MS</span>
        <div>
          <span className="brand-name">MiniShop</span>
          <span className="brand-tagline">Curated essentials, better shopping</span>
        </div>
      </div>

      <nav className="header-nav">
        {NAV_ITEMS.map((item) => (
          <Link key={item.label} to={item.to} className="nav-link">
            {item.label}
          </Link>
        ))}
      </nav>

      <div className="header-actions">
        <button onClick={toggleTheme} className="btn btn-sm btn-ghost">
          {darkMode ? "🌙 Dark" : "☀️ Light"}
        </button>
        <button type="button" className="btn btn-sm btn-ghost" disabled>
          Sign In
        </button>
      </div>
    </header>
  );
}

export default Headbar;
