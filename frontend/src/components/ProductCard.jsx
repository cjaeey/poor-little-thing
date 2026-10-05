const ACTIVE_LABELS = {
  retinoid: "Retinoid",
  aha: "AHA",
  bha: "BHA",
  benzoyl_peroxide: "Benzoyl peroxide",
  vitamin_c: "Vitamin C",
  niacinamide: "Niacinamide",
};

export default function ProductCard({ product, number }) {
  return (
    <li className="product">
      {number && <span className="step-number">{number}</span>}
      <div>
        <p className="step-name">{product.step}</p>
        <h3>{product.name}</h3>
        <p className="brand">{product.brand} · ${product.price.toFixed(2)}</p>
        {product.reason && <p className="reason">{product.reason}</p>}
        <div className="actives">
          {product.actives.map((a) => (
            <span key={a} className="active-tag">{ACTIVE_LABELS[a] || a}</span>
          ))}
        </div>
      </div>
    </li>
  );
}