#!/usr/bin/env node
/**
 * Build shim for shahababbasi.com.
 *
 * Delegates to the Python/Jinja2 generator under scripts/. The generator
 * reads templates/, data/master-data.json, and writes the static site to dist/.
 *
 * Run order:
 *   1) scripts/import_data.py - merges src-static/data/*.json into data/master-data.json
 *      (idempotent; only matters when the source data files have been edited)
 *   2) scripts/generate.py    - generates ~2,000+ HTML files across 22 languages
 *
 * Usage:
 *   node build/build.js          # fresh build of dist/
 *   npm run build                # same
 *
 * Cloudflare Pages config:
 *   - Build command: node build/build.js
 *   - Output directory: dist
 *   - (Optional) Skip build entirely: dist/ is committed, point Cloudflare at it
 */
import { execFileSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, '..');

function run(cmd, args, opts = {}) {
  console.log(`> ${cmd} ${args.join(' ')}`);
  execFileSync(cmd, args, { stdio: 'inherit', cwd: ROOT, ...opts });
}

function pickPython() {
  const candidates = ['python3', 'python', 'py'];
  for (const c of candidates) {
    try {
      execFileSync(c, ['--version'], { stdio: 'ignore' });
      return c;
    } catch (_) { /* not available */ }
  }
  throw new Error('Python 3 is required (python3, python, or py).');
}

function ensureJinja(py) {
  try {
    execFileSync(py, ['-c', 'import jinja2'], { stdio: 'ignore' });
  } catch (_) {
    console.log('Installing jinja2 ...');
    try {
      run(py, ['-m', 'pip', 'install', '--quiet', 'jinja2']);
    } catch (e) {
      console.error('Failed to install jinja2 with pip. If running in a restricted env, install it manually.');
      throw e;
    }
  }
}

const py = pickPython();
ensureJinja(py);

// 1) Refresh data/master-data.json from the seed + src-static/data overlays
if (fs.existsSync(path.join(ROOT, 'scripts', 'import_data.py')) && fs.existsSync(path.join(ROOT, 'src-static', 'data'))) {
  run(py, ['scripts/import_data.py']);
}

// 2) Render the static site
run(py, ['scripts/generate.py']);

console.log('Build complete. Output: dist/');
