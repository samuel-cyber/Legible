# Gold set built from LaTeX source

Existing (hand-kept) entries preserved: 6  ·  generated from source: 146

Source equations are paired with detected PDF regions by a reading-order alignment (matching pairs must run in the same order on both sides); a pair is kept only when the PDF glyph letters and digits plausibly match the source. Everything else is skipped, fail-closed.

## lec_notes.pdf

- Source: `eval/sources/uh_lecture/lec_notes.tex`
- Simple source equations: **114**  ·  detected regions: **192**  ·  kept: **96**  ·  unmatched regions (prose/fragments): **96**

| id | page | kind | LaTeX | PDF glyph text |
| --- | --- | --- | --- | --- |
| uh_p1e1 | 1 | align | `+ : F(I) \times F(I) \to F(I), \cdot : \mathbb R \times F(I) \to F(I),` | `+:F(I)×F(I)→F(I),·:R×F(I)→F(I),` |
| uh_p1e2 | 1 | align | `(u + v)(x) = u(x) + v(x), (cu)(x) = cu(x), x \in I.` | `(u+v)(x)=u(x)+v(x),(cu)(x)=cu(x),x∈I.` |
| uh_p1e3 | 1 | align | `C(I) = \{ u \in F(I) \mid \text{$u$ is continuous on $I$}\}.` | `C(I)={u∈F(I)\|uiscontinuousonI}.` |
| uh_p2e4 | 2 | align | `C^k(I) = \{ u \in C(I) \mid u', \dots, u^{(k)} \in C(I)\}, k = 1,2,\dots.` | `k′(k)C(I)={u∈C(I)\|u,...,u∈C(I)},k=1,2,....` |
| uh_p2e5 | 2 | align | `L^p(I) = \{u \in F(I) \mid \int_I \|u(x)\|^p dx < \infty \}, p \ge 1.` | `∫ppL(I)={u∈F(I)\|\|u(x)\|dx<∞},p≥1.I` |
| uh_p2e6 | 2 | align | `\\|u\\|_{L^p(I)} = \left( \int_I \|u(x)\|^p dx \right)^{\frac1p}.` | `(∫)1p∥∥\|\|puLp(I)=u(x)dx.I` |
| uh_p2e7 | 2 | align | `(u, v) = \int_I u(x) v(x) dx, (\cdot, \cdot) : L^2(I) \times L^2(I) \to \mathbb R.` | `∫··2×2→R(u,v)=u(x)v(x)dx,(,):L(I)L(I).I` |
| uh_p2e8 | 2 | align | `1, x, x^2, \dots, x^n` | `1,x,x2,...,xn` |
| uh_p2e9 | 2 | align | `\mathbb P_n \subset C^k(I)` | `kPn⊂C(I)` |
| uh_p2e10 | 2 | align | `C^k(I) \subset L^2(I) \subset F(I).` | `Ck(I)⊂L2(I)⊂F(I).` |
| uh_p2e11 | 2 | align | `(u, v) \le \\|u\\| \\|v\\| u,v \in V.` | `(u,v)≤∥u∥∥v∥u,v∈V.` |
| uh_p3e12 | 3 | align | `(u - s, v) = 0 \text{for all $v \in S$}.` | `(u-s,v)=0forallv∈S.` |
| uh_p3e13 | 3 | align | `I = [0,1]` | `I=[0,1]` |
| uh_p3e14 | 3 | align | `\mathcal V = \{ v \in C^1(I) : v(0) = v(1) = 0 \},` | `1V={v∈C(I):v(0)=v(1)=0},` |
| uh_p3e15 | 3 | align | `(u', v') = (f, v) \text{for all $v \in \mathcal V$}.` | `(u′,v′)=(f,v)forallv∈V.` |
| uh_p3e16 | 3 | align | `a(u, v) = (u', v'), a : \mathcal V \times \mathcal V \to \mathbb R,` | `′′V×V→Ra(u,v)=(u,v),a:,` |
| uh_p3e17 | 3 | align | `L(v) = (f,v), L : \mathcal V \to \mathbb R.` | `L(v)=(f,v),L:V→R.` |
| uh_p4e18 | 4 | align | `a(u_S,v) = L(v) \text{for all $v \in S$}.` | `a(uS,v)=L(v)forallv∈S.` |
| uh_p4e19 | 4 | align | `a(u_S,v) = L(v) \text{for all $v \in S$}.` | `forall∈a(uS,v)=L(v)vS.` |
| uh_p4e20 | 4 | align | `a(u, v) = L(v) \text{for all $v \in V$}.` | `a(u,v)=L(v)forallv∈V.` |
| uh_p4e21 | 4 | align | `a(u-u_S,v) = 0 \text{for all $v \in S$}.` | `a(u-u,v)=0forallv∈S.S` |
| uh_p4e22 | 4 | align | `a(u-u_S,v) = a(u, v) - a(u_S, v) = L(v) - L(v) = 0.` | `a(u-u,v)=a(u,v)-a(u,v)=L(v)-L(v)=0.SS` |
| uh_p5e23 | 5 | align | `0 = x_0 < x_1 < \dots < x_n = 1,` | `0=x<x<···<x=1,01n` |
| uh_p5e24 | 5 | align | `\mathcal I_h u(x_i) = u(x_i), i=0,\dots,n.` | `Iu(x)=u(x),i=0,...,n.hii` |
| uh_p5e25 | 5 | align | `\\|u - \mathcal I_h u\\|_{L^\infty(I)} \lesssim \\|(h \partial)^2 u\\|_{L^\infty(I)}.` | `∥u-Iu∥∞≲∥(h∂)2u∥∞.hL(I)L(I)` |
| uh_p6e26 | 6 | align | `c_1 \phi_1 + \dots + c_{n-1} \phi_{n-1} = 0` | `c1φ1+···+cn-1φn-1=0` |
| uh_p6e27 | 6 | align | `a(u, v) = (u', v'), a : V \times V \to \mathbb R,` | `′′a(u,v)=(u,v),a:V×V→R,` |
| uh_p6e28 | 6 | align | `a(u, v) = L(v) \text{for all $v \in V$},` | `a(u,v)=L(v)forallv∈V,` |
| uh_p7e29 | 7 | align | `(u,v) = \int_I u(x)v(x)dx.` | `∫(u,v)=u(x)v(x)dx.I` |
| uh_p7e30 | 7 | align | `\\|u-v\\|_X < \delta \implies \\|Au-Av\\|_Y < \epsilon.` | `∥u-v∥X<δ=⇒∥Au-Av∥Y<ε.` |
| uh_p7e31 | 7 | align | `\\|Au-Av\\|_Y = \\|A(u-v)\\|_Y \le C \\|u-v\\|_X < C \delta = \epsilon.` | `∥Au-Av∥Y=∥A(u-v)∥Y≤C∥u-v∥X<Cδ=ε.` |
| uh_p8e32 | 8 | align | `\\|Au\\|_Y \le C \\|u\\|_X` | `∥Au∥≤C∥u∥YX` |
| uh_p8e33 | 8 | align | `\\|Au\\|_Y \le p(u),` | `∥Au∥≤p(u),Y` |
| uh_p8e34 | 8 | align | `\{x \in I \mid u(x) \ne 0\}.` | `{x∈I\|u(x)̸=0}.` |
| uh_p9e35 | 9 | align | `K = [x_L + \delta, x_R - \delta].` | `K=[x+δ,x-δ].LR` |
| uh_p9e36 | 9 | align | `\\|u1_K - u\\| \le 1/j.` | `∥u1K-u∥≤1/j.` |
| uh_p9e37 | 9 | align | `\\|u_j - u\\| \le \\|u_j - u1_K\\| + \\|u1_K - u\\| \le 2/j \to 0, j \to \infty.` | `∥u-u∥≤∥u-u1∥+∥u1-u∥≤2/j→0,j→∞.jjKK` |
| uh_p9e38 | 9 | align | `L_u(\phi) = L_v(\phi), \text{for all $\phi \in C_0^\infty(I)$}.` | `∞Lu(φ)=Lv(φ),forallφ∈C0(I).` |
| uh_p10e39 | 10 | align | `A(w) = (u - v, w), A : L^2(I) \to \mathbb R,` | `2A(w)=(u-v,w),A:L(I)→R,` |
| uh_p10e40 | 10 | align | `L(\phi) = (-1)^k (f, \phi^{(k)}), \phi \in C_0^\infty(I).` | `∞L(φ)=(-1)k(f,φ(k)),φ∈C(I).0` |
| uh_p11e41 | 11 | align | `(-1)^2 (u, \phi'') = (-1)^2 (u, (\phi')') = (-1) (w, \phi').` | `2′′2′′′(-1)(u,φ)=(-1)(u,(φ))=(-1)(w,φ).` |
| uh_p11e42 | 11 | align | `L : C_0^\infty(I) \to \mathbb R,` | `∞L:C(I)→R,0` |
| uh_p11e43 | 11 | align | `H^k(I) = \{ u \in L^2(I) \mid u', \dots, u^{(k)} \in L^2(I)\}.` | `k{∈2\|′(k)∈2}H(I)=uL(I)u,...,uL(I).` |
| uh_p11e44 | 11 | align | `(u,v)_{H^1(I)} = (u,v) + (u', v').` | `′′(u,v)H1(I)=(u,v)+(u,v).` |
| uh_p12e45 | 12 | align | `\\|E u\\|_{L^2(\mathbb R)} \lesssim \\|u\\|_{L^2(I)}, \\|E u\\|_{H^1(\mathbb R)} \lesssim \\|u\\|_{H^1(I)}.` | `∥Eu∥2≲∥u∥2,∥Eu∥1≲∥u∥1.L(R)L(I)H(R)H(I)` |
| uh_p12e46 | 12 | align | `\\|u\\|_{L^\infty(I)} \lesssim \\|u\\|_{H^1(I)}.` | `∥u∥L∞(I)≲∥u∥H1(I).` |
| uh_p12e47 | 12 | align | `H_0^1(I) = \{u \in H^1(I) \mid u(x_L) = 0 = u(x_R) \}.` | `H1(I)={u∈H1(I)\|u(x)=0=u(x)}.0LR` |
| uh_p12e48 | 12 | align | `\\|u\\|_{H^1(I)} \lesssim \\|u'\\|_{L^2(I)}, u \in H_0^1(I).` | `∥u∥≲∥u′∥,u∈H1(I).H1(I)L2(I)0` |
| uh_p12e49 | 12 | align | `I = [0,1], V = H_0^1(I),` | `1I=[0,1],V=H(I),0` |
| uh_p12e50 | 12 | align | `a(u, v) = (u', v'), a : V \times V \to \mathbb R.` | `′′×→Ra(u,v)=(u,v),a:VV.` |
| uh_p12e51 | 12 | align | `L(v) = (f, v), L : V \to \mathbb R.` | `L(v)=(f,v),L:V→R.` |
| uh_p13e52 | 13 | align | `a(u, v) = L(v) \text{for all $v \in V$},` | `a(u,v)=L(v)forallv∈V,` |
| uh_p13e53 | 13 | align | `Av = a(u,v) - L(v), A : V \to \mathbb R,` | `Av=a(u,v)-L(v),A:V→R,` |
| uh_p13e54 | 13 | align | `\\|(h\partial)(u-u_h)\\| \lesssim \\|(h \partial)^2 u\\|_{L^\infty(I)}.` | `2∥(h∂)(u-u)∥≲∥(h∂)u∥∞.hL(I)` |
| uh_p13e55 | 13 | align | `\\|w\\|_E^2 = a(w,w) = \\|w'\\|^2, w \in V,` | `2′2∥w∥E=a(w,w)=∥w∥,w∈V,` |
| uh_p14e56 | 14 | align | `\mathcal I_h : H^1(I) \to S.` | `1Ih:H(I)→S.` |
| uh_p14e57 | 14 | align | `\\|\mathcal I_h u\\|_{H^1(I)} \lesssim \\|u\\|_{H^1(I)}, u \in H^1(I).` | `∥Iu∥1≲∥u∥1,u∈H1(I).hH(I)H(I)` |
| uh_p14e58 | 14 | align | `\\|\mathcal I_h u\\|_{H^1(I)} \lesssim \\|u\\|_{H^1(I)}, u \in C^\infty(I).` | `∥Iu∥≲∥u∥,u∈C∞(I).hH1(I)H1(I)` |
| uh_p14e59 | 14 | align | `\\|\mathcal I_h u\\| \lesssim \\|\mathcal I_h u\\|_{L^\infty(I)} \le \\|u\\|_{L^\infty(I)} \lesssim \\|u\\|_{H^1(I)}, u \in H^1(I),` | `1∥Ihu∥≲∥Ihu∥L∞(I)≤∥u∥L∞(I)≲∥u∥H1(I),u∈H(I),` |
| uh_p14e60 | 14 | align | `\\|\partial \mathcal I_h u\\| \lesssim \\|u\\|_{H^1(I)}, u \in C^\infty(I).` | `∥∂Iu∥≲∥u∥1,u∈C∞(I).hH(I)` |
| uh_p14e61 | 14 | align | `\partial \mathcal I_h u\|_{I_i} = \frac{u(x_i) - u(x_{i-1})}{x_i - x_{i-1}}.` | `u(xi)-u(xi-1)∂Ihu\|I=.ix-xii-1` |
| uh_p14e62 | 14 | align | `u(x_i) - u(x_{i-1}) = \int_{I_i} u'(x) dx \le \|x_i - x_{i-1}\|^{\frac12} \\|u'\\|_{L^2(I_i)}.` | `∫1u(x)-u(x)=u′(x)dx≤\|x-x\|2∥u′∥.ii-1ii-1L2(Ii)Ii` |
| uh_p15e63 | 15 | align | `\mathcal I_h u = \sum_{i=0}^n u(x_i) \phi_i,` | `∑nIu=u(x)φ,hiii=0` |
| uh_p15e64 | 15 | align | `\\|\mathcal I_h u\\|_{H^1(I)} \le \\|u\\|_{L^\infty(I)} \sum_{i=0}^n \\|\phi_i\\|_{H^1(I)} \le C_h \\|u\\|_{H^1(I)},` | `∑n∥Iu∥≤∥u∥∞∥φ∥≤C∥u∥,hH1(I)L(I)iH1(I)hH1(I)i=0` |
| uh_p15e65 | 15 | align | `\\|u - \mathcal I_h u\\| + \\|(h\partial)(u - \mathcal I_h u)\\| \lesssim \\|(h\partial)^2 u\\|, u \in H^2(I).` | `∥u-Iu∥+∥(h∂)(u-Iu)∥≲∥(h∂)2u∥,u∈H2(I).hh` |
| uh_p15e66 | 15 | align | `w(x) = \int_\xi^x w'(y) dy \le \|x - \xi\|^{\frac12} \\|w'\\|_{L^2(I_i)},` | `ii∫x′1′w(x)=w(y)dy≤\|x-ξ\|2∥w∥L2(I),iξ` |
| uh_p15e67 | 15 | align | `\\|w\\|_{L^2(I_i)}^2 \le \int_{I_i} \|x - \xi\| dx\, \\|w'\\|_{L^2(I_i)}^2 \le h^2 \\|w'\\|_{L^2(I_i)}^2 = \\|(h\partial) w\\|_{L^2(I_i)}^2.` | `∫′′2≤\|x-ξ\|dx∥w∥2≤h2∥w∥2=∥(h∂)w∥2.L2(Ii)L2(Ii)L2(Ii)L2(Ii)Ii` |
| uh_p15e68 | 15 | align | `\\|(h\partial)(u - \mathcal I_h u)\\|_{L^2(I_i)}^2 \le \\|(h\partial)^2 (u - \mathcal I_h u)\\|_{L^2(I_i)}^2 = \\|(h\partial)^2 u\\|_{L^2(I_i)}^2,` | `222222≤∥(h∂)(u-Ihu)∥2=∥(h∂)u∥2,L(Ii)L(Ii)L(Ii)` |
| uh_p15e69 | 15 | align | `\\|(u - \mathcal I_h u)\\|_{L^2(I_i)}^2 \le \\|(h\partial)(u - \mathcal I_h u)\\|_{L^2(I_i)}^2 \le \\|(h\partial)^2 u\\|_{L^2(I_i)}^2.` | `2222∥(u-Ihu)∥L2(I)≤∥(h∂)(u-Ihu)∥L2(I)≤∥(h∂)u∥L2(I).iii` |
| uh_p16e70 | 16 | align | `L : H \to \mathbb R` | `L:H→R` |
| uh_p16e71 | 16 | align | `L(v) = (u,v), v \in H.` | `L(v)=(u,v),v∈H.` |
| uh_p16e72 | 16 | align | `\\|u-u_h\\| \lesssim \\|(h \partial)^2 u\\|.` | `∥u-u∥≲∥(h∂)2u∥.h` |
| uh_p16e73 | 16 | align | `\\|u-u_h\\|^2 = L(u - u_h) = a(w, u - u_h).` | `2∥u-uh∥=L(u-uh)=a(w,u-uh).` |
| uh_p17e74 | 17 | align | `a(\mathcal I_h w, u - u_h) = 0.` | `a(Iw,u-u)=0.hh` |
| uh_p17e75 | 17 | align | `\\|u-u_h\\|^2 = a(w - \mathcal I_h w, u - u_h) \le \\|\partial(w - \mathcal I_h)\\|\\|\partial(u-u_h)\\|.` | `∥u-u∥2=a(w-Iw,u-u)≤∥∂(w-I)∥∥∂(u-u)∥.hhhhh` |
| uh_p17e76 | 17 | align | `\\|w''\\| = \\|u - u_h\\|.` | `′′∥w∥=∥u-u∥.h` |
| uh_p17e77 | 17 | align | `\\|(h\partial)(w - \mathcal I_h)\\| \lesssim \\|(h\partial)^2 w\\|.` | `2∥(h∂)(w-Ih)∥≲∥(h∂)w∥.` |
| uh_p17e78 | 17 | align | `\\|u-u_h\\| \le \\|(h\partial)(u-u_h)\\| \lesssim \\|(h \partial)^2 u\\|.` | `2∥u-uh∥≤∥(h∂)(u-uh)∥≲∥(h∂)u∥.` |
| uh_p17e79 | 17 | align | `a(u_h,v) = L(v) \text{for all $v \in P_{h,0}^k$}.` | `forallka(uh,v)=L(v)v∈Ph,0.` |
| uh_p17e80 | 17 | align | `\xi_m = x_{i-1} + \frac m k (x_i - x_{i-1}) \in I_i, m = 0,\dots,k.` | `mξ=x+(x-x)∈I,m=0,...,k.mi-1ii-1ik` |
| uh_p17e81 | 17 | align | `\mathcal L_m(x) = \prod_{l=0,l \ne m}^k \frac{x - \xi_l}{\xi_m - \xi_l}.` | `k∏x-ξlLm(x)=.ξ-ξl=0,l̸=mml` |
| uh_p18e82 | 18 | align | `\mathcal I^k_{h,i} u(x) = \sum_{m=0}^k u(\xi_m) \mathcal L_m(x), u \in C(I_i).` | `∑kIku(x)=u(ξ)L(x),u∈C(I).h,immim=0` |
| uh_p18e83 | 18 | align | `\\|\mathcal I_{h,i}^k u\\|_{H^1(I_i)} \lesssim \\|u\\|_{H^1(I_i)}, u \in H^1(I_i).` | `∥Iku∥≲∥u∥,u∈H1(I).h,iH1(Ii)H1(Ii)i` |
| uh_p18e84 | 18 | align | `\sum_{m=0}^{l+1} \\|(h\partial)^m (u - \mathcal I_{h,i}^k u)\\|_{L^2(I_i)} \lesssim \\|(h\partial)^{l+1} u\\|_{L^2(I_i)}, u \in H^{l+1}(I_i).` | `∑l+1mkl+1l+1∥(h∂)(u-Iu)∥L2(I)≲∥(h∂)u∥L2(I),u∈H(Ii).h,iiim=0` |
| uh_p18e85 | 18 | align | `\\|(h\partial)(u-u_h)\\| \lesssim \\|(h \partial)^{l+1} u\\|,` | `∥(h∂)(u-u)∥≲∥(h∂)l+1u∥,h` |
| uh_p18e86 | 18 | align | `\\|u-u_h\\| \lesssim \\|(h \partial)^{l+1} u\\|.` | `l+1∥u-uh∥≲∥(h∂)u∥.` |
| uh_p18e87 | 18 | align | `V = H_0^1(\Omega) = \{u \in H^1(\Omega) \mid u\|_{\partial \Omega} = 0\},` | `11V=H0(Ω)={u∈H(Ω)\|u\|∂Ω=0},` |
| uh_p19e88 | 19 | align | `a(u, v) = L(v) \text{for all $v \in V$}.` | `a(u,v)=L(v)forallv∈V.` |
| uh_p19e89 | 19 | align | `\mathcal I_h : V \to V_h,` | `Ih:V→Vh,` |
| uh_p19e90 | 19 | align | `\\|(h\nabla)(u - \mathcal I_h u)\\|_{L^2(\Omega)} \lesssim \\|(hD)^2 u\\|_{L^2(\Omega)},` | `∥(h∇)(u-Iu)∥2≲∥(hD)2u∥2,hL(Ω)L(Ω)` |
| uh_p19e91 | 19 | align | `\\|D^2 u\\|_{L^2(\Omega)} \lesssim \\|f\\|_{L^2(\Omega)}.` | `∥D2u∥≲∥f∥.L2(Ω)L2(Ω)` |
| uh_p19e92 | 19 | align | `a(u_h,v) = L(v) \text{for all $v \in V_h$},` | `a(u,v)=L(v)forallv∈V,hh` |
| uh_p19e93 | 19 | align | `\\|u - u_h\\|_{L^2(\Omega)} + \\|(h\nabla)(u - u_h)\\|_{L^2(\Omega)} \lesssim \\|(hD)^2 u\\|_{L^2(\Omega)}.` | `2∥u-uh∥L2(Ω)+∥(h∇)(u-uh)∥L2(Ω)≲∥(hD)u∥L2(Ω).` |
| uh_p19e94 | 19 | align | `\\|\cdot\\| = \\|\cdot\\|_{L^2(\Omega)}, \\|\cdot\\|_E = a(\cdot, \cdot),` | `∥·∥=∥·∥2,∥·∥=a(·,·),L(Ω)E` |
| uh_p20e95 | 20 | align | `\\|(h\nabla)(w - \mathcal I_h)\\| \lesssim \\|h^2 D^2 w\\| \lesssim h^2 \\|u - u_h\\|,` | `222∥(h∇)(w-I)∥≲∥hDw∥≲h∥u-u∥,hh` |
| uh_p20e96 | 20 | align | `a(u,v) = \int_\Omega (\nabla u \cdot \nabla v + q u v)\, dx.` | `∫∇·∇a(u,v)=(uv+quv)dx.` |

### Skipped (48)

| kind | reason | LaTeX |
| --- | --- | --- |
| align | multi-line (2 rows) | `(u + (v + w))(x) = u(x) + (v+w)(x) = u(x) + v(x) + w(x)` |
| align | multi-line (2 rows) | `\\| u - s \\|^2 = (u - s, u - s) = (u - s, u - v) + (u - s, v - s) = (u - s, u - v)` |
| align | multi-line (2 rows) | `\begin{cases} -u'' = f \text{on $I$},` |
| align | multi-line (3 rows) | `\phi_i(x) = \begin{cases} \frac{x - x_{i-1}}{x_i - x_{i-1}} \text{if $x \in I_i$},` |
| align | multi-line (3 rows) | `S = \linspan \{ \phi_1,\dots,\phi_{n-1} \},` |
| align | multi-line (2 rows) | `\\|(h\partial)(u-u_S)\\| = h\\|u-u_S\\|_E = h \min_{v \in S}\\|u-v\\|_E \le \\|(h\partial)(u-\I_h` |
| align | multi-line (2 rows) | `\\|Au\\|_Y \le \\|Au_j\\|_Y + \\|Au - Au_j\\|_Y \le C \\|u_j\\|_X + \\|Au - Au_j\\|_Y` |
| align | multi-line (2 rows) | `C^\infty(I) = \{ u \mid \text{$u \in C^k(I)$ for all $k=0,1\dots$} \},` |
| align | multi-line (2 rows) | `1_K(x) = \begin{cases} 1 x \in K,` |
| align | signature too small to verify safely | `L_f(\phi) = (f, \phi),` |
| align | signature too small to verify safely | `-(f, \phi') = (f', \phi) = L_{f'}(\phi).` |
| align | multi-line (2 rows) | `u(x) = \begin{cases} 0 x < 0,` |
| align | multi-line (2 rows) | `w(x) = \begin{cases} 0 x < 0,` |
| align | multi-line (2 rows) | `H^1(I) = \{ u \in L^2(I) \mid \ \text{there is $w \in L^2(I)$ such that}` |
| align | multi-line (2 rows) | `((u + c \tilde u)', \phi) = -(u + c \tilde u, \phi') = -(u, \phi') - c (\tilde u, \phi') =` |
| align | signature too small to verify safely | `(u + c \tilde u)' = u' + c \tilde u'.` |
| align | signature too small to verify safely | `(u,u) + (u', u') \ge (u, u) > 0.` |
| align | multi-line (2 rows) | `\\|(h\partial)(u-u_h)\\| = h\\|u-u_h\\|_E = h \min_{v \in S}\\|u-v\\|_E \le \\|(h\partial)(u-\I_h` |
| align | multi-line (2 rows) | `\\|\p \I_h u\\|^2 = \sum_{i=1}^n \int_{I_i} \frac{\|u(x_i) - u(x_{i-1})\|^2}{\|x_i - x_{i-1}\|^2` |
| align | multi-line (2 rows) | `\\|(h\partial)(u-u_h)\\| = h\\|u-u_h\\|_E = h \min_{v \in S}\\|u-v\\|_E \le \\|(h\partial)(u-\I_h` |
| align | signature too small to verify safely | `\\|u''\\| = \\|f\\|.` |
| align | multi-line (2 rows) | `P^k_{h} = \{ u \in C(I) \mid \text{$u\|_{I_{i}} \in \mathbb P_k$ for $i=1,\dots,n$} \},` |
| align | signature too small to verify safely | `- \Delta u = f.` |
| align | signature too small to verify safely | `u\|_{\partial \Omega} = 0.` |
| align | multi-line (2 rows) | `a(u,v) = \int_\Omega \nabla u \cdot \nabla v\, dx, a : V \times V \to \R,` |
| align | multi-line (2 rows) | `\\|(h\nabla)(u-u_h)\\| = h\\|u-u_h\\|_E = h \min_{v \in V_h}\\|u-v\\|_E \le \\|(h\nabla)(u-\I_h u` |
| align | multi-line (2 rows) | `\\|u-u_h\\|^2 = L(u - u_h) = a(w, u - u_h). = a(w - \I_h w, u - u_h)` |
| align | multi-line (2 rows) | `- \Delta u + q u = f,` |
| align | multi-line (2 rows) | `-u'' - u = 0,` |
| align | multi-line (2 rows) | `- \Delta u + b\cdot\nabla u + q u = f,` |
| align | no matching glyph region in reading order | `\\|u\\|_{L^\infty(I)} = \sup_{x \in I} \|u(x)\|.` |
| align | no matching glyph region in reading order | `\mathbb P_n = \{p : \mathbb R \to \mathbb R \mid \text{$p$ is a polynomial of degree $\le ` |
| align | no matching glyph region in reading order | `u_S = \sum_{j=1}^n U_j \phi_j, K_{ij} = a(\phi_i, \phi_j), F_i = L(\phi_i), i,j=1,\dots,n.` |
| align | no matching glyph region in reading order | `\\|u-u_S\\|_E = \min_{v \in S} \\|u - v\\|_E.` |
| align | no matching glyph region in reading order | `h = \max_{i=1,\dots,n} \|x_i - x_{i-1}\|.` |
| align | no matching glyph region in reading order | `\mathcal I_h u(x) = \frac{x - x_{i-1}}{x_i - x_{i-1}} u(x_i) + \frac{x_{i} - x}{x_i - x_{i` |
| align | no matching glyph region in reading order | `\max_{i=1,\dots,n}\\|(h\partial)(u - \mathcal I_h u)\\|_{L^\infty(I_i)} \lesssim \\|(h \parti` |
| align | no matching glyph region in reading order | `v = c_1 \phi_1 + \dots + c_{n-1} \phi_{n-1},` |
| align | no matching glyph region in reading order | `f * g(x) = \int_\mathbb R f(y) g(x - y) dy` |
| align | no matching glyph region in reading order | `\supp(g_k) \subset \{x \in \mathbb R \mid \|x\| \le 1/k\}, \int_\mathbb R g_k(x) dx = 1.` |
| align | no matching glyph region in reading order | `\\|u_j - u1_K\\| \le 1/j.` |
| align | no matching glyph region in reading order | `-(u, \phi') = -\int_0^1 x \phi'(x) dx = \int_0^1 \phi(x) dx = (w, \phi).` |
| align | no matching glyph region in reading order | `w(x) = \frac{u(x_i) - u(x_{i-1})}{x_i - x_{i-1}}, x \in I_i,\ i=1,\dots,n.` |
| align | no matching glyph region in reading order | `% To the students looking at this code: % In general I recommend to avoid using manual spa` |
| align | no matching glyph region in reading order | `\phi \mapsto (u', \phi') = a(u, \phi), \phi \in C_0^\infty(I).` |
| align | no matching glyph region in reading order | `\\|(h\partial)(u-u_h)\\| \lesssim \\|(h \partial)^2 u\\|.` |
| align | no matching glyph region in reading order | `\tilde \mathcal I_h^k v\|_{I_i} = \mathcal I_{h,i}^k(v\|_{I_i}), v \in C(I),` |
| align | no matching glyph region in reading order | `a(u,v) = \int_\Omega (\nabla u \cdot \nabla v + (b \cdot \nabla u) v+ q u v)\, dx,` |

## deriving-navier-stokes.pdf

- Source: `eval/sources/ff_navierstokes/deriving-navier-stokes.tex`
- Simple source equations: **80**  ·  detected regions: **122**  ·  kept: **50**  ·  unmatched regions (prose/fragments): **72**

| id | page | kind | LaTeX | PDF glyph text |
| --- | --- | --- | --- | --- |
| ffns_p8e1 | 8 | bracket | `\nabla\phi= \left(\frac{\partial\phi}{\partial x}, \frac{\partial\phi}{\partial y}, \frac{\partial\phi}{\partial z}\right).` | `x=(x,y,z)` |
| ffns_p10e2 | 10 | bracket | `\frac{d\mathbf{X}}{dt} =\bm{u}(\mathbf{X}(\bm{\xi},t),t).` | `d∂φdXφ(X(t),t)=+·∇φdt∂tdt∂φ=+u·∇φ.∂t` |
| ffns_p10e3 | 10 | bracket | `\boxed{\frac{D\phi}{Dt} =\frac{\partial\phi}{\partial t} +\bm{u}\cdot\nabla\phi}.` | `Dφ∂φ=+u·∇φ.Dt∂t` |
| ffns_p11e4 | 11 | bracket | `\frac{d\phi}{dt} =\frac{\partial\phi}{\partial t} +\frac{dx}{dt}\frac{\partial\phi}{\partial x} +\frac{dy}{dt}\frac{\partial\phi}{\partial y} +\frac{dz}{dt}\frac{\partial\phi}{\partial z}.` | `dφ∂φdx∂φdy∂φdz∂φ=+++.dt∂tdt∂xdt∂ydt∂z` |
| ffns_p11e5 | 11 | bracket | `\boxed{ \frac{D\phi}{Dt} =\frac{\partial\phi}{\partial t} +u\frac{\partial\phi}{\partial x} +v\frac{\partial\phi}{\partial y} +w\frac{\partial\phi}{\partial z}}` | `Dφ∂φ∂φ∂φ∂φ=+u+v+wDt∂t∂x∂y∂z` |
| ffns_p12e6 | 12 | bracket | `\boxed{ \bm{a} =\frac{D\bm{u}}{Dt} =\frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} }.` | `Du∂ua==+(u·∇)u.Dt∂t` |
| ffns_p12e7 | 12 | bracket | `a_i=\frac{\partial u_i}{\partial t} +u_j\frac{\partial u_i}{\partial x_j},` | `∂u∂ua=i+ui,ij∂t∂xj` |
| ffns_p14e8 | 14 | bracket | `\frac{D\bm{u}}{Dt} =\underbrace{\frac{\partial\bm{u}}{\partial t}}_{\text{local acceleration}} +\underbrace{(\bm{u}\cdot\nabla)\bm{u}}_{\text{advective acceleration}}.` | `Du∂u=+(u·∇)u.Dt∂t\|{z}\|{z}advectiveacceleration` |
| ffns_p15e9 | 15 | bracket | `\boxed{\frac{d}{dt}\|\Omega(t)\|=0}.` | `d\|Ω(t)\|=0.dt` |
| ffns_p18e10 | 18 | bracket | `\boxed{ \frac{\partial\rho}{\partial t} +\nabla\cdot(\rho\bm{u})=0 } \Longleftrightarrow \boxed{ \frac{D\rho}{Dt}+\rho\nabla\cdot\bm{u}=0 }.` | `∂ρDρ+∇·(ρu)=0⇐⇒+ρ∇·u=0.∂tDt` |
| ffns_p18e11 | 18 | bracket | `\frac{D\rho}{Dt}=0 \Longrightarrow \boxed{\nabla\cdot\bm{u}=0}.` | `Dρ=0=⇒∇·u=0.Dt` |
| ffns_p19e12 | 19 | bracket | `\boxed{\bm{t}_p(\bm{n})=-p\bm{n}}.` | `tp(n)=-pn.` |
| ffns_p22e13 | 22 | bracket | `\boxed{\mathbf{F}_{p,\mathrm{parcel}} \approx-(\nabla p)\,\delta V}.` | `F≈-(∇p)δV.p,parcel` |
| ffns_p22e14 | 22 | bracket | `\mathbf{F}_{p,\mathrm{surroundings}} \approx+(\nabla p)\,\delta V.` | `≈∇Fp,surroundings+(p)δV.` |
| ffns_p23e15 | 23 | bracket | `\bm{t}_p=-p\bm{n}.` | `tp=-pn.` |
| ffns_p24e16 | 24 | bracket | `\boxed{\mathbf{F}_{\mathrm{total}} \approx(-\nabla p+\rho\bm g)\,\delta V}.` | `F≈(-∇p+ρg)δV.total` |
| ffns_p25e17 | 25 | bracket | `\rho\,\delta V\,\frac{D\bm{u}}{Dt} =(-\nabla p+\rho\bm g)\,\delta V.` | `DuρδV=(-∇p+ρg)δV.Dt` |
| ffns_p25e18 | 25 | bracket | `\boxed{ \rho\frac{D\bm{u}}{Dt}=-\nabla p+\rho\bm g}.` | `Duρ=-∇p+ρg.Dt` |
| ffns_p26e19 | 26 | bracket | `\boxed{ \frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} =-\frac{1}{\rho}\nabla p+\bm{b}}.` | `∂u1+(u·∇)u=-∇p+b.∂tρ` |
| ffns_p28e20 | 28 | bracket | `\bm{t}(\bm{n})\,dS,` | `t(n)dS,` |
| ffns_p30e21 | 30 | bracket | `\boxed{\bm{t}(\bm{n})=\bm{\sigma}\bm{n}}, t_i=\sigma_{ij}n_j.` | `ti=σijnj.` |
| ffns_p32e22 | 32 | bracket | `\boxed{\rho\frac{D\bm{u}}{Dt} =\nabla\cdot\bm{\sigma}+\rho\bm{b}}.` | `Duρ=∇·σ+ρb.Dt` |
| ffns_p33e23 | 33 | bracket | `t_i=\sigma_{ij}n_j, (\nabla\cdot\bm{\sigma})_i =\frac{\partial\sigma_{ij}}{\partial x_j}.` | `∂σijti=σijnj,(∇·σ)i=.∂xj` |
| ffns_p33e24 | 33 | bracket | `\boxed{ \rho\left( \frac{\partial u_i}{\partial t} +u_j\frac{\partial u_i}{\partial x_j} \right) =\frac{\partial\sigma_{ij}}{\partial x_j} +\rho b_i}.` | `∂ui∂ui∂σijρ+uj=+ρbi.∂t∂x∂xjj` |
| ffns_p34e25 | 34 | bracket | `\rho\frac{D\bm{u}}{Dt} =-\nabla p+\nabla\cdot\bm{\tau}+\rho\bm{b}.` | `Du-∇∇·ρ=p+τ+ρb.Dt` |
| ffns_p35e26 | 35 | bracket | `\operatorname{tr}\mathbf{D}=\nabla\cdot\bm{u}.` | `trD=∇·u.` |
| ffns_p36e27 | 36 | bracket | `d\bm{u}=(\nabla\bm{u})\,d\bm{x} =\mathbf{D}\,d\bm{x}+\mathbf{W}\,d\bm{x}.` | `du=(∇u)dx=Ddx+Wdx.` |
| ffns_p37e28 | 37 | bracket | `\bm{\tau}=2\mu\mathbf{D} +\lambda(\nabla\cdot\bm{u})\mathbf{I}.` | `τ=2μD+λ(∇·u)I.` |
| ffns_p38e29 | 38 | bracket | `\boxed{ \bm{\tau} =2\mu\mathbf{D} +\lambda(\nabla\cdot\bm{u})\mathbf{I} }.` | `τ=2μD+λ(∇·u)I.` |
| ffns_p39e30 | 39 | bracket | `\boxed{\bm{\tau}=2\mu\mathbf{D}}, \boxed{\bm{\sigma}=-p\mathbf{I}+2\mu\mathbf{D}}.` | `τ=2μD,σ=-pI+2μD.` |
| ffns_p39e31 | 39 | bracket | `\sigma_{ij} =-p\delta_{ij} +\mu\left( \frac{\partial u_i}{\partial x_j} +\frac{\partial u_j}{\partial x_i} \right).` | `∂ui∂ujσ=-pδ+μ+.ijij∂x∂xji` |
| ffns_p40e32 | 40 | bracket | `\nabla\cdot(2\mu\mathbf{D}) =\mu\nabla^2\bm{u} +\mu\nabla(\nabla\cdot\bm{u}).` | `2∇·(2μD)=μ∇u+μ∇(∇·u).` |
| ffns_p41e33 | 41 | bracket | `\boxed{ \rho\left[ \frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} \right] =-\nabla p+\mu\nabla^2\bm{u}+\rho\bm{b} }` | `∂uρ+(u·∇)u=-∇p+μ∇2u+ρb∂t` |
| ffns_p41e34 | 41 | bracket | `\frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} =-\frac{1}{\rho}\nabla p +\nu\nabla^2\bm{u}+\bm{b}.` | `∂u12+(u·∇)u=-∇p+ν∇u+b.∂tρ` |
| ffns_p44e35 | 44 | bracket | `\boxed{ \rho\left( \frac{\partial u_i}{\partial t} +u_j\frac{\partial u_i}{\partial x_j} \right) =-\frac{\partial p}{\partial x_i} +\mu\frac{\partial^2u_i}{\partial x_j\partial x_j} +\rho b_i }, i=1,2,3,` | `∂ui∂ui∂p∂2uiρ+u=-+μ+ρb,i=1,2,3,ji∂t∂xj∂xi∂xj∂xj` |
| ffns_p44e36 | 44 | bracket | `\boxed{\frac{\partial u_i}{\partial x_i}=0}.` | `∂ui=0.∂xi` |
| ffns_p45e37 | 45 | bracket | `\boxed{ \rho(\bm{u}\cdot\nabla)\bm{u} =-\nabla p+\mu\nabla^2\bm{u}+\rho\bm{b}}, \boxed{\nabla\cdot\bm{u}=0}.` | `ρ(u·∇)u=-∇p+μ∇2u+ρb,∇·u=0.` |
| ffns_p46e38 | 46 | bracket | `\bm{u}=(u(y,t),0,0), \frac{\partial u}{\partial x} =\frac{\partial u}{\partial z}=0.` | `∂u∂uu=(u(y,t),0,0),==0.∂x∂z` |
| ffns_p46e39 | 46 | bracket | `\boxed{ \rho\frac{\partial u}{\partial t} =-\frac{\partial p}{\partial x} +\mu\frac{\partial^2u}{\partial y^2} +\rho b_x }.` | `∂u∂p∂2uρ=-+μ+ρb.2x∂t∂x∂y` |
| ffns_p47e40 | 47 | bracket | `\rho(u_t+u u_x+v u_y) =-p_x+\mu(u_{xx}+u_{yy})+\rho b_x,` | `ρ(u+uu+vu)=-p+μ(u+u)+ρb,txyxxxyyx` |
| ffns_p47e41 | 47 | bracket | `\rho(v_t+u v_x+v v_y) =-p_y+\mu(v_{xx}+v_{yy})+\rho b_y,` | `ρ(v+uv+vv)=-p+μ(v+v)+ρb,txyyxxyyy` |
| ffns_p47e42 | 47 | bracket | `\boxed{u_x+v_y=0}.` | `ux+vy=0.` |
| ffns_p49e43 | 49 | bracket | `\bm{u}(\bm{x},0)=\bm{u}_0(\bm{x}), \nabla\cdot\bm{u}_0=0,` | `u(x,0)=u(x),∇·u=0,00` |
| ffns_p49e44 | 49 | bracket | `\bm{u}=\overline{\bm{u}} \ \text{on }\Gamma_D, \bm{\sigma}\bm{n}=\overline{\bm{t}} \ \text{on }\Gamma_N.` | `u=uonΓD,σn=tonΓN.` |
| ffns_p50e45 | 50 | bracket | `(\bm{u}-\mathbf{U}_{\mathrm{wall}})\cdot\bm{n}=0.` | `(u-U)·n=0.wall` |
| ffns_p51e46 | 51 | bracket | `\bm{\sigma}\bm{n}=-p_{\mathrm{ext}}\bm{n};` | `σn=-pextn;` |
| ffns_p52e47 | 52 | bracket | `(\bm{\sigma}\bm{n})_{\parallel} +\frac{\mu}{\ell_s} (\bm{u}-\mathbf U_{\mathrm{wall}})_{\parallel}=0.` | `(u-Uwall)·n=0,μ-(σn)∥+(uUwall)∥=0.ℓs` |
| ffns_p53e48 | 53 | bracket | `(\bm{u}-\mathbf{U}_{\mathrm{wall}})\cdot\bm{n}=0,` | `(u-Uwall)·n=0,` |
| ffns_p56e49 | 56 | bracket | `\boxed{ \nabla^2p =-\rho\,\nabla\cdot\left[(\bm{u}\cdot\nabla)\bm{u}\right] +\rho\,\nabla\cdot\bm{b} }.` | `2∇p=-ρ∇·[(u·∇)u]+ρ∇·b.` |
| ffns_p63e50 | 63 | bracket | `\nabla\cdot(2\mu\mathbf{D}) =\mu\nabla^2\bm{u} +\mu\nabla(\nabla\cdot\bm{u}).` | `∇·(2μD)=μ∇2u+μ∇(∇·u).` |

### Skipped (53)

| kind | reason | LaTeX |
| --- | --- | --- |
| bracket | multi-line / aligned | `\begin{aligned} &\rho\left( \frac{\partial\bm{u}}{\partial t} +(\bm{u}\!\cdot\!\nabla)\bm{` |
| bracket | signature too small to verify safely | `\nabla\!\cdot\bm{u}=0` |
| align | multi-line (2 rows) | `\frac{d}{dt}\phi(\mathbf{X}(t),t) =\frac{\partial\phi}{\partial t} +\frac{d\mathbf{X}}{dt}` |
| align | multi-line (3 rows) | `\frac{Du}{Dt} =\frac{\partial u}{\partial t} +u\frac{\partial u}{\partial x} +v\frac{\part` |
| bracket | multi-line / aligned | `4pt] \frac{Dv}{Dt} &=\frac{\partial v}{\partial t} +u\frac{\partial v}{\partial x} +v\frac` |
| bracket | signature too small to verify safely | `\boxed{\nabla\cdot\bm{u}=0}.` |
| bracket | signature too small to verify safely | `\boxed{\nabla\cdot\bm{u}=0}.` |
| align | multi-line (3 rows) | `\frac{\partial u}{\partial t} +u\frac{\partial u}{\partial x} +v\frac{\partial u}{\partial` |
| bracket | multi-line / aligned | `3pt] \frac{\partial v}{\partial t} +u\frac{\partial v}{\partial x} +v\frac{\partial v}{\pa` |
| bracket | multi-line / aligned | `\bm{\sigma}= \begin{pmatrix} \sigma_{xx}&\sigma_{xy}&\sigma_{xz}\\ \sigma_{yx}&\sigma_{yy}` |
| bracket | signature too small to verify safely | `\nabla\cdot\bm{\sigma}=-\nabla p` |
| bracket | signature too small to verify safely | `\boxed{\bm{\sigma}=-p\mathbf{I}+\bm{\tau}},` |
| bracket | signature too small to verify safely | `\bm{\sigma}=\bm{\sigma}^{\mathsf T}.` |
| bracket | signature too small to verify safely | `\zeta=\lambda+\frac{2}{3}\mu.` |
| bracket | signature too small to verify safely | `\boxed{\nabla\cdot\bm{\tau}=\mu\nabla^2\bm{u}}.` |
| bracket | signature too small to verify safely | `\boxed{\nabla\cdot\bm{u}=0}.` |
| align | multi-line (3 rows) | `\rho\left(u_t+u u_x+v u_y+w u_z\right) =-p_x+\mu(u_{xx}+u_{yy}+u_{zz})+\rho b_x,` |
| bracket | multi-line / aligned | `4pt] \rho\left(v_t+u v_x+v v_y+w v_z\right) &=-p_y+\mu(v_{xx}+v_{yy}+v_{zz})+\rho b_y,\\[4` |
| bracket | signature too small to verify safely | `\partial\Omega=\Gamma_D\cup\Gamma_N, \Gamma_D\cap\Gamma_N=\varnothing,` |
| bracket | signature too small to verify safely | `\bm{\sigma}\bm{n}=\overline{\bm{t}}.` |
| align | multi-line (4 rows) | `\nabla\phi =\left( \frac{\partial\phi}{\partial x}, \frac{\partial\phi}{\partial y}, \frac` |
| bracket | multi-line / aligned | `5pt] \nabla\cdot\bm{u} &=\frac{\partial u}{\partial x} +\frac{\partial v}{\partial y} +\fr` |
| bracket | signature too small to verify safely | `\nabla\cdot\bm{\tau} =\mu\nabla^2\bm{u} +(\lambda+\mu)\nabla(\nabla\cdot\bm{u}).` |
| bracket | no matching glyph region in reading order | `\bm{x}=(x_1,x_2,x_3)=(x,y,z),` |
| bracket | no matching glyph region in reading order | `\bm{u}=(u_1,u_2,u_3)=(u,v,w).` |
| bracket | no matching glyph region in reading order | `\nabla\cdot\bm{u}= \frac{\partial u}{\partial x} +\frac{\partial v}{\partial y} +\frac{\pa` |
| bracket | no matching glyph region in reading order | `\nabla\times\bm{u}= \left( \frac{\partial w}{\partial y}-\frac{\partial v}{\partial z}, \f` |
| bracket | no matching glyph region in reading order | `\nabla^2\bm{u}=(\nabla^2u,\nabla^2v,\nabla^2w).` |
| bracket | no matching glyph region in reading order | `\frac{d}{dt}\|\Omega(t)\| =\oint_{\partial\Omega(t)}\bm{u}\cdot\bm{n}\,dS.` |
| bracket | no matching glyph region in reading order | `\oint_{\partial\Omega(t)}\bm{u}\cdot\bm{n}\,dS =\int_{\Omega(t)}\nabla\cdot\bm{u}\,dV.` |
| bracket | no matching glyph region in reading order | `M(t)=\int_{\Omega(t)}\rho(\bm{x},t)\,dV.` |
| bracket | no matching glyph region in reading order | `\frac{d}{dt}\int_{\Omega(t)}\rho\,dV=0.` |
| bracket | no matching glyph region in reading order | `\frac{d}{dt}\int_{\Omega(t)}\rho\,dV =\int_{\Omega(t)} \left[ \frac{\partial\rho}{\partial` |
| bracket | no matching glyph region in reading order | `\frac{d}{dt}\|\Omega(t)\| =\oint_{\partial\Omega(t)}\bm{u}\cdot\bm{n}\,dS =\int_{\Omega(t)}\` |
| bracket | no matching glyph region in reading order | `\boxed{ \mathbf{F}_p=-\oint_{\partial\Omega(t)}p\bm{n}\,dS}.` |
| bracket | no matching glyph region in reading order | `\oint_{\partial\Omega}(p\bm e_i)\cdot\bm{n}\,dS =\int_\Omega\nabla\cdot(p\bm e_i)\,dV =\in` |
| bracket | no matching glyph region in reading order | `\oint_{\partial\Omega}p\bm{n}\,dS =\int_\Omega\nabla p\,dV.` |
| bracket | no matching glyph region in reading order | `\boxed{\mathbf{F}_p=-\int_\Omega\nabla p\,dV}.` |
| bracket | no matching glyph region in reading order | `\mathbf{F}_p =-\oint_{\partial\Omega}p\bm{n}\,dS =-\int_{\delta V}\nabla p\,dV \approx-(\n` |
| bracket | no matching glyph region in reading order | `\mathbf{F}_g =\int_{\delta V}\rho\bm g\,dV \approx\rho\bm g\,\delta V.` |
| bracket | no matching glyph region in reading order | `\sigma_{ij} =\text{the $i$th component of force per unit area on a plane whose normal is $` |
| bracket | no matching glyph region in reading order | `\frac{d}{dt}\int_{\Omega(t)}\rho\bm{u}\,dV =\underbrace{\oint_{\partial\Omega(t)}\bm{\sigm` |
| bracket | no matching glyph region in reading order | `\oint_{\partial\Omega(t)}\bm{\sigma}\bm{n}\,dS =\int_{\Omega(t)}\nabla\cdot\bm{\sigma}\,dV` |
| bracket | no matching glyph region in reading order | `\frac{d}{dt}\int_{\Omega(t)}\rho\bm{u}\,dV =\int_{\Omega(t)}\rho\frac{D\bm{u}}{Dt}\,dV,` |
| bracket | no matching glyph region in reading order | `\int_{\Omega(t)}\rho\frac{D\bm{u}}{Dt}\,dV =\int_{\Omega(t)}(\nabla\cdot\bm{\sigma}+\rho\b` |
| bracket | no matching glyph region in reading order | `\nabla\bm{u}=\mathbf{D}+\mathbf{W},` |
| bracket | no matching glyph region in reading order | `\mathbf{D}=\frac12\left(\nabla\bm{u}+(\nabla\bm{u})^{\mathsf T}\right), \mathbf{W}=\frac12` |
| bracket | no matching glyph region in reading order | `\int_{\partial\Omega}\overline{\bm{u}}\cdot\bm{n}\,dS=0.` |
| bracket | no matching glyph region in reading order | `\bm{u}=\mathbf{U}_{\mathrm{wall}}.` |
| bracket | no matching glyph region in reading order | `\bm{u}=\bm{u}_{\mathrm{in}}(\bm{x},t).` |
| bracket | no matching glyph region in reading order | `(\bm{u}-\mathbf U_{\mathrm{wall}})\cdot\bm{n}=0,` |
| bracket | no matching glyph region in reading order | `(\bm{\sigma}\bm{n})_{\parallel} +\frac{\mu}{\ell_s} (\bm{u}-\mathbf{U}_{\mathrm{wall}})_{\` |
| bracket | no matching glyph region in reading order | `\int_\Omega p\,dV=0 \text{or} p(\bm{x}_0)=0.` |
