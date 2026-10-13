"""
Generate equation images and the pipeline diagram used in the
Qiskit Fall Fest PS-01 Max-Cut project's README and report.

Creates:
    assets/qff_phase1_latex_images/
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


# Expected location: scripts/make_assets.py
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "assets" / "qff_phase1_latex_images"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Mathematical equations used in the project.
EQUATIONS = {
    "eq_maxcut_cost": (
        r"$C(z)=\sum_{(i,j)\in E} w_{ij}\,\frac{1-z_i z_j}{2},"
        r"\quad z_i\in\{-1,+1\}$"
    ),

    "eq_cost_hamiltonian": (
        r"$H_C=\sum_{(i,j)\in E}\frac{w_{ij}}{2}(I-Z_iZ_j)$"
    ),

    "eq_qaoa_state": (
        r"$|\gamma,\beta\rangle="
        r"\prod_{\ell=1}^{p}"
        r"\left[e^{-i\beta_\ell H_M}"
        r"e^{-i\gamma_\ell H_C}\right]"
        r"|+\rangle^{\otimes n},"
        r"\quad H_M=\sum_i X_i$"
    ),

    # Under RZZ(theta) = exp(-i * theta * ZZ / 2),
    # exp(-i * gamma * HC) uses RZZ(-gamma * weight),
    # up to a global phase for each edge.
    "eq_rzz_gate": (
        r"$R_{ZZ}(-\gamma w_{ij})="
        r"e^{+i\gamma w_{ij}Z_iZ_j/2}"
        r"\;\longrightarrow\;"
        r"\mathrm{CX}\cdot R_Z(-\gamma w_{ij})\cdot\mathrm{CX}$"
    ),

    "eq_approx_ratio": (
        r"$r=\frac{\langle C\rangle}{C_{\max}},"
        r"\qquad "
        r"r_{\mathrm{random}}="
        r"\frac{\frac{1}{2}\sum_{(i,j)\in E}w_{ij}}{C_{\max}}$"
    ),

    # This formula applies to a Bernoulli outcome with success probability p.
    # For general Max-Cut score samples, use the sample standard error instead.
    "eq_bernoulli_standard_error": (
        r"$\mathrm{SE}(\hat p)\approx"
        r"\sqrt{\frac{p(1-p)}{N}}"
        r"\quad\text{(Bernoulli outcome)}$"
    ),

    "eq_hellinger_fidelity": (
        r"$F=\left(\sum_x"
        r"\sqrt{P_{\mathrm{ideal}}(x)P_{\mathrm{noisy}}(x)}"
        r"\right)^2$"
    ),

    "eq_swap_cost": (
        r"$\mathrm{SWAP}=3\,\mathrm{CX},"
        r"\qquad N_{\mathrm{CX}}="
        r"2p|E|+3N_{\mathrm{SWAP}}$"
        r"\quad\text{(before cancellations)}$"
    ),
}


def render_equations():
    """Render each LaTeX equation as a PNG image."""
    for name, equation in EQUATIONS.items():
        fig = plt.figure(figsize=(9, 1.1))
        fig.text(
            0.5,
            0.5,
            equation,
            ha="center",
            va="center",
            fontsize=15,
        )

        fig.savefig(
            OUTPUT_DIR / f"{name}.png",
            dpi=200,
            bbox_inches="tight",
            pad_inches=0.15,
            facecolor="white",
        )
        plt.close(fig)


def draw_box(ax, x, y, width, height, label, facecolor):
    """Draw a labeled rounded rectangle."""
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.05",
        facecolor=facecolor,
        edgecolor="#333333",
        linewidth=1.0,
    )
    ax.add_patch(patch)

    ax.text(
        x + width / 2,
        y + height / 2,
        label,
        ha="center",
        va="center",
        fontsize=8,
    )


def draw_arrow(ax, start, end):
    """Draw a directional arrow between pipeline stages."""
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops={
            "arrowstyle": "->",
            "color": "#333333",
            "linewidth": 1.2,
        },
    )


def render_pipeline():
    """Render the processor comparison and evaluation pipeline."""
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis("off")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)

    # Input and QAOA circuit
    draw_box(
        ax, 0.2, 1.55, 1.8, 0.9,
        "Weighted\nMax-Cut graph", "#e8f0fe"
    )
    draw_box(
        ax, 2.4, 1.55, 1.8, 0.9,
        "QAOA circuit\np = 1, 2", "#e8f0fe"
    )

    # Processor A branch
    draw_box(
        ax, 4.8, 2.5, 1.8, 0.9,
        "Processor A\n5-qubit branching", "#cfe3ff"
    )
    draw_box(
        ax, 7.0, 2.5, 1.8, 0.9,
        "Transpile\nlayout + routing", "#f1f1f1"
    )
    draw_box(
        ax, 9.2, 2.5, 1.8, 0.9,
        "Noisy execution\nsame noise model", "#f1f1f1"
    )

    # Processor B branch
    draw_box(
        ax, 4.8, 0.6, 1.8, 0.9,
        "Processor B\n9-qubit topology", "#ffe0b3"
    )
    draw_box(
        ax, 7.0, 0.6, 1.8, 0.9,
        "Transpile\nlayout + routing", "#f1f1f1"
    )
    draw_box(
        ax, 9.2, 0.6, 1.8, 0.9,
        "Noisy execution\nsame noise model", "#f1f1f1"
    )

    # Final metrics
    draw_box(
        ax, 11.5, 1.55, 2.2, 0.9,
        "Metrics\ncut quality, CX,\ndepth and SWAPs", "#d9f2d9"
    )

    # Connect stages
    draw_arrow(ax, (2.0, 2.0), (2.4, 2.0))
    draw_arrow(ax, (4.2, 2.0), (4.8, 2.95))
    draw_arrow(ax, (4.2, 2.0), (4.8, 1.05))

    draw_arrow(ax, (6.6, 2.95), (7.0, 2.95))
    draw_arrow(ax, (8.8, 2.95), (9.2, 2.95))

    draw_arrow(ax, (6.6, 1.05), (7.0, 1.05))
    draw_arrow(ax, (8.8, 1.05), (9.2, 1.05))

    draw_arrow(ax, (11.0, 2.95), (11.5, 2.25))
    draw_arrow(ax, (11.0, 1.05), (11.5, 1.75))

    ax.set_title(
        "PS-01 Max-Cut: comparing two processor architectures",
        fontsize=12,
        pad=12,
    )

    fig.savefig(
        OUTPUT_DIR / "pipeline_overview.png",
        dpi=200,
        bbox_inches="tight",
        facecolor="white",
    )
    plt.close(fig)


def main():
    render_equations()
    render_pipeline()

    generated_files = sorted(
        path.name for path in OUTPUT_DIR.glob("*.png")
    )

    print(f"Assets saved to: {OUTPUT_DIR}")
    print(f"Generated {len(generated_files)} PNG files:")

    for filename in generated_files:
        print(f"  - {filename}")


if __name__ == "__main__":
    main()