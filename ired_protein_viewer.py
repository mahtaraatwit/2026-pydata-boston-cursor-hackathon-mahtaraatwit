"""3Dmol-backed protein structure viewer for IRED hackathon notebooks."""

from __future__ import annotations

import anywidget
import traitlets


class ProteinStructureViewer(anywidget.AnyWidget):
    pdb_text = traitlets.Unicode("").tag(sync=True)
    pdb_chain = traitlets.Unicode("A").tag(sync=True)
    effects_conversion_mean = traitlets.Unicode("{}").tag(sync=True)
    effects_conversion_max = traitlets.Unicode("{}").tag(sync=True)
    effects_chirality_mean = traitlets.Unicode("{}").tag(sync=True)
    effects_chirality_max = traitlets.Unicode("{}").tag(sync=True)
    color_mode = traitlets.Unicode("conversion").tag(sync=True)
    aggregation_mode = traitlets.Unicode("mean").tag(sync=True)

    _esm = r"""
    export default {
      async render({ model, el }) {
        el.replaceChildren();
        const host = document.createElement("div");
        host.style.width = "100%";
        host.style.height = "520px";
        el.appendChild(host);

        await new Promise((resolve, reject) => {
          if (globalThis.$3Dmol) {
            resolve();
            return;
          }
          const script = document.createElement("script");
          script.src = "https://cdn.jsdelivr.net/npm/3dmol@2.1.0/build/3Dmol-min.js";
          script.onload = () => resolve();
          script.onerror = () => reject(new Error("Failed to load 3Dmol.js"));
          document.head.appendChild(script);
        });

        const viewer = globalThis.$3Dmol.createViewer(host, { backgroundColor: "white" });
        const $3D = globalThis.$3Dmol;

        const proteinSel = { not: { resn: ["HOH", "WAT", "H2O", "DOD"] } };

        const clamp01 = (x) => Math.max(0, Math.min(1, x));
        const lerp = (a, b, t) => a + (b - a) * t;

        const interpolateRgbStops = (stops, tRaw) => {
          const t = clamp01(tRaw);
          let left = stops[0];
          let right = stops[stops.length - 1];
          for (let i = 1; i < stops.length; i++) {
            if (t <= stops[i][0]) {
              left = stops[i - 1];
              right = stops[i];
              break;
            }
          }
          const denom = right[0] - left[0] || 1;
          const localT = clamp01((t - left[0]) / denom);
          const r = Math.round(lerp(left[1][0], right[1][0], localT));
          const g = Math.round(lerp(left[1][1], right[1][1], localT));
          const b = Math.round(lerp(left[1][2], right[1][2], localT));
          return `rgb(${r}, ${g}, ${b})`;
        };

        const conversionStops = [
          [0.0, [49, 54, 149]],
          [0.35, [69, 117, 180]],
          [0.5, [247, 247, 247]],
          [0.7, [253, 174, 97]],
          [1.0, [165, 0, 38]],
        ];

        const chiralityStops = [
          [0.0, [94, 60, 153]],
          [0.35, [178, 171, 210]],
          [0.5, [247, 247, 247]],
          [0.7, [253, 184, 99]],
          [1.0, [230, 97, 1]],
        ];

        const tooltip = document.createElement("div");
        tooltip.style.position = "absolute";
        tooltip.style.pointerEvents = "none";
        tooltip.style.background = "rgba(20, 20, 20, 0.9)";
        tooltip.style.color = "#ffffff";
        tooltip.style.padding = "6px 8px";
        tooltip.style.borderRadius = "6px";
        tooltip.style.fontSize = "12px";
        tooltip.style.fontFamily = "ui-sans-serif, system-ui, -apple-system";
        tooltip.style.lineHeight = "1.35";
        tooltip.style.zIndex = "1000";
        tooltip.style.display = "none";
        el.style.position = "relative";
        el.appendChild(tooltip);

        const hideTooltip = () => {
          tooltip.style.display = "none";
        };

        const AA3_TO_AA1 = {
          ALA: "A", ARG: "R", ASN: "N", ASP: "D", CYS: "C",
          GLN: "Q", GLU: "E", GLY: "G", HIS: "H", ILE: "I",
          LEU: "L", LYS: "K", MET: "M", MSE: "M", PHE: "F",
          PRO: "P", SER: "S", THR: "T", TRP: "W", TYR: "Y", VAL: "V",
        };

        const effectMapForCurrentSelection = () => {
          const raw = selectedEffectMap();
          try {
            return JSON.parse(raw || "{}");
          } catch (_err) {
            return {};
          }
        };

        let atomClickedInCycle = false;

        const showTooltip = (atom, event) => {
          if (!atom) return;
          const mode = model.get("color_mode");
          const agg = model.get("aggregation_mode");
          const effects = effectMapForCurrentSelection();
          const key = String(atom.resi);
          const value = Number(effects[key]);
          const valueText = Number.isFinite(value) ? value.toFixed(4) : "NA";
          const resn = String(atom.resn || "").toUpperCase();
          const wtAA = AA3_TO_AA1[resn] || "?";

          tooltip.innerHTML =
            `<div><strong>Chain</strong>: ${atom.chain ?? "?"}</div>` +
            `<div><strong>Residue</strong>: ${atom.resi}</div>` +
            `<div><strong>WT AA</strong>: ${wtAA} (${resn || "NA"})</div>` +
            `<div><strong>Mode</strong>: ${mode}</div>` +
            `<div><strong>Summary</strong>: ${agg}</div>` +
            `<div><strong>Value</strong>: ${valueText}</div>`;

          const rect = host.getBoundingClientRect();
          const clientX = event?.clientX ?? event?.pageX ?? (rect.left + rect.width / 2);
          const clientY = event?.clientY ?? event?.pageY ?? (rect.top + rect.height / 2);
          const x = clientX - rect.left + 10;
          const y = clientY - rect.top + 10;

          tooltip.style.left = `${Math.max(8, Math.min(rect.width - 180, x))}px`;
          tooltip.style.top = `${Math.max(8, Math.min(rect.height - 110, y))}px`;
          tooltip.style.display = "block";
        };

        const getColorForValue = (mode, value, lo, hi) => {
          if (!Number.isFinite(value)) return "#d2d2d2";
          const span = hi - lo || 1;
          const t = clamp01((value - lo) / span);
          const stops = mode === "chirality" ? chiralityStops : conversionStops;
          return interpolateRgbStops(stops, t);
        };

        const applyRepresentation = () => {
          viewer.removeAllSurfaces();
          viewer.setStyle({}, {
            cartoon: { color: "#bfbfbf", opacity: 0.95 },
            stick: { hidden: true },
            sphere: { hidden: true },
            line: { hidden: true },
          });

          viewer.setStyle(
            { hetflag: true, not: { resn: ["HOH", "WAT", "H2O", "DOD"] } },
            {
              stick: { radius: 0.2, colorscheme: "Jmol" },
              sphere: { scale: 0.25, colorscheme: "Jmol" },
            },
          );
        };

        const selectedEffectMap = () => {
          const mode = model.get("color_mode");
          const agg = model.get("aggregation_mode");
          if (mode === "chirality") {
            return agg === "max"
              ? model.get("effects_chirality_max")
              : model.get("effects_chirality_mean");
          }
          return agg === "max"
            ? model.get("effects_conversion_max")
            : model.get("effects_conversion_mean");
        };

        const recolor = () => {
          const mode = model.get("color_mode");
          const raw = selectedEffectMap();

          let effects = {};
          try {
            effects = JSON.parse(raw || "{}");
          } catch (_err) {
            effects = {};
          }

          const numericVals = Object.values(effects)
            .map((x) => Number(x))
            .filter((x) => Number.isFinite(x));
          const lo = numericVals.length ? Math.min(...numericVals) : 0;
          const hi = numericVals.length ? Math.max(...numericVals) : 1;

          applyRepresentation();

          viewer.addSurface(
            $3D.SurfaceType.MS,
            {
              opacity: 0.92,
              colorfunc: (atom) => {
                const key = String(atom.resi);
                const value = Number(effects[key]);
                return getColorForValue(mode, value, lo, hi);
              },
            },
            proteinSel,
          );

          viewer.setStyle(
            proteinSel,
            {
              cartoon: {
                colorfunc: (atom) => {
                  const key = String(atom.resi);
                  const value = Number(effects[key]);
                  return getColorForValue(mode, value, lo, hi);
                },
                opacity: 0.95,
              },
            },
          );

          viewer.zoomTo();
          viewer.render();
        };

        const bindBackgroundClickToHide = () => {
          const canvas = host.querySelector("canvas");
          if (!canvas) return;
          if (canvas.dataset.tooltipHideBound === "1") return;

          const onCanvasClick = () => {
            setTimeout(() => {
              if (!atomClickedInCycle) {
                hideTooltip();
              }
              atomClickedInCycle = false;
            }, 0);
          };

          canvas.addEventListener("click", onCanvasClick);
          canvas.dataset.tooltipHideBound = "1";
        };

        const reloadStructure = () => {
          viewer.removeAllModels();
          viewer.addModel(model.get("pdb_text"), "pdb");
          viewer.setClickable({}, true, (atom, _viewer, event) => {
            atomClickedInCycle = true;
            showTooltip(atom, event);
          });
          bindBackgroundClickToHide();
          recolor();
        };

        reloadStructure();

        model.on("change:pdb_text", reloadStructure);
        model.on("change:color_mode", recolor);
        model.on("change:aggregation_mode", recolor);
        model.on("change:effects_conversion_mean", recolor);
        model.on("change:effects_conversion_max", recolor);
        model.on("change:effects_chirality_mean", recolor);
        model.on("change:effects_chirality_max", recolor);
        model.on("change:color_mode", hideTooltip);
        model.on("change:aggregation_mode", hideTooltip);
      },
    };
    """
