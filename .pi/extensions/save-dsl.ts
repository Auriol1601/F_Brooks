// Enregistre automatiquement le DSL Structurizr produit par F. Brooks.
//
// Après chaque réponse de l'assistant, le dernier bloc ```structurizr``` qui
// contient un workspace est écrit dans <dossier>/workspace.dsl (nom imposé
// par Structurizr). Une réponse sans DSL (question, analyse) ne touche à rien.
//
// <dossier> = FBROOKS_PROJECT_DIR (variable d'environnement, sinon fichier
// .env du dépôt), sinon structurizr/ du dépôt — le même dossier que celui
// affiché par docker compose.
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { isAbsolute, join, resolve } from "node:path";

const DSL_BLOCK = /```(?:structurizr|dsl)[^\n]*\n([\s\S]*?)```/g;

export function extractWorkspace(text: string): string | undefined {
  let found: string | undefined;
  for (const match of text.matchAll(DSL_BLOCK)) {
    const body = match[1].trim();
    if (/^workspace\b/.test(body)) found = body;
  }
  return found;
}

function readEnvFile(cwd: string): string | undefined {
  const file = join(cwd, ".env");
  if (!existsSync(file)) return undefined;
  for (const line of readFileSync(file, "utf8").split(/\r?\n/)) {
    const m = line.match(/^\s*FBROOKS_PROJECT_DIR\s*=\s*(.*?)\s*$/);
    if (m && m[1]) return m[1].replace(/^["']|["']$/g, "");
  }
  return undefined;
}

export function targetDir(cwd: string): string {
  const dir = process.env.FBROOKS_PROJECT_DIR || readEnvFile(cwd) || "structurizr";
  return isAbsolute(dir) ? dir : resolve(cwd, dir);
}

function messageText(message: any): string {
  const content = message?.content;
  if (typeof content === "string") return content;
  if (!Array.isArray(content)) return "";
  return content
    .filter((part: any) => part?.type === "text" && typeof part.text === "string")
    .map((part: any) => part.text)
    .join("\n");
}

export default function (pi: ExtensionAPI) {
  pi.on("message_end", async (event, ctx) => {
    if ((event.message as any)?.role !== "assistant") return;
    const dsl = extractWorkspace(messageText(event.message));
    if (!dsl) return;

    const dir = targetDir(ctx.cwd);
    const file = join(dir, "workspace.dsl");
    try {
      mkdirSync(dir, { recursive: true });
      writeFileSync(file, dsl + "\n", "utf8");
      ctx.ui.notify(`Diagramme enregistré : ${file}`, "info");
    } catch (error) {
      ctx.ui.notify(`Échec de l'enregistrement du diagramme (${file}) : ${error}`, "error");
    }
  });
}
