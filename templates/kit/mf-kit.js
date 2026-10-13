/* MotionFly kit: optional helpers for scene compositions (HyperFrames + GSAP).
   Loaded once in index.html by tools/assemble.py, so every scene can use window.MF.
   Nothing here is required: a scene may ignore the kit and draw its own way.
   All helpers are deterministic (no Math.random, no Date): the same time always gives the same frame.

   const K = MF.scene("s3", { bpm: 92, doc: document });   // pass the scene's own document; tl, A(key), DUR, beats(), $()
   K.draw("outline", K.A("hook"), 0.6, { pen: "#s3-crayon" });
   K.write("title", 0.4, 0.35);
   K.pageIn(); K.drift("#s3-cam"); K.pageOut(); K.boil(); K.done();
*/
(() => {
  const f1 = (n) => (+n).toFixed(1);

  /* ---------- deterministic hand-drawn geometry ---------- */
  const geo = {
    // rectangle with rounded corners and a gentle hand wobble (seed changes the wobble)
    wobRect(x, y, w, h, r = 18, sd = 1, amp = 2.6) {
      const j = (k) => f1(amp * Math.sin(sd * 3.1 + k * 2.7));
      const X = x + w, Y = y + h;
      return `M${x + r} ${+y + +j(0)} Q${x + w / 2} ${y - 3 + +j(1)} ${X - r} ${+y + +j(2)} Q${X} ${y} ${X + +j(3)} ${y + r}`
        + ` Q${X + 3 + +j(4)} ${y + h / 2} ${X + +j(5)} ${Y - r} Q${X} ${Y} ${X - r} ${Y + +j(6)}`
        + ` Q${x + w / 2} ${Y + 3 + +j(7)} ${x + r} ${Y + +j(8)} Q${x} ${Y} ${x + +j(9)} ${Y - r}`
        + ` Q${x - 3 + +j(10)} ${y + h / 2} ${x + +j(11)} ${y + r} Q${x} ${y} ${x + r + 6} ${y + +j(12)}`;
    },
    // ellipse traced as a closed wobbly polyline
    wobEll(cx, cy, rx, ry, sd = 1, n = 44, amp = 2.4) {
      const p = [];
      for (let i = 0; i <= n; i++) {
        const a = (i / n) * Math.PI * 2, k = 1 + (amp / Math.max(rx, ry)) * Math.sin(a * 3 + sd);
        p.push(f1(cx + Math.cos(a) * rx * k) + " " + f1(cy + Math.sin(a) * ry * k));
      }
      return "M" + p.join(" L");
    },
    // zig-zag colouring hatch over a box, spilling `ov` px past the edge; o = { g: gap, s: slant, ov, seed, v: vertical }
    hatch(x, y, w, h, o = {}) {
      const g = o.g || 36, ov = o.ov ?? 7, sd = o.seed || 1, V = !!o.v;
      const A0 = V ? y : x, B0 = V ? x : y, AW = V ? h : w, BH = V ? w : h, s = o.s ?? BH * 0.4;
      const lo = A0 - ov, hi = A0 + AW + ov, pts = [];
      for (let u = lo - s, i = 0; u <= hi + g / 2; u += g / 2, i++) {
        const j = 3.5 * Math.sin(i * 1.93 + sd), k = 2.5 * Math.sin(i * 0.71 + sd * 2);
        const a = Math.min(hi, Math.max(lo, i % 2 ? u + s : u)) + k;
        const b = i % 2 ? B0 - ov - j : B0 + BH + ov + j;
        pts.push(V ? [b, a] : [a, b]);
      }
      return "M" + pts.map((q) => f1(q[0]) + " " + f1(q[1])).join(" L");
    },
    // the same hatch clipped to an ellipse
    hatchEll(cx, cy, rx, ry, o = {}) {
      const g = o.g || 36, ov = o.ov ?? 7, sd = o.seed || 1, s = o.s ?? 40, pts = [];
      const half = (xx) => { const q = (xx - cx) / rx; return q * q >= 1 ? 0 : ry * Math.sqrt(1 - q * q); };
      for (let u = cx - rx - ov, i = 0; u <= cx + rx + ov; u += g / 2, i++) {
        const j = 3.5 * Math.sin(i * 1.93 + sd);
        const a = Math.min(cx + rx, Math.max(cx - rx, i % 2 ? u + s : u));
        pts.push(f1(a) + " " + f1(i % 2 ? cy - half(a) - ov - j : cy + half(a) + ov + j));
      }
      return "M" + pts.join(" L");
    },
    // cursive scribble standing in for handwriting (humps, word gaps)
    scrib(x0, x1, y, sd = 1) {
      const n = Math.max(2, Math.round((x1 - x0) / 17));
      let d = `M${x0} ${y}`;
      for (let i = 1; i <= n; i++) {
        const x = x0 + ((x1 - x0) * i) / n, up = (i % 3 === 0 ? -17 : -9) + 2 * Math.sin(i * 1.3 + sd);
        const yy = y + 2 * Math.sin(i * 2.1 + sd);
        d += i % 7 === 0 ? ` M${f1(x + 6)} ${f1(yy)}` : ` Q${f1(x - 9)} ${f1(y + up)} ${f1(x)} ${f1(yy)}`;
      }
      return d;
    },
    star(cx, cy, R, r, n = 5) {
      const p = [];
      for (let i = 0; i < n * 2; i++) {
        const a = -Math.PI / 2 + (i * Math.PI) / n, q = i % 2 ? r : R;
        p.push(f1(cx + Math.cos(a) * q) + " " + f1(cy + Math.sin(a) * q));
      }
      return "M" + p.join(" L") + " Z";
    },
  };

  /* ---------- texture packs: SVG <defs> strings with ids prefixed by the scene id ---------- */
  const style = {
    // crayon-book: wobbly wax line, speckled wax on paper tooth, wobbly lettering; turbulences get class `<p>-turb` for boil()
    crayon: {
      defs: (p, W = 1080, H = 1920) => `
        <filter id="${p}-fline" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}" color-interpolation-filters="sRGB">
          <feTurbulence class="${p}-turb" type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="1" result="wob"/>
          <feDisplacementMap in="SourceGraphic" in2="wob" scale="4.5" xChannelSelector="R" yChannelSelector="G" result="moved"/>
          <feTurbulence class="${p}-turb" type="fractalNoise" baseFrequency="0.75" numOctaves="2" seed="3" result="grain"/>
          <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  5 0 0 0 -1.6" result="ga"/>
          <feComposite in="moved" in2="ga" operator="in"/>
        </filter>
        <filter id="${p}-fwax" filterUnits="userSpaceOnUse" x="0" y="0" width="${W}" height="${H}" color-interpolation-filters="sRGB">
          <feTurbulence class="${p}-turb" type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="2" result="wob"/>
          <feDisplacementMap in="SourceGraphic" in2="wob" scale="3.5" xChannelSelector="R" yChannelSelector="G" result="moved"/>
          <feTurbulence class="${p}-turb" type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="tooth"/>
          <feColorMatrix in="tooth" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  6 0 0 0 -2.1" result="ta"/>
          <feComposite in="moved" in2="ta" operator="in"/>
        </filter>
        <filter id="${p}-ftxt" x="-10%" y="-25%" width="120%" height="150%" color-interpolation-filters="sRGB">
          <feTurbulence class="${p}-turb" type="fractalNoise" baseFrequency="0.04" numOctaves="2" seed="5" result="wob"/>
          <feDisplacementMap in="SourceGraphic" in2="wob" scale="3" xChannelSelector="R" yChannelSelector="G" result="moved"/>
          <feTurbulence class="${p}-turb" type="fractalNoise" baseFrequency="0.8" numOctaves="2" seed="6" result="grain"/>
          <feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  4 0 0 0 -1.1" result="ga"/>
          <feComposite in="moved" in2="ga" operator="in"/>
        </filter>`,
    },
    // blueprint: 45-degree section hatching and a soft white pen-tip glow
    blueprint: {
      defs: (p) => `
        <pattern id="${p}-hatch" width="12" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <path d="M0 0V12" stroke="rgba(231,240,249,.55)" stroke-width="1.2"/>
        </pattern>
        <filter id="${p}-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>`,
    },
  };

  /* ---------- a scene bound helper set ---------- */
  function scene(id, o = {}) {
    const sc = window.__vv.scenes[id];
    if (!sc) throw new Error("MF.scene: unknown scene " + id);
    const DUR = sc.end - sc.start, S = sc.start, BEAT = 60 / (o.bpm || 100);
    const tl = gsap.timeline({ paused: true });
    // HyperFrames runs a scene script with its own `document`; the scene passes it in: MF.scene("s3", { doc: document })
    const doc = o.doc || document;
    const root = doc.getElementById(id + "-root") || doc.querySelector(`[data-composition-id="${id}"]`);
    if (!root) throw new Error("MF.scene: no root for scene " + id + " (pass { doc: document } from the scene script)");
    const $ = (x) => {
      if (typeof x !== "string") return x;
      const el = x[0] === "#" ? doc.getElementById(x.slice(1)) : x[0] === "." ? root.querySelector(x) : doc.getElementById(`${id}-${x}`);
      if (!el) throw new Error(`MF ${id}: không thấy phần tử ${x}`);
      return el;
    };
    const A = (key) => window.__vv.local(id, key);
    const exitAt = DUR - 0.3;
    let penAt = null;
    const K = {
      id, tl, DUR, S, A, $, root, geo, exitAt,
      // beat times (scene-local) between from and to, counted from 0 s of the video
      beats(from = 0, to = DUR) { const r = []; for (let k = Math.ceil((S + from) / BEAT); k * BEAT - S <= to; k++) r.push(k * BEAT - S); return r; },
      // draw a stroke on in visible stabs; hidden until it starts (no round-cap dot on blank paper); optional pen follows the tip
      draw(el, t, dur = 0.6, d = {}) {
        el = $(el); const n = d.steps ?? 8, len = el.getTotalLength() + 2, op = d.opacity ?? 1;
        gsap.set(el, { strokeDasharray: len, opacity: 0 });
        tl.set(el, { opacity: 0 }, 0); tl.set(el, { opacity: op }, t);
        tl.fromTo(el, { strokeDashoffset: len }, { strokeDashoffset: 0, duration: dur, ease: n ? `steps(${n})` : "power1.inOut" }, t);
        if (d.pen) {
          const pen = $(d.pen), k = n || 12;
          for (let i = 0; i <= k; i++) {
            const q = el.getPointAtLength(((len - 2) * i) / k);
            tl.set(pen, { x: q.x, y: q.y, opacity: 1 }, t + (dur * i) / k);
            penAt = q;
          }
        }
        return t + dur;
      },
      // letters appear left to right, each tilted and lifted by a fixed formula (reads hand-set, never random)
      write(el, t, dur = 0.35, d = {}) {
        el = $(el); const sd = d.seed ?? 1, tilt = d.tilt ?? 4, lift = d.lift ?? 1.5;
        const chars = Array.from(el.textContent.normalize("NFC")); el.textContent = "";
        chars.forEach((ch, i) => {
          const s = document.createElement("span");
          s.setAttribute("data-layout-allow-overlap", ""); s.style.display = "inline-block"; s.style.whiteSpace = "pre";
          s.textContent = ch; el.appendChild(s);
          gsap.set(s, { opacity: 0, rotation: tilt * Math.sin(i * 2.39 + sd), y: lift + lift * Math.sin(i * 1.37 + sd * 1.7) });
          tl.set(s, { opacity: 0 }, 0); tl.set(s, { opacity: 1 }, t + (dur * i) / chars.length);
        });
        return t + dur;
      },
      // colour a shape row by row (clip-path inset sweeping in the hatch direction)
      colour(els, t, dur = 0.4, d = {}) {
        const n = d.steps ?? 6, from = d.from || "left";
        const start = { left: "inset(-40px 100% -40px -40px)", right: "inset(-40px -40px -40px 100%)", top: "inset(-40px -40px 100% -40px)", bottom: "inset(100% -40px -40px -40px)" }[from];
        [].concat(els).forEach((e) => tl.fromTo($(e), { clipPath: start }, { clipPath: "inset(-40px -40px -40px -40px)", duration: dur, ease: `steps(${n})` }, t));
        return t + dur;
      },
      // keep a hatch inside a shape, grown by `grow` (1.04 = spills a few px past the outline, like a child colouring)
      clip(fill, shape, grow = 1.04) {
        fill = $(fill); shape = $(shape);
        const svg = shape.ownerSVGElement, NS = "http://www.w3.org/2000/svg";
        let defs = svg.querySelector("defs"); if (!defs) { defs = doc.createElementNS(NS, "defs"); svg.prepend(defs); }
        const b = shape.getBBox(), cx = b.x + b.width / 2, cy = b.y + b.height / 2, cpId = `${fill.id}-cp`;
        const cp = doc.createElementNS(NS, "clipPath"); cp.setAttribute("id", cpId);
        const u = doc.createElementNS(NS, "path"); u.setAttribute("d", shape.getAttribute("d"));
        u.setAttribute("transform", `translate(${f1(cx)} ${f1(cy)}) scale(${grow}) translate(${f1(-cx)} ${f1(-cy)})`);
        cp.appendChild(u); defs.appendChild(cp);
        // clip a wrapper, so colour()'s clip-path sweep on the hatch itself keeps working
        const g = doc.createElementNS(NS, "g"); g.setAttribute("clip-path", `url(#${cpId})`);
        fill.parentNode.insertBefore(g, fill); g.appendChild(fill);
        return fill;
      },
      // place a Lucide icon (mf-icons.js) inside an <svg> or <g> of the scene as <g id="<scene>-<as>">; strokes stay `width` px at any size
      icon(name, parent, d = {}) {
        const NS = "http://www.w3.org/2000/svg", size = d.size ?? 160, k = size / 24;
        const g = doc.createElementNS(NS, "g");
        g.setAttribute("id", `${id}-${d.as || name}`);
        g.setAttribute("transform", `translate(${f1((d.x ?? 0) - size / 2)} ${f1((d.y ?? 0) - size / 2)}) scale(${k})`);
        g.setAttribute("fill", "none"); g.setAttribute("stroke", d.stroke || "currentColor");
        g.setAttribute("stroke-width", f1((d.width ?? 6) / k)); g.setAttribute("stroke-linecap", "round"); g.setAttribute("stroke-linejoin", "round");
        if (d.filter) g.setAttribute("filter", `url(#${d.filter})`);
        g.innerHTML = MF.icon(name);
        $(parent).appendChild(g);
        return g;
      },
      // draw every stroke of an icon (or any <g>) one after another inside `dur`
      drawIcon(g, t, dur = 0.8, d = {}) {
        const parts = Array.from($(g).querySelectorAll("path,circle,ellipse,rect,line,polyline,polygon")), each = dur / parts.length;
        parts.forEach((p, i) => K.draw(p, t + i * each, each, { steps: d.steps ?? 4, opacity: d.opacity }));
        return t + dur;
      },
      pop(els, t, dur = 0.25, d = {}) {
        tl.fromTo([].concat(els).map($), { scale: 0, opacity: 0, transformOrigin: d.origin || "50% 50%" },
          { scale: 1, opacity: 1, duration: dur, ease: d.ease || "back.out(1.7)" }, t);
        return t + dur;
      },
      // camera: page turn in, slow drift on an inner wrapper, page turn out in the last 0.3 s
      pageIn(sel = `#${id}-stage`, dur = 0.45) {
        tl.fromTo($(sel), { rotation: 6, x: 260, opacity: 0, transformOrigin: "0% 50%" }, { rotation: 0, x: 0, opacity: 1, duration: dur, ease: "power3.out" }, 0);
      },
      drift(sel = `#${id}-cam`, d = {}) {
        tl.fromTo($(sel), { scale: 1, x: 0, y: 0, transformOrigin: "50% 45%" }, { scale: d.scale ?? 1.04, x: d.x ?? -14, y: d.y ?? -12, duration: DUR, ease: "none" }, 0);
      },
      pageOut(sel = `#${id}-stage`) {
        tl.to($(sel), { x: -240, rotation: -5, opacity: 0, duration: 0.3, ease: "power2.in" }, exitAt);
      },
      // re-seed every texture on twos at 12 fps so held frames still breathe
      boil(selector = `.${id}-turb`, fps = 6) {
        const turbs = Array.from(root.querySelectorAll(selector));
        for (let t = 0, k = 0; t < DUR; t += 1 / fps, k++) turbs.forEach((tb, j) => tl.set(tb, { attr: { seed: 1 + ((k + j * 2) % 5) } }, t));
      },
      // register the timeline; warn (console, read by tools/gate.py) when something new still appears in the last 0.6 s before the exit
      done(d = {}) {
        const limit = (d.last ? DUR : exitAt) - 0.6;
        const late = tl.getChildren(true, true, false).filter((c) => c.duration() > 0.05 && c.endTime() > limit && c.startTime() < exitAt - 0.01 && c.startTime() > 0.01 && !(c.vars && c.vars.mfIdle));
        if (late.length) console.warn(`MF ${id}: ${late.length} tween kết thúc sát cuối cảnh (sau ${limit.toFixed(2)} s); hình cuối có thể chưa xong`);
        window.__timelines[id] = tl;
        return tl;
      },
    };
    return K;
  }

  // Lucide icon markup by name (24x24 box); throws with a hint when the name does not exist
  function icon(name) {
    const m = (window.MF_ICONS || {})[name];
    if (!m) throw new Error(`MF.icon: không có icon "${name}" (tra tên: python tools/icon_find.py <từ khóa>)`);
    return m;
  }

  window.MF = { scene, geo, style, icon, version: "2" };
})();
