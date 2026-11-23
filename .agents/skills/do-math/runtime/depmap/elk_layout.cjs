/* Runs one ELK layout. Adapted from the layout runner of the dependency-map generator of the
 * previous research (its build stage, `배치.cjs`).
 *
 * As there, the graph is assembled entirely in Python (draw.py) and this file only hands the input
 * JSON to elkjs and writes the result, so no topic or setting lives in JavaScript. What changed:
 * the elkjs package is named on the command line instead of being required from a fixed
 * node_modules folder, because the skill does not ship elkjs.
 *
 * usage: node elk_layout.cjs <elkjs folder> <input.json> <output.json>
 */
const fs = require('fs');
const path = require('path');
const [elkDir, inputPath, outputPath] = process.argv.slice(2);
if (!elkDir || !inputPath || !outputPath) {
  console.error('usage: node elk_layout.cjs <elkjs folder> <input.json> <output.json>');
  process.exit(2);
}
const ELK = require(path.resolve(elkDir));
const version = require(path.join(path.resolve(elkDir), 'package.json')).version;
const input = JSON.parse(fs.readFileSync(inputPath, 'utf8'));
async function main() {
  const started = Date.now();
  const raw = await new ELK().layout(input);
  raw.__elk_version = version;
  raw.__elapsed_ms = Date.now() - started;
  fs.writeFileSync(outputPath, JSON.stringify(raw));
  console.log(JSON.stringify({ width: raw.width, height: raw.height, elk: version, ms: raw.__elapsed_ms }));
}
main().catch(e => { console.error(e && e.stack || e); process.exit(1); });
