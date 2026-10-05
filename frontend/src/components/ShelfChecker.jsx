import { useState } from "react";
import ProductCard from "./ProductCard.jsx";
import { searchProducts, checkConflicts } from "../api.js";

export default function ShelfChecker() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [shelf, setShelf] = useState([]);
  const [conflicts, setConflicts] = useState(null);
  const [error, setError] = useState("");

  async function handleSearch(event) {
    event.preventDefault();
    if (!query.trim()) return;
    try {
      setResults(await searchProducts(query));
      setError("");
    } catch {
      setError("Search failed. Check that the server is running.");
    }
  }

  function addToShelf(product) {
    if (!shelf.some((p) => p.id === product.id)) {
      setShelf([...shelf, product]);
      setConflicts(null);
    }
  }

  async function handleCheck() {
    try {
      const data = await checkConflicts(shelf.map((p) => p.id));
      setConflicts(data.conflicts);
    } catch {
      setError("Couldn't check conflicts. Try again.");
    }
  }

  return (
    <section className="shelf">
      <p>Add the products you use in one routine, then check if any of them clash.</p>
      <form onSubmit={handleSearch} className="search">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search by product or brand"
          aria-label="Search products"
        />
        <button className="primary" type="submit">Search</button>
      </form>
      {error && <p className="error">{error}</p>}

      <ul className="results">
        {results.map((p) => (
          <li key={p.id}>
            <span>{p.brand}: {p.name}</span>
            <button className="secondary" onClick={() => addToShelf(p)}>Add</button>
          </li>
        ))}
      </ul>

      {shelf.length > 0 && (
        <>
          <h2>Your shelf</h2>
          <ol>{shelf.map((p) => <ProductCard key={p.id} product={p} />)}</ol>
          <button className="primary check-button" disabled={shelf.length < 2} onClick={handleCheck}>
            Check for clashes
          </button>
        </>
      )}

      {conflicts && conflicts.length === 0 && <p className="ok">No clashes found. You're good.</p>}
      {conflicts && conflicts.map((c, i) => (
        <div key={i} className="conflict">
          <strong>{c.products.join(" + ")}</strong>
          <p>{c.message}</p>
        </div>
      ))}
    </section>
  );
}