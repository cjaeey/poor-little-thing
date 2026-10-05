import { useState } from "react";

const SKIN_TYPES = ["dry", "oily", "combination", "normal"];
const CONCERNS = ["acne", "aging", "dullness", "dryness"];
const BUDGETS = [25, 50, 100, 500];

export default function Quiz({ onSubmit, loading }) {
  const [skinType, setSkinType] = useState("");
  const [concerns, setConcerns] = useState([]);
  const [maxPrice, setMaxPrice] = useState(50);

  function toggleConcern(concern) {
    setConcerns((current) =>
      current.includes(concern) ? current.filter((c) => c !== concern) : [...current, concern]
    );
  }

  return (
    <section className="quiz">
      <fieldset>
        <legend>What's your skin type?</legend>
        {SKIN_TYPES.map((type) => (
          <button key={type} className={skinType === type ? "chip word on" : "chip word"} onClick={() => setSkinType(type)}>
            {type}
          </button>
        ))}
      </fieldset>

      <fieldset>
        <legend>What do you want to work on? Pick any.</legend>
        {CONCERNS.map((concern) => (
          <button key={concern} className={concerns.includes(concern) ? "chip word on" : "chip word"} onClick={() => toggleConcern(concern)}>
            {concern}
          </button>
        ))}
      </fieldset>

      <fieldset>
        <legend>Most you'd spend on one product</legend>
        {BUDGETS.map((budget) => (
          <button key={budget} className={maxPrice === budget ? "chip on" : "chip"} onClick={() => setMaxPrice(budget)}>
            {budget === 500 ? "No limit" : `$${budget}`}
          </button>
        ))}
      </fieldset>

      <button
        className="primary"
        disabled={!skinType || loading}
        onClick={() => onSubmit({ skin_type: skinType, concerns, max_price: maxPrice })}
      >
        {loading ? "Building your routine..." : "Build my routine"}
      </button>
    </section>
  );
}
