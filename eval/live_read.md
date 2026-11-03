# Real Muse Spark reading (Channel A) vs Channel B

- Equations: 152
- agrees (A matched B): 114
- Muse Spark errors (A wrong, B reproduces gold): 4
- Channel B gaps (B cannot reproduce gold): 34

## Muse Spark errors

| Equation | Page | What A read | What the PDF says |
| --- | ---: | --- | --- |
| `uh_p9e36` | 10 | `||u1_K - u|| \le 1/j.` | `∥u1K-u∥≤1/j.` |
| `uh_p18e85` | 19 | `||(h\partial)(u-u_h)||\underset{\sim}{\lesssim}||(h\partial)^{l+1}u||,` | `∥(h∂)(u-u)∥≲∥(h∂)l+1u∥,h` |
| `uh_p18e86` | 19 | `|| u - u_h || \lesssim || (h\partial)^{l+1} u ||.` | `l+1∥u-uh∥≲∥(h∂)u∥.` |
| `ffns_p45e37` | 46 | `\rho(\boldsymbol{u} \cdot \nabla)\boldsymbol{u} = -\nabla p + \mu \nabla^2 \boldsymbol{u} + \rho \boldsymbol{b}` | `ρ(u·∇)u=-∇p+μ∇2u+ρb,∇·u=0.` |

Full explanations:

- **uh_p9e36**: Could not be verified: The PDF has '∥', but the reading has '|', '|'.
- **uh_p18e85**: Could not be verified: The PDF has '∥', but the reading has '|', '|'.
- **uh_p18e86**: Could not be verified: The PDF has '∥', but the reading has '|', '|'.
- **ffns_p45e37**: Could not be verified: The PDF has ',', '∇', '·', 'u', '=', '0', '.', but the reading leaves it out.

## All readings

| Equation | Kind | Read | Gold |
| --- | --- | --- | --- |
| `p1e1` | agrees | `\frac{p}{\rho g} + \frac{v^2}{2g} + z = H` | `\frac{p}{\rho g} + \frac{v^2}{2g} + z = H` |
| `p1e2` | agrees | `p = p_0 + \rho g h` | `p = p_0 + \rho g h` |
| `p1e3` | agrees | `A_1 v_1 = A_2 v_2` | `A_1 v_1 = A_2 v_2` |
| `p1e4` | agrees | `h_f = f \frac{L}{D} \frac{v^2}{2g}` | `h_f = f \frac{L}{D} \frac{v^2}{2g}` |
| `p1e5` | agrees | `Re = \frac{\rho v D}{\mu}` | `Re = \frac{\rho v D}{\mu}` |
| `p1e6` | agrees | `F_x = -\dot{m}(v_2 - v_1)` | `F_x = -\dot{m}(v_2 - v_1)` |
| `uh_p1e1` | agrees | `+ : F(I) \times F(I) \to F(I), \cdot : \mathbb{R} \times F(I) \to F(I),` | `+ : F(I) \times F(I) \to F(I), \cdot : \mathbb R \times F(I) \to F(I),` |
| `uh_p1e2` | agrees | `(u + v)(x) = u(x) + v(x), (cu)(x) = cu(x), x \in I.` | `(u + v)(x) = u(x) + v(x), (cu)(x) = cu(x), x \in I.` |
| `uh_p1e3` | agrees | `C(I) = \{u \in F(I) | u \text{ is continuous on } I\}.` | `C(I) = \{ u \in F(I) \mid \text{$u$ is continuous on $I$}\}.` |
| `uh_p2e4` | agrees | `C^k(I) = \{u \in C(I) | u', \dots, u^{(k)} \in C(I)\}, \quad k = 1, 2, \dots.` | `C^k(I) = \{ u \in C(I) \mid u', \dots, u^{(k)} \in C(I)\}, k = 1,2,\dots.` |
| `uh_p2e5` | agrees | `L^p(I) = \{u \in F(I) \mid \int_I |u(x)|^p dx < \infty\}, p \ge 1.` | `L^p(I) = \{u \in F(I) \mid \int_I |u(x)|^p dx < \infty \}, p \ge 1.` |
| `uh_p2e6` | b_gap | `\|u\|_{L^p(I)} = \left(\int_I |u(x)|^p dx\right)^{\frac{1}{p}}.` | `\|u\|_{L^p(I)} = \left( \int_I |u(x)|^p dx \right)^{\frac1p}.` |
| `uh_p2e7` | agrees | `(u, v) = \int_I u(x)v(x)dx, \quad (\cdot, \cdot) : L^2(I) \times L^2(I) \to \mathbb{R}.` | `(u, v) = \int_I u(x) v(x) dx, (\cdot, \cdot) : L^2(I) \times L^2(I) \to \mathbb R.` |
| `uh_p2e8` | agrees | `1, x, x^2, \dots, x^n` | `1, x, x^2, \dots, x^n` |
| `uh_p2e9` | agrees | `\mathbb{P}_n \subset C^k (I)` | `\mathbb P_n \subset C^k(I)` |
| `uh_p2e10` | agrees | `C^k(I) \subset L^2(I) \subset F(I).` | `C^k(I) \subset L^2(I) \subset F(I).` |
| `uh_p2e11` | agrees | `(u, v) \le \|u\|\|v\| \quad u, v \in V.` | `(u, v) \le \|u\| \|v\| u,v \in V.` |
| `uh_p3e12` | agrees | `(u - s, v) = 0 \text{ for all } v \in S.` | `(u - s, v) = 0 \text{for all $v \in S$}.` |
| `uh_p3e13` | agrees | `I = [0,1]` | `I = [0,1]` |
| `uh_p3e14` | agrees | `\mathcal{V} = \{v \in C^1(I) : v(0) = v(1) = 0\},` | `\mathcal V = \{ v \in C^1(I) : v(0) = v(1) = 0 \},` |
| `uh_p3e15` | agrees | `(u', v') = (f, v) \quad \text{for all } v \in \mathcal{V}.` | `(u', v') = (f, v) \text{for all $v \in \mathcal V$}.` |
| `uh_p3e16` | agrees | `a(u,v) = (u', v'), \quad a : \mathcal{V} \times \mathcal{V} \to \mathbb{R},` | `a(u, v) = (u', v'), a : \mathcal V \times \mathcal V \to \mathbb R,` |
| `uh_p3e17` | agrees | `L(v) = (f, v), L : \mathcal{V} \to \mathbb{R}.` | `L(v) = (f,v), L : \mathcal V \to \mathbb R.` |
| `uh_p4e18` | agrees | `a(u_S, v) = L(v) \text{ for all } v \in S.` | `a(u_S,v) = L(v) \text{for all $v \in S$}.` |
| `uh_p4e19` | agrees | `a(u_S, v) = L(v) \text{ for all } v \in S.` | `a(u_S,v) = L(v) \text{for all $v \in S$}.` |
| `uh_p4e20` | agrees | `a(u, v) = L(v) \text{ for all } v \in V.` | `a(u, v) = L(v) \text{for all $v \in V$}.` |
| `uh_p4e21` | agrees | `a(u - u_S, v) = 0 \text{ for all } v \in S.` | `a(u-u_S,v) = 0 \text{for all $v \in S$}.` |
| `uh_p4e22` | agrees | `a(u - u_S, v) = a(u, v) - a(u_S, v) = L(v) - L(v) = 0.` | `a(u-u_S,v) = a(u, v) - a(u_S, v) = L(v) - L(v) = 0.` |
| `uh_p5e23` | agrees | `0 = x_0 < x_1 < \cdots < x_n = 1,` | `0 = x_0 < x_1 < \dots < x_n = 1,` |
| `uh_p5e24` | agrees | `\mathcal{I}_h u(x_i) = u(x_i), i = 0, \ldots, n.` | `\mathcal I_h u(x_i) = u(x_i), i=0,\dots,n.` |
| `uh_p5e25` | b_gap | `\|u - \mathcal{I}_h u\|_{L^\infty(I)} \lesssim \|(h\partial)^2 u\|_{L^\infty(I)}.` | `\|u - \mathcal I_h u\|_{L^\infty(I)} \lesssim \|(h \partial)^2 u\|_{L^\infty(I)}.` |
| `uh_p6e26` | agrees | `c_1\phi_1 + \cdots + c_{n-1}\phi_{n-1} = 0` | `c_1 \phi_1 + \dots + c_{n-1} \phi_{n-1} = 0` |
| `uh_p6e27` | agrees | `a(u,v) = (u',v'), a : V \times V \to \mathbb{R},` | `a(u, v) = (u', v'), a : V \times V \to \mathbb R,` |
| `uh_p6e28` | agrees | `a(u, v) = L(v) \quad \text{for all } v \in V,` | `a(u, v) = L(v) \text{for all $v \in V$},` |
| `uh_p7e29` | agrees | `(u, v) = \int_I u(x)v(x)dx.` | `(u,v) = \int_I u(x)v(x)dx.` |
| `uh_p7e30` | b_gap | `\|u - v\|_X < \delta \implies \|Au - Av\|_Y < \epsilon.` | `\|u-v\|_X < \delta \implies \|Au-Av\|_Y < \epsilon.` |
| `uh_p7e31` | agrees | `\|Au - Av\|_Y = \|A(u - v)\|_Y \le C\|u - v\|_X < C\delta = \epsilon.` | `\|Au-Av\|_Y = \|A(u-v)\|_Y \le C \|u-v\|_X < C \delta = \epsilon.` |
| `uh_p8e32` | agrees | `\|Au\|_Y \le C\|u\|_X` | `\|Au\|_Y \le C \|u\|_X` |
| `uh_p8e33` | agrees | `\|Au\|_Y \le p(u),` | `\|Au\|_Y \le p(u),` |
| `uh_p8e34` | agrees | `\{x \in I \mid u(x) \neq 0\}.` | `\{x \in I \mid u(x) \ne 0\}.` |
| `uh_p9e35` | agrees | `K = [x_L + \delta, x_R - \delta].` | `K = [x_L + \delta, x_R - \delta].` |
| `uh_p9e36` | muse_error | `||u1_K - u|| \le 1/j.` | `\|u1_K - u\| \le 1/j.` |
| `uh_p9e37` | agrees | `\|u_j - u\| \le \|u_j - u1_K\| + \|u1_K - u\| \le 2/j \to 0, \quad j \to \infty.` | `\|u_j - u\| \le \|u_j - u1_K\| + \|u1_K - u\| \le 2/j \to 0, j \to \infty.` |
| `uh_p9e38` | agrees | `L_u(\phi) = L_v(\phi), \quad \text{for all } \phi \in C_0^\infty(I).` | `L_u(\phi) = L_v(\phi), \text{for all $\phi \in C_0^\infty(I)$}.` |
| `uh_p10e39` | agrees | `A(w) = (u - v, w), \quad A : L^2(I) \to \mathbb{R},` | `A(w) = (u - v, w), A : L^2(I) \to \mathbb R,` |
| `uh_p10e40` | agrees | `L(\phi) = (-1)^k (f, \phi^{(k)}), \phi \in C_0^\infty (I).` | `L(\phi) = (-1)^k (f, \phi^{(k)}), \phi \in C_0^\infty(I).` |
| `uh_p11e41` | agrees | `(-1)^2(u, \phi'') = (-1)^2(u, (\phi')') = (-1)(w, \phi').` | `(-1)^2 (u, \phi'') = (-1)^2 (u, (\phi')') = (-1) (w, \phi').` |
| `uh_p11e42` | agrees | `L : C_0^\infty (I) \to \mathbb{R},` | `L : C_0^\infty(I) \to \mathbb R,` |
| `uh_p11e43` | agrees | `H^k(I) = \{u \in L^2(I) | u', \ldots, u^{(k)} \in L^2(I)\}.` | `H^k(I) = \{ u \in L^2(I) \mid u', \dots, u^{(k)} \in L^2(I)\}.` |
| `uh_p11e44` | b_gap | `(u, v)_{H^1(I)} = (u, v) + (u', v').` | `(u,v)_{H^1(I)} = (u,v) + (u', v').` |
| `uh_p12e45` | b_gap | `\|Eu\|_{L^2(\mathbb{R})} \lesssim \|u\|_{L^2(I)}, \quad \|Eu\|_{H^1(\mathbb{R})} \lesssim \|u\|_{H^1(I)}.` | `\|E u\|_{L^2(\mathbb R)} \lesssim \|u\|_{L^2(I)}, \|E u\|_{H^1(\mathbb R)} \lesssim \|u\|_{H^1(I)}.` |
| `uh_p12e46` | b_gap | `\|u\|_{L^\infty(I)} \lesssim \|u\|_{H^1(I)}.` | `\|u\|_{L^\infty(I)} \lesssim \|u\|_{H^1(I)}.` |
| `uh_p12e47` | agrees | `H_0^1(I) = \{u \in H^1(I) \mid u(x_L) = 0 = u(x_R)\}.` | `H_0^1(I) = \{u \in H^1(I) \mid u(x_L) = 0 = u(x_R) \}.` |
| `uh_p12e48` | b_gap | `\|u\|_{H^1(I)} \lesssim \|u'\|_{L^2(I)}, u \in H_0^1(I).` | `\|u\|_{H^1(I)} \lesssim \|u'\|_{L^2(I)}, u \in H_0^1(I).` |
| `uh_p12e49` | agrees | `I = [0, 1], V = H_0^1(I),` | `I = [0,1], V = H_0^1(I),` |
| `uh_p12e50` | agrees | `a(u,v) = (u',v'),\quad a : V \times V \to \mathbb{R}.` | `a(u, v) = (u', v'), a : V \times V \to \mathbb R.` |
| `uh_p12e51` | agrees | `L(v) = (f, v),\quad L : V \to \mathbb{R}.` | `L(v) = (f, v), L : V \to \mathbb R.` |
| `uh_p13e52` | agrees | `a(u, v) = L(v) \text{ for all } v \in V,` | `a(u, v) = L(v) \text{for all $v \in V$},` |
| `uh_p13e53` | agrees | `Av = a(u, v) - L(v), \quad A : V \to \mathbb{R},` | `Av = a(u,v) - L(v), A : V \to \mathbb R,` |
| `uh_p13e54` | b_gap | `\|(h\partial)(u - u_h)\| \lesssim \|(h\partial)^2 u\|_{L^\infty(I)}.` | `\|(h\partial)(u-u_h)\| \lesssim \|(h \partial)^2 u\|_{L^\infty(I)}.` |
| `uh_p13e55` | agrees | `\|w\|_E^2 = a(w, w) = \|w'\|^2, \quad w \in V,` | `\|w\|_E^2 = a(w,w) = \|w'\|^2, w \in V,` |
| `uh_p14e56` | agrees | `\mathcal{I}_h : H^1(I) \to S.` | `\mathcal I_h : H^1(I) \to S.` |
| `uh_p14e57` | b_gap | `\|\mathcal{I}_h u\|_{H^1(I)} \lesssim \|u\|_{H^1(I)}, \quad u \in H^1(I).` | `\|\mathcal I_h u\|_{H^1(I)} \lesssim \|u\|_{H^1(I)}, u \in H^1(I).` |
| `uh_p14e58` | b_gap | `\|\mathcal{I}_h u\|_{H^1(I)} \lesssim \|u\|_{H^1(I)}, \quad u \in C^\infty(I).` | `\|\mathcal I_h u\|_{H^1(I)} \lesssim \|u\|_{H^1(I)}, u \in C^\infty(I).` |
| `uh_p14e59` | b_gap | `\| \mathcal{I}_{h} u \| \lesssim \| \mathcal{I}_{h} u \|_{L^{\infty}(I)} \le \| u \|_{L^{\infty}(I)} \lesssim \| u \|_{H^{1}(I)}, \quad u \in H^{1}(I),` | `\|\mathcal I_h u\| \lesssim \|\mathcal I_h u\|_{L^\infty(I)} \le \|u\|_{L^\infty(I)} \lesssim \|u\|_{H^1(I)}, u \in H^1(I),` |
| `uh_p14e60` | b_gap | `||\partial \mathcal{I}_h u|| \lesssim ||u||_{H^1(I)}, \quad u \in C^\infty(I).` | `\|\partial \mathcal I_h u\| \lesssim \|u\|_{H^1(I)}, u \in C^\infty(I).` |
| `uh_p14e61` | b_gap | `\partial \mathcal{I}_h u|_{I_i} = \frac{u(x_i) - u(x_{i-1})}{x_i - x_{i-1}}.` | `\partial \mathcal I_h u|_{I_i} = \frac{u(x_i) - u(x_{i-1})}{x_i - x_{i-1}}.` |
| `uh_p14e62` | b_gap | `u(x_i) - u(x_{i-1}) = \int_{I_i} u'(x)dx \le |x_i - x_{i-1}|^{\frac{1}{2}} \|u'\|_{L^2(I_i)}.` | `u(x_i) - u(x_{i-1}) = \int_{I_i} u'(x) dx \le |x_i - x_{i-1}|^{\frac12} \|u'\|_{L^2(I_i)}.` |
| `uh_p15e63` | agrees | `\mathcal{I}_h u = \sum_{i=0}^n u(x_i)\phi_i,` | `\mathcal I_h u = \sum_{i=0}^n u(x_i) \phi_i,` |
| `uh_p15e64` | b_gap | `\|\mathcal{I}_h u\|_{H^1(I)} \le \|u\|_{L^\infty(I)} \sum_{i=0}^n \|\phi_i\|_{H^1(I)} \le C_h\|u\|_{H^1(I)},` | `\|\mathcal I_h u\|_{H^1(I)} \le \|u\|_{L^\infty(I)} \sum_{i=0}^n \|\phi_i\|_{H^1(I)} \le C_h \|u\|_{H^1(I)},` |
| `uh_p15e65` | agrees | `\|u - \mathcal{I}_h u\| + \|(h\partial)(u - \mathcal{I}_h u)\| \lesssim \|(h\partial)^2 u\|,\quad u \in H^2(I).` | `\|u - \mathcal I_h u\| + \|(h\partial)(u - \mathcal I_h u)\| \lesssim \|(h\partial)^2 u\|, u \in H^2(I).` |
| `uh_p15e66` | b_gap | `w(x) = \int_{\xi}^{x} w'(y)dy \le |x - \xi|^{\frac{1}{2}} \|w'\|_{L^2(I_i)},` | `w(x) = \int_\xi^x w'(y) dy \le |x - \xi|^{\frac12} \|w'\|_{L^2(I_i)},` |
| `uh_p15e67` | b_gap | `|^2_{L^2(I_i)} \le \int_{I_i} |x - \xi|dx \|w'\|^2_{L^2(I_i)} \le h^2\|w'\|^2_{L^2(I_i)} = \|(h\partial)w\|^2_{L^2(I_i)}.` | `\|w\|_{L^2(I_i)}^2 \le \int_{I_i} |x - \xi| dx\, \|w'\|_{L^2(I_i)}^2 \le h^2 \|w'\|_{L^2(I_i)}^2 = \|(h\partial) w\|_{L^2(I_i)}^2.` |
| `uh_p15e68` | b_gap | `|^2_{L^2(I_i)} \le \|(h\partial)^2(u - \mathcal{I}_h u)\|^2_{L^2(I_i)} = \|(h\partial)^2 u\|^2_{L^2(I_i)},` | `\|(h\partial)(u - \mathcal I_h u)\|_{L^2(I_i)}^2 \le \|(h\partial)^2 (u - \mathcal I_h u)\|_{L^2(I_i)}^2 = \|(h\partial)^2 u\|_{L^2(I_i)}^2,` |
| `uh_p15e69` | b_gap | `\|(u - \mathcal{I}_h u)\|_{L^2(I_i)}^2 \le \|(h\partial)(u - \mathcal{I}_h u)\|_{L^2(I_i)}^2 \le \|(h\partial)^2 u\|_{L^2(I_i)}^2.` | `\|(u - \mathcal I_h u)\|_{L^2(I_i)}^2 \le \|(h\partial)(u - \mathcal I_h u)\|_{L^2(I_i)}^2 \le \|(h\partial)^2 u\|_{L^2(I_i)}^2.` |
| `uh_p16e70` | agrees | `L : H \to \mathbb{R}` | `L : H \to \mathbb R` |
| `uh_p16e71` | agrees | `L(v) = (u, v), \quad v \in H.` | `L(v) = (u,v), v \in H.` |
| `uh_p16e72` | agrees | `\|u - u_h\| \lesssim \|(h\partial)^2 u\|.` | `\|u-u_h\| \lesssim \|(h \partial)^2 u\|.` |
| `uh_p16e73` | agrees | `\|u - u_h\|^2 = L(u - u_h) = a(w, u - u_h).` | `\|u-u_h\|^2 = L(u - u_h) = a(w, u - u_h).` |
| `uh_p17e74` | agrees | `a(\mathcal{I}_h w, u - u_h) = 0.` | `a(\mathcal I_h w, u - u_h) = 0.` |
| `uh_p17e75` | agrees | `\|u - u_h\|^2 = a(w - \mathcal{I}_h w, u - u_h) \le \|\partial(w - \mathcal{I}_h)\|\|\partial(u - u_h)\|.` | `\|u-u_h\|^2 = a(w - \mathcal I_h w, u - u_h) \le \|\partial(w - \mathcal I_h)\|\|\partial(u-u_h)\|.` |
| `uh_p17e76` | agrees | `\|w''\| = \|u - u_h\|.` | `\|w''\| = \|u - u_h\|.` |
| `uh_p17e77` | agrees | `\|(h\partial)(w - \mathcal{I}_h)\| \lesssim \|(h\partial)^2 w\|.` | `\|(h\partial)(w - \mathcal I_h)\| \lesssim \|(h\partial)^2 w\|.` |
| `uh_p17e78` | agrees | `\|u - u_h\| \le \|(h\partial)(u - u_h)\| \lesssim \|(h\partial)^2 u\|.` | `\|u-u_h\| \le \|(h\partial)(u-u_h)\| \lesssim \|(h \partial)^2 u\|.` |
| `uh_p17e79` | agrees | `a(u_h, v) = L(v) \quad \text{for all } v \in P_{h,0}^k.` | `a(u_h,v) = L(v) \text{for all $v \in P_{h,0}^k$}.` |
| `uh_p17e80` | agrees | `\xi_m = x_{i-1} + \frac{m}{k}(x_i - x_{i-1}) \in I_i, \quad m = 0, \dots, k.` | `\xi_m = x_{i-1} + \frac m k (x_i - x_{i-1}) \in I_i, m = 0,\dots,k.` |
| `uh_p17e81` | b_gap | `\mathcal{L}_m(x) = \prod_{l=0,l\neq m}^{k} \frac{x - \xi_l}{\xi_m - \xi_l}.` | `\mathcal L_m(x) = \prod_{l=0,l \ne m}^k \frac{x - \xi_l}{\xi_m - \xi_l}.` |
| `uh_p18e82` | b_gap | `\mathcal{I}_{h,i}^k u(x) = \sum_{m=0}^k u(\xi_m) \mathcal{L}_m(x), \quad u \in C(I_i).` | `\mathcal I^k_{h,i} u(x) = \sum_{m=0}^k u(\xi_m) \mathcal L_m(x), u \in C(I_i).` |
| `uh_p18e83` | b_gap | `\|\mathcal{I}_{h,i}^k u\|_{H^1(I_i)} \lesssim \|u\|_{H^1(I_i)}, \quad u \in H^1(I_i).` | `\|\mathcal I_{h,i}^k u\|_{H^1(I_i)} \lesssim \|u\|_{H^1(I_i)}, u \in H^1(I_i).` |
| `uh_p18e84` | b_gap | `\sum_{m=0}^{l+1}\|(h\partial)^m(u - \mathcal{I}^k_{h,i}u)\|_{L^2(I_i)}\lesssim\|(h\partial)^{l+1}u\|_{L^2(I_i)},\quad u\in H^{l+1}(I_i).` | `\sum_{m=0}^{l+1} \|(h\partial)^m (u - \mathcal I_{h,i}^k u)\|_{L^2(I_i)} \lesssim \|(h\partial)^{l+1} u\|_{L^2(I_i)}, u \in H^{l+1}(I_i).` |
| `uh_p18e85` | muse_error | `||(h\partial)(u-u_h)||\underset{\sim}{\lesssim}||(h\partial)^{l+1}u||,` | `\|(h\partial)(u-u_h)\| \lesssim \|(h \partial)^{l+1} u\|,` |
| `uh_p18e86` | muse_error | `|| u - u_h || \lesssim || (h\partial)^{l+1} u ||.` | `\|u-u_h\| \lesssim \|(h \partial)^{l+1} u\|.` |
| `uh_p18e87` | agrees | `V = H_0^1(\Omega) = \{u \in H^1(\Omega) \mid u|_{\partial\Omega} = 0\},` | `V = H_0^1(\Omega) = \{u \in H^1(\Omega) \mid u|_{\partial \Omega} = 0\},` |
| `uh_p19e88` | agrees | `a(u, v) = L(v) \text{ for all } v \in V.` | `a(u, v) = L(v) \text{for all $v \in V$}.` |
| `uh_p19e89` | agrees | `\mathcal{I}_h : V \to V_h,` | `\mathcal I_h : V \to V_h,` |
| `uh_p19e90` | b_gap | `\|(h\nabla)(u - \mathcal{I}_h u)\|_{L^2(\Omega)} \lesssim \|(hD)^2 u\|_{L^2(\Omega)},` | `\|(h\nabla)(u - \mathcal I_h u)\|_{L^2(\Omega)} \lesssim \|(hD)^2 u\|_{L^2(\Omega)},` |
| `uh_p19e91` | b_gap | `\|D^2 u\|_{L^2(\Omega)} \lesssim \|f\|_{L^2(\Omega)}.` | `\|D^2 u\|_{L^2(\Omega)} \lesssim \|f\|_{L^2(\Omega)}.` |
| `uh_p19e92` | agrees | `a(u_h, v) = L(v) \text{ for all } v \in V_h,` | `a(u_h,v) = L(v) \text{for all $v \in V_h$},` |
| `uh_p19e93` | b_gap | `\|u - u_h\|_{L^2(\Omega)} + \|(h\nabla)(u - u_h)\|_{L^2(\Omega)} \lesssim \|(hD)^2u\|_{L^2(\Omega)}.` | `\|u - u_h\|_{L^2(\Omega)} + \|(h\nabla)(u - u_h)\|_{L^2(\Omega)} \lesssim \|(hD)^2 u\|_{L^2(\Omega)}.` |
| `uh_p19e94` | b_gap | `\| \cdot \| = \| \cdot \|_{L^2(\Omega)}, \| \cdot \|_E = a(\cdot,\cdot),` | `\|\cdot\| = \|\cdot\|_{L^2(\Omega)}, \|\cdot\|_E = a(\cdot, \cdot),` |
| `uh_p20e95` | agrees | `\|(h\nabla)(w - \mathcal{I}_h)\| \lesssim \|h^2 D^2 w\| \lesssim h^2\|u - u_h\|,` | `\|(h\nabla)(w - \mathcal I_h)\| \lesssim \|h^2 D^2 w\| \lesssim h^2 \|u - u_h\|,` |
| `uh_p20e96` | b_gap | `a(u, v) = \int_{\Omega} (\nabla u \cdot \nabla v + q u v) dx.` | `a(u,v) = \int_\Omega (\nabla u \cdot \nabla v + q u v)\, dx.` |
| `ffns_p8e1` | agrees | `\boldsymbol{x} = (x, y, z)` | `\nabla\phi= \left(\frac{\partial\phi}{\partial x}, \frac{\partial\phi}{\partial y}, \frac{\partial\phi}{\partial z}\right).` |
| `ffns_p10e2` | b_gap | `\frac{d}{dt}\phi(\mathbf{X}(t),t) = \frac{\partial\phi}{\partial t} + \frac{d\mathbf{X}}{dt} \cdot \nabla\phi \\ = \frac{\partial\phi}{\partial t} + \boldsymbol{u} \cdot \nabla\phi.` | `\frac{d\mathbf{X}}{dt} =\bm{u}(\mathbf{X}(\bm{\xi},t),t).` |
| `ffns_p10e3` | agrees | `\frac{D\phi}{Dt} = \frac{\partial\phi}{\partial t} + \boldsymbol{u} \cdot \nabla \phi.` | `\boxed{\frac{D\phi}{Dt} =\frac{\partial\phi}{\partial t} +\bm{u}\cdot\nabla\phi}.` |
| `ffns_p11e4` | agrees | `\frac{d\phi}{dt} = \frac{\partial\phi}{\partial t} + \frac{dx}{dt} \frac{\partial\phi}{\partial x} + \frac{dy}{dt} \frac{\partial\phi}{\partial y} + \frac{dz}{dt} \frac{\partial\phi}{\partial z}.` | `\frac{d\phi}{dt} =\frac{\partial\phi}{\partial t} +\frac{dx}{dt}\frac{\partial\phi}{\partial x} +\frac{dy}{dt}\frac{\partial\phi}{\partial y} +\frac{dz}{dt}\frac{\partial\phi}{\partial z}.` |
| `ffns_p11e5` | agrees | `\frac{D\phi}{Dt} = \frac{\partial\phi}{\partial t} + u\frac{\partial\phi}{\partial x} + v\frac{\partial\phi}{\partial y} + w\frac{\partial\phi}{\partial z}` | `\boxed{ \frac{D\phi}{Dt} =\frac{\partial\phi}{\partial t} +u\frac{\partial\phi}{\partial x} +v\frac{\partial\phi}{\partial y} +w\frac{\partial\phi}{\partial z}}` |
| `ffns_p12e6` | agrees | `\boldsymbol{a} = \frac{D \boldsymbol{u}}{D t} = \frac{\partial \boldsymbol{u}}{\partial t} + (\boldsymbol{u} \cdot \nabla) \boldsymbol{u}.` | `\boxed{ \bm{a} =\frac{D\bm{u}}{Dt} =\frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} }.` |
| `ffns_p12e7` | agrees | `a_i = \frac{\partial u_i}{\partial t} + u_j\frac{\partial u_i}{\partial x_j},` | `a_i=\frac{\partial u_i}{\partial t} +u_j\frac{\partial u_i}{\partial x_j},` |
| `ffns_p14e8` | b_gap | `\frac{D\boldsymbol{u}}{Dt} = \frac{\partial \boldsymbol{u}}{\partial t} + (\boldsymbol{u} \cdot \nabla)\boldsymbol{u}.` | `\frac{D\bm{u}}{Dt} =\underbrace{\frac{\partial\bm{u}}{\partial t}}_{\text{local acceleration}} +\underbrace{(\bm{u}\cdot\nabla)\bm{u}}_{\text{advective acceleration}}.` |
| `ffns_p15e9` | agrees | `\frac{d}{dt}|\Omega(t)| = 0.` | `\boxed{\frac{d}{dt}|\Omega(t)|=0}.` |
| `ffns_p18e10` | b_gap | `\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \boldsymbol{u}) = 0 \Longleftrightarrow \frac{D \rho}{D t} + \rho \nabla \cdot \boldsymbol{u} = 0.` | `\boxed{ \frac{\partial\rho}{\partial t} +\nabla\cdot(\rho\bm{u})=0 } \Longleftrightarrow \boxed{ \frac{D\rho}{Dt}+\rho\nabla\cdot\bm{u}=0 }.` |
| `ffns_p18e11` | b_gap | `\frac{D \rho}{D t} = 0 \implies \boxed{\nabla \cdot \boldsymbol{u} = 0}.` | `\frac{D\rho}{Dt}=0 \Longrightarrow \boxed{\nabla\cdot\bm{u}=0}.` |
| `ffns_p19e12` | agrees | `\boldsymbol{t}_p(\boldsymbol{n}) = -p\boldsymbol{n}.` | `\boxed{\bm{t}_p(\bm{n})=-p\bm{n}}.` |
| `ffns_p22e13` | agrees | `\mathbf{F}_{p,parcel} \approx -(\nabla p) \delta V.` | `\boxed{\mathbf{F}_{p,\mathrm{parcel}} \approx-(\nabla p)\,\delta V}.` |
| `ffns_p22e14` | agrees | `\mathbf{F}_{p,surroundings} \approx +(\nabla p) \delta V.` | `\mathbf{F}_{p,\mathrm{surroundings}} \approx+(\nabla p)\,\delta V.` |
| `ffns_p23e15` | agrees | `\boldsymbol{t}_p = -p\boldsymbol{n}.` | `\bm{t}_p=-p\bm{n}.` |
| `ffns_p24e16` | agrees | `\mathbf{F}_{\text{total}} \approx (-\nabla p + \rho \boldsymbol{g}) \delta V.` | `\boxed{\mathbf{F}_{\mathrm{total}} \approx(-\nabla p+\rho\bm g)\,\delta V}.` |
| `ffns_p25e17` | agrees | `\rho \delta V \frac{D \boldsymbol{u}}{D t} = (-\nabla p + \rho \boldsymbol{g}) \delta V.` | `\rho\,\delta V\,\frac{D\bm{u}}{Dt} =(-\nabla p+\rho\bm g)\,\delta V.` |
| `ffns_p25e18` | agrees | `\rho \frac{D \boldsymbol{u}}{D t} = -\nabla p + \rho \boldsymbol{g}.` | `\boxed{ \rho\frac{D\bm{u}}{Dt}=-\nabla p+\rho\bm g}.` |
| `ffns_p26e19` | agrees | `\frac{\partial \boldsymbol{u}}{\partial t} + (\boldsymbol{u} \cdot \nabla) \boldsymbol{u} = -\frac{1}{\rho} \nabla p + \boldsymbol{b}.` | `\boxed{ \frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} =-\frac{1}{\rho}\nabla p+\bm{b}}.` |
| `ffns_p28e20` | agrees | `\boldsymbol{t}(\boldsymbol{n}) dS,` | `\bm{t}(\bm{n})\,dS,` |
| `ffns_p30e21` | agrees | `t_i = \sigma_{ij} n_j.` | `\boxed{\bm{t}(\bm{n})=\bm{\sigma}\bm{n}}, t_i=\sigma_{ij}n_j.` |
| `ffns_p32e22` | agrees | `\rho \frac{D \boldsymbol{u}}{D t} = \nabla \cdot \boldsymbol{\sigma} + \rho \boldsymbol{b}.` | `\boxed{\rho\frac{D\bm{u}}{Dt} =\nabla\cdot\bm{\sigma}+\rho\bm{b}}.` |
| `ffns_p33e23` | agrees | `t_i = \sigma_{ij} n_j, (\nabla \cdot \boldsymbol{\sigma})_i = \frac{\partial \sigma_{ij}}{\partial x_j}.` | `t_i=\sigma_{ij}n_j, (\nabla\cdot\bm{\sigma})_i =\frac{\partial\sigma_{ij}}{\partial x_j}.` |
| `ffns_p33e24` | agrees | `\rho \left(\frac{\partial u_i}{\partial t} + u_j \frac{\partial u_i}{\partial x_j}\right) = \frac{\partial \sigma_{ij}}{\partial x_j} + \rho b_i.` | `\boxed{ \rho\left( \frac{\partial u_i}{\partial t} +u_j\frac{\partial u_i}{\partial x_j} \right) =\frac{\partial\sigma_{ij}}{\partial x_j} +\rho b_i}.` |
| `ffns_p34e25` | agrees | `\rho \frac{D \boldsymbol{u}}{D t} = -\nabla p + \nabla \cdot \boldsymbol{\tau} + \rho \boldsymbol{b}.` | `\rho\frac{D\bm{u}}{Dt} =-\nabla p+\nabla\cdot\bm{\tau}+\rho\bm{b}.` |
| `ffns_p35e26` | agrees | `\mathrm{tr} \mathbf{D} = \nabla \cdot \mathbf{u}.` | `\operatorname{tr}\mathbf{D}=\nabla\cdot\bm{u}.` |
| `ffns_p36e27` | agrees | `d\boldsymbol{u} = (\nabla \boldsymbol{u}) d\boldsymbol{x} = \mathbf{D} d\boldsymbol{x} + \mathbf{W} d\boldsymbol{x}.` | `d\bm{u}=(\nabla\bm{u})\,d\bm{x} =\mathbf{D}\,d\bm{x}+\mathbf{W}\,d\bm{x}.` |
| `ffns_p37e28` | agrees | `\boldsymbol{\tau} = 2\mu\mathbf{D} + \lambda(\nabla \cdot \boldsymbol{u})\mathbf{I}.` | `\bm{\tau}=2\mu\mathbf{D} +\lambda(\nabla\cdot\bm{u})\mathbf{I}.` |
| `ffns_p38e29` | agrees | `\boldsymbol{\tau} = 2\mu \mathbf{D} + \lambda(\nabla \cdot \boldsymbol{u})\mathbf{I}.` | `\boxed{ \bm{\tau} =2\mu\mathbf{D} +\lambda(\nabla\cdot\bm{u})\mathbf{I} }.` |
| `ffns_p39e30` | agrees | `\boxed{\boldsymbol{\tau} = 2\mu\mathbf{D}}, \boxed{\boldsymbol{\sigma} = -p\mathbf{I} + 2\mu\mathbf{D}}.` | `\boxed{\bm{\tau}=2\mu\mathbf{D}}, \boxed{\bm{\sigma}=-p\mathbf{I}+2\mu\mathbf{D}}.` |
| `ffns_p39e31` | agrees | `\sigma_{ij} = -p\delta_{ij} + \mu \left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i}\right).` | `\sigma_{ij} =-p\delta_{ij} +\mu\left( \frac{\partial u_i}{\partial x_j} +\frac{\partial u_j}{\partial x_i} \right).` |
| `ffns_p40e32` | agrees | `\nabla \cdot (2 \mu \mathbf{D}) = \mu \nabla^2 \mathbf{u} + \mu \nabla (\nabla \cdot \mathbf{u}).` | `\nabla\cdot(2\mu\mathbf{D}) =\mu\nabla^2\bm{u} +\mu\nabla(\nabla\cdot\bm{u}).` |
| `ffns_p41e33` | agrees | `\rho \left[\frac{\partial \boldsymbol{u}}{\partial t} + (\boldsymbol{u} \cdot \nabla)\boldsymbol{u}\right] = -\nabla p + \mu \nabla^2 \boldsymbol{u} + \rho \boldsymbol{b}` | `\boxed{ \rho\left[ \frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} \right] =-\nabla p+\mu\nabla^2\bm{u}+\rho\bm{b} }` |
| `ffns_p41e34` | agrees | `\frac{\partial \boldsymbol{u}}{\partial t} + (\boldsymbol{u} \cdot \nabla) \boldsymbol{u} = -\frac{1}{\rho} \nabla p + \nu \nabla^2 \boldsymbol{u} + \boldsymbol{b}.` | `\frac{\partial\bm{u}}{\partial t} +(\bm{u}\cdot\nabla)\bm{u} =-\frac{1}{\rho}\nabla p +\nu\nabla^2\bm{u}+\bm{b}.` |
| `ffns_p44e35` | agrees | `\rho \left(\frac{\partial u_i}{\partial t} + u_j \frac{\partial u_i}{\partial x_j}\right) = -\frac{\partial p}{\partial x_i} + \mu \frac{\partial^2 u_i}{\partial x_j \partial x_j} + \rho b_i, \quad i = 1, 2, 3,` | `\boxed{ \rho\left( \frac{\partial u_i}{\partial t} +u_j\frac{\partial u_i}{\partial x_j} \right) =-\frac{\partial p}{\partial x_i} +\mu\frac{\partial^2u_i}{\partial x_j\partial x_j} +\rho b_i }, i=1,2,3,` |
| `ffns_p44e36` | agrees | `\frac{\partial u_i}{\partial x_i} = 0.` | `\boxed{\frac{\partial u_i}{\partial x_i}=0}.` |
| `ffns_p45e37` | muse_error | `\rho(\boldsymbol{u} \cdot \nabla)\boldsymbol{u} = -\nabla p + \mu \nabla^2 \boldsymbol{u} + \rho \boldsymbol{b}` | `\boxed{ \rho(\bm{u}\cdot\nabla)\bm{u} =-\nabla p+\mu\nabla^2\bm{u}+\rho\bm{b}}, \boxed{\nabla\cdot\bm{u}=0}.` |
| `ffns_p46e38` | agrees | `\boldsymbol{u} = (u(y, t), 0, 0), \frac{\partial u}{\partial x} = \frac{\partial u}{\partial z} = 0.` | `\bm{u}=(u(y,t),0,0), \frac{\partial u}{\partial x} =\frac{\partial u}{\partial z}=0.` |
| `ffns_p46e39` | agrees | `\rho \frac{\partial u}{\partial t} = -\frac{\partial p}{\partial x} + \mu \frac{\partial^2 u}{\partial y^2} + \rho b_x.` | `\boxed{ \rho\frac{\partial u}{\partial t} =-\frac{\partial p}{\partial x} +\mu\frac{\partial^2u}{\partial y^2} +\rho b_x }.` |
| `ffns_p47e40` | agrees | `\rho(u_t + u u_x + v u_y) = -p_x + \mu(u_{xx} + u_{yy}) + \rho b_x,` | `\rho(u_t+u u_x+v u_y) =-p_x+\mu(u_{xx}+u_{yy})+\rho b_x,` |
| `ffns_p47e41` | agrees | `\rho(v_t + u v_x + v v_y) = -p_y + \mu(v_{xx} + v_{yy}) + \rho b_y,` | `\rho(v_t+u v_x+v v_y) =-p_y+\mu(v_{xx}+v_{yy})+\rho b_y,` |
| `ffns_p47e42` | agrees | `u_x + v_y = 0.` | `\boxed{u_x+v_y=0}.` |
| `ffns_p49e43` | agrees | `\boldsymbol{u}(\boldsymbol{x},0) = \boldsymbol{u}_0(\boldsymbol{x}), \quad \nabla \cdot \boldsymbol{u}_0 = 0,` | `\bm{u}(\bm{x},0)=\bm{u}_0(\bm{x}), \nabla\cdot\bm{u}_0=0,` |
| `ffns_p49e44` | b_gap | `\boldsymbol{u} = \bar{\boldsymbol{u}} \text{on} \Gamma_D, \quad \boldsymbol{\sigma} \boldsymbol{n} = \bar{\boldsymbol{t}} \text{on} \Gamma_N.` | `\bm{u}=\overline{\bm{u}} \ \text{on }\Gamma_D, \bm{\sigma}\bm{n}=\overline{\bm{t}} \ \text{on }\Gamma_N.` |
| `ffns_p50e45` | agrees | `(\boldsymbol{u} - \mathbf{U}_{wall}) \cdot \boldsymbol{n} = 0.` | `(\bm{u}-\mathbf{U}_{\mathrm{wall}})\cdot\bm{n}=0.` |
| `ffns_p51e46` | agrees | `\boldsymbol{\sigma} \boldsymbol{n} = -p_{\text{ext}} \boldsymbol{n};` | `\bm{\sigma}\bm{n}=-p_{\mathrm{ext}}\bm{n};` |
| `ffns_p52e47` | b_gap | `(\boldsymbol{u} - \boldsymbol{U}_{\text{wall}}) \cdot \boldsymbol{n} = 0, (\boldsymbol{\sigma} \boldsymbol{n})_{||} + \frac{\mu}{\ell_s}(\boldsymbol{u} - \boldsymbol{U}_{\text{wall}})_{||} = 0.` | `(\bm{\sigma}\bm{n})_{\parallel} +\frac{\mu}{\ell_s} (\bm{u}-\mathbf U_{\mathrm{wall}})_{\parallel}=0.` |
| `ffns_p53e48` | agrees | `(\boldsymbol{u} - \mathbf{U}_{wall}) \cdot \boldsymbol{n} = 0,` | `(\bm{u}-\mathbf{U}_{\mathrm{wall}})\cdot\bm{n}=0,` |
| `ffns_p56e49` | agrees | `\nabla^2 p = -\rho \nabla \cdot [(\boldsymbol{u} \cdot \nabla)\boldsymbol{u}] + \rho \nabla \cdot \boldsymbol{b}.` | `\boxed{ \nabla^2p =-\rho\,\nabla\cdot\left[(\bm{u}\cdot\nabla)\bm{u}\right] +\rho\,\nabla\cdot\bm{b} }.` |
| `ffns_p63e50` | agrees | `\nabla \cdot (2\mu \mathbf{D}) = \mu \nabla^2 \mathbf{u} + \mu \nabla(\nabla \cdot \mathbf{u}).` | `\nabla\cdot(2\mu\mathbf{D}) =\mu\nabla^2\bm{u} +\mu\nabla(\nabla\cdot\bm{u}).` |
