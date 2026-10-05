import ProductCard from "./ProductCard.jsx";

function RoutineList({ title, products }) {
  if (products.length === 0) {
    return <p className="empty">No {title} products fit your budget. Try raising it.</p>;
  }
  const total = products.reduce((sum, p) => sum + p.price, 0);
  return (
    <div className="routine-column">
      <h2>{title}</h2>
      <ol>
        {products.map((p, i) => <ProductCard key={p.id} product={p} number={i + 1} />)}
      </ol>
      <p className="total">Total: ${total.toFixed(2)}</p>
    </div>
  );
}

export default function Routine({ routine, onRestart }) {
  return (
    <section>
      <div className="routine">
        <RoutineList title="Morning" products={routine.am} />
        <RoutineList title="Night" products={routine.pm} />
      </div>
      <p className="note">
        Products are checked so nothing in the same routine clashes. Not medical advice; patch test new products.
      </p>
      <button className="secondary" onClick={onRestart}>Retake the quiz</button>
    </section>
  );
}