// Supabase Edge Function (Deno) — backend del Tutor AI e dello scanner esercizi.
// Deploy: supabase functions deploy ai-tutor
// Secret richiesto (mai esposto al client): supabase secrets set ANTHROPIC_API_KEY=sk-ant-...
//
// Modello: claude-opus-5 (1M di contesto, $5/$25 per milione di token di input/output).
// Per un tutor conversazionale ad alto volume, claude-sonnet-5 è un'alternativa più economica
// ($2/$10 per milione) — cambiala impostando il secret ANTHROPIC_MODEL se preferisci quella.
import Anthropic from "npm:@anthropic-ai/sdk@^0.32.0";

const MODEL = Deno.env.get("ANTHROPIC_MODEL") ?? "claude-opus-5";
const anthropic = new Anthropic({ apiKey: Deno.env.get("ANTHROPIC_API_KEY") });

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

type ChatRole = "user" | "assistant";
interface ChatBody {
  type?: "chat";
  mode: "spiegami" | "esercitati" | "aiutami" | "controlla" | "interrogami";
  noSolution: boolean;
  subjectName?: string | null;
  topicName?: string | null;
  explanationStyle: "semplice" | "universitario" | "tecnico" | "dettagliato";
  level: "principiante" | "intermedio" | "avanzato";
  messages: { role: ChatRole; content: string }[];
}

interface RecognizeBody {
  type: "recognize";
  imageBase64: string;
}

const MODE_INSTRUCTIONS: Record<ChatBody["mode"], string> = {
  spiegami: "Lo studente vuole una spiegazione chiara della teoria richiesta.",
  esercitati: "Proponi allo studente un esercizio pertinente e guidalo nella pratica.",
  aiutami: "Lo studente è bloccato su un esercizio: aiutalo a sbloccarsi senza risolverlo al posto suo, a meno che 'noSolution' sia false.",
  controlla: "Lo studente ti mostrerà un procedimento: individua l'errore e spiega perché è sbagliato.",
  interrogami: "Fai domande allo studente sulla teoria per verificare quanto ha capito, una alla volta.",
};

function buildSystemPrompt(body: ChatBody): string {
  const context = [body.subjectName, body.topicName].filter(Boolean).join(" · ");
  const noSolutionRule = body.noSolution
    ? "REGOLA IMPORTANTE: non fornire mai la soluzione completa. Dai solo piccoli suggerimenti " +
      "progressivi, uno alla volta, finché lo studente non arriva da solo alla risposta. " +
      "Se lo studente chiede esplicitamente la soluzione, ricorda gentilmente che può disattivare " +
      "questa modalità dall'interruttore 'Non darmi la soluzione'."
    : "Lo studente ha disattivato la modalità 'non darmi la soluzione': puoi mostrare procedimenti completi quando richiesto.";

  return [
    "Sei ENGI AI, il tutor AI di uno studente di ingegneria italiano.",
    context ? `Contesto attuale: ${context}.` : "",
    `Modalità: ${body.mode}. ${MODE_INSTRUCTIONS[body.mode]}`,
    `Stile di spiegazione richiesto: ${body.explanationStyle}.`,
    `Livello dello studente: ${body.level}.`,
    noSolutionRule,
    "Rispondi sempre in italiano, con formule in notazione testuale semplice (es. x^2, sqrt(x), integrale di f(x)dx).",
  ]
    .filter(Boolean)
    .join("\n");
}

async function handleChat(body: ChatBody): Promise<Response> {
  const response = await anthropic.messages.create({
    model: MODEL,
    max_tokens: 2048,
    system: buildSystemPrompt(body),
    messages: body.messages.map((m) => ({ role: m.role, content: m.content })),
  });

  const textBlock = response.content.find((b): b is Anthropic.TextBlock => b.type === "text");
  return new Response(JSON.stringify({ reply: textBlock?.text ?? "" }), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

async function handleRecognize(body: RecognizeBody): Promise<Response> {
  const response = await anthropic.messages.create({
    model: MODEL,
    max_tokens: 300,
    messages: [
      {
        role: "user",
        content: [
          { type: "image", source: { type: "base64", media_type: "image/jpeg", data: body.imageBase64 } },
          {
            type: "text",
            text:
              "Questa è la foto di un esercizio universitario (matematica, fisica o ingegneria). " +
              "Rispondi in italiano SOLO con una breve etichetta che identifica il tipo di problema " +
              "(es. 'Equazione differenziale del primo ordine', 'Integrale definito per sostituzione'). " +
              "Nessuna spiegazione, nessuna soluzione.",
          },
        ],
      },
    ],
  });

  const textBlock = response.content.find((b): b is Anthropic.TextBlock => b.type === "text");
  return new Response(JSON.stringify({ label: textBlock?.text?.trim() ?? "Esercizio riconosciuto" }), {
    headers: { ...corsHeaders, "Content-Type": "application/json" },
  });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders });
  }

  try {
    const body = (await req.json()) as ChatBody | RecognizeBody;

    if (body.type === "recognize") {
      return await handleRecognize(body);
    }
    return await handleChat(body as ChatBody);
  } catch (err) {
    console.error("[ai-tutor] errore:", err);
    return new Response(JSON.stringify({ error: "internal_error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
