import { Routes, Route, Link } from "react-router-dom";
import Headbar from "./components/Headbar";
import Home from "./pages/Home";
import ItemPage from "./pages/ItemPage";
import About from "./pages/About";
import Collections from "./pages/Collections";
import Contact from "./pages/Contact";
import CartSidebar from "./components/CartSidebar";

function App() {
  return (
    <div className="app">
      <Headbar />

      <main className="app-content">
        <nav>
          <Link to="/">Home</Link>
          <Link to="/collections">Collections</Link>
          <Link to="/contact">Contact</Link>
          <Link to="/about">About</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/collections" element={<Collections />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/item/:id" element={<ItemPage />} />
          <Route path="/about" element={<About />} />
        </Routes>
        <CartSidebar />
      </main>
    </div>
  );
}

export default App;
