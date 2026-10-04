import React, { useState, useEffect } from 'react';
import { ChefHat, ShieldAlert, Sparkles, HeartPulse, RefreshCw, BookmarkCheck } from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function App() {
  const [profile, setProfile] = useState({
    name: "Mom",
    conditions: ["Diabetic Friendly (Low GI)", "Low Sodium"],
    disliked_ingredients: ["Quinoa", "Bland Salads"],
    preferred_oil: "Cold-Pressed Sesame / Mustard Oil",
    spice_level: "Authentic Regional"
  });

  const [rawText, setRawText] = useState("");
  const [customNotes, setCustomNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [recipe, setRecipe] = useState(null);

  const sampleRecipe = `My mom's Sunday Sambar notes:
2 cups toor dal, big gooseberry size tamarind soaked in hot water, lots of drumstick, pumpkin, and shallots.
Tadka: mustard, cumin, dried red chili, generous pinch of hing, fresh curry leaves.
She says: 'Fry onions till translucent, boil vegetables with tamarind water till raw smell leaves, don't skimp on dal water.'`;

  const handleTransform = async () => {
    if (!rawText.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/adapt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raw_text: rawText,
          custom_notes: customNotes,
          profile: profile
        })
      });
      const data = await res.json();
      setRecipe(data);
    } catch (err) {
      console.error("Failed to adapt recipe:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 font-sans">
      {/* Top Navigation */}
      <header className="border-b border-stone-200 bg-white/80 backdrop-blur sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="p-2 bg-amber-100 text-amber-800 rounded-xl">
              <ChefHat className="w-6 h-6" />
            </span>
            <div>
              <h1 className="font-bold text-lg leading-tight tracking-tight">RasoiVault</h1>
              <p className="text-xs text-stone-500">Open-Source Heritage Culinary Engine</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
              <HeartPulse className="w-3.5 h-3.5" /> Built for {profile.name}
            </span>
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono bg-stone-100 text-stone-600">
              Gemma-2-9B • On-Device Ready
            </span>
          </div>
        </div>
      </header>

      {/* Main Workspace */}
      <main className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Column: Input and Profile Controls */}
        <div className="lg:col-span-5 space-y-6">
          
          {/* Profile Card */}
          <div className="p-5 bg-white rounded-2xl border border-stone-200 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-500">Care Profile Active</h2>
              <span className="text-xs text-amber-700 font-medium bg-amber-50 px-2 py-0.5 rounded">Backboard Synced</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {profile.conditions.map((c, i) => (
                <span key={i} className="px-2.5 py-1 text-xs rounded-lg bg-rose-50 text-rose-700 border border-rose-100 font-medium">
                  {c}
                </span>
              ))}
              <span className="px-2.5 py-1 text-xs rounded-lg bg-stone-100 text-stone-700 font-medium">
                {profile.spice_level}
              </span>
            </div>
            <p className="text-xs text-stone-500 italic">
              Strictly filters out generic replacements (e.g., won't suggest {profile.disliked_ingredients.join(', ')}).
            </p>
          </div>

          {/* Recipe Input */}
          <div className="p-5 bg-white rounded-2xl border border-stone-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-sm font-semibold text-stone-800">1. Raw Recipe Notes or Oral Memory</label>
              <button 
                onClick={() => setRawText(sampleRecipe)}
                className="text-xs text-amber-700 hover:text-amber-800 font-medium hover:underline"
              >
                Load Mom's Sambar Sample
              </button>
            </div>
            
            <textarea
              rows={8}
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste vague family notes, voice memo transcripts, or a list of ingredients..."
              className="w-full text-sm p-3.5 rounded-xl border border-stone-200 focus:ring-2 focus:ring-amber-500 focus:outline-none bg-stone-50/50"
            />

            <div>
              <label className="text-xs font-medium text-stone-600 block mb-1">Additional adjustments or cravings for today:</label>
              <input
                type="text"
                value={customNotes}
                onChange={(e) => setCustomNotes(e.target.value)}
                placeholder="e.g., Keep tamarind sourness high, but avoid store-bought paste"
                className="w-full text-xs p-2.5 rounded-lg border border-stone-200 focus:ring-2 focus:ring-amber-500 focus:outline-none"
              />
            </div>

            <button
              onClick={handleTransform}
              disabled={loading || !rawText.trim()}
              className="w-full py-3 px-4 rounded-xl font-medium text-sm bg-stone-900 text-white hover:bg-black transition-colors flex items-center justify-center gap-2 disabled:opacity-50 shadow-sm"
            >
              {loading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Adapting with Open Weights...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4 text-amber-300" /> Transform with Heritage Safeguards
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Adapted Output */}
        <div className="lg:col-span-7">
          {recipe ? (
            <div className="p-6 bg-white rounded-2xl border border-stone-200 shadow-sm space-y-6 animate-fadeIn">
              
              <div className="border-b border-stone-100 pb-4">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-600">Clinically & Culturally Validated</span>
                <h2 className="text-2xl font-bold text-stone-900 mt-1">{recipe.title}</h2>
                <p className="text-sm text-stone-600 mt-1">{recipe.summary}</p>
              </div>

              {/* Substitution Delta Box */}
              <div className="bg-amber-50/70 border border-amber-200/80 rounded-xl p-4 space-y-2">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-amber-900 flex items-center gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-amber-600" /> Thoughtful Substitutions
                </h3>
                <div className="space-y-2 pt-1">
                  {recipe.substitutions.map((sub, idx) => (
                    <div key={idx} className="text-xs bg-white/80 p-2.5 rounded-lg border border-amber-100">
                      <div className="flex items-center gap-2">
                        <span className="line-through text-stone-400 font-medium">{sub.original}</span>
                        <span className="text-stone-400">→</span>
                        <span className="font-semibold text-emerald-700">{sub.substitute}</span>
                      </div>
                      <p className="text-stone-600 mt-1 italic">{sub.reason}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Ingredients & Method */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-stone-400 mb-2">Ingredients</h3>
                  <ul className="space-y-1.5 text-xs text-stone-700">
                    {recipe.ingredients.map((ing, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-amber-600 font-bold">•</span>
                        <span>{ing}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-stone-400 mb-2">Heritage Preservation</h3>
                  <p className="text-xs text-stone-600 leading-relaxed bg-stone-50 p-3 rounded-lg border border-stone-100">
                    {recipe.culinary_preservation_notes}
                  </p>
                </div>
              </div>

              {/* Steps */}
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-stone-400 mb-3">Preparation Steps</h3>
                <ol className="space-y-2.5 text-xs text-stone-700">
                  {recipe.instructions.map((step, i) => (
                    <li key={i} className="flex gap-3">
                      <span className="flex-shrink-0 w-5 h-5 rounded-full bg-stone-100 font-bold text-stone-600 flex items-center justify-center text-[11px]">
                        {i + 1}
                      </span>
                      <span className="pt-0.5 leading-relaxed">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>

              {/* Nutritional verdict */}
              <div className="p-3.5 bg-emerald-50 rounded-xl border border-emerald-100 text-xs text-emerald-800 flex items-center justify-between">
                <div>
                  <span className="font-bold">Health Impact:</span> {recipe.health_impact}
                </div>
                <button 
                  onClick={() => alert("Recipe saved to sovereign family book!")} 
                  className="px-3 py-1.5 bg-emerald-600 text-white rounded-lg font-medium hover:bg-emerald-700 transition"
                >
                  Save Recipe
                </button>
              </div>

            </div>
          ) : (
            <div className="h-full min-h-[350px] border-2 border-dashed border-stone-200 rounded-2xl flex flex-col items-center justify-center p-8 text-center bg-white/50">
              <ChefHat className="w-12 h-12 text-stone-300 mb-3" />
              <h3 className="font-semibold text-stone-700">No Recipe Adapted Yet</h3>
              <p className="text-xs text-stone-400 max-w-sm mt-1">
                Enter oral shorthand notes or memories on the left to generate an authentic, clinically calibrated recipe.
              </p>
            </div>
          )}
        </div>

      </main>
    </div>
  );
}