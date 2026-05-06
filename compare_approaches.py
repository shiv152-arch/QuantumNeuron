"""
compare_approaches.py
=====================
Runs the full comparison between the Old and Novel quantum neuron approaches,
reproducing and extending the figures from the paper.

Generates:
  results/01_activation_functions_old.png   – f(θ,k) for various k
  results/02_activation_functions_novel.png – g(θ,k) for various k
  results/03_resource_comparison.png        – qubit & CX gate scaling
  results/04_simulation_vs_theory.png       – IBM-style sim results (novel)
  results/05_side_by_side_comparison.png    – combined comparison panel
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from qiskit_aer import AerSimulator

# Make sure src/ is importable
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from quantum_neuron import (
    f_theoretical, g_theoretical,
    old_approach_resources, novel_approach_resources,
    simulate_novel,
)

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

THETA = np.linspace(0.01, np.pi / 2 - 0.01, 300)

# ── colour palette ────────────────────────────────────────────────────────────
OLD_COLORS   = ["#e63946", "#f4a261", "#2a9d8f", "#457b9d", "#6a4c93"]
NOVEL_COLORS = ["#4361ee", "#3a0ca3", "#7209b7", "#f72585", "#4cc9f0"]


# ── 1. Old approach: f(θ,k) ──────────────────────────────────────────────────
def plot_old_approach():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    k_values = [1, 2, 3, 4, 5]
    for k, c in zip(k_values, OLD_COLORS):
        ax.plot(THETA, f_theoretical(THETA, k), color=c, lw=2,
                label=f"k = {k}")
    ax.set_xlabel(r"$\theta$", fontsize=13)
    ax.set_ylabel(r"$f(\theta, k)$", fontsize=13)
    ax.set_title("Old Approach: $f(\\theta,k) = \\sin^2(\\arctan(\\tan^{2^k}(\\theta)))$",
                 fontsize=11)
    ax.legend(framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, np.pi / 2)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, "01_activation_functions_old.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ── 2. Novel approach: g(θ,k) ────────────────────────────────────────────────
def plot_novel_approach():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    k_values = [1.0, 1.25, 1.5, 1.75, 2.0]
    for k, c in zip(k_values, NOVEL_COLORS):
        ax.plot(THETA, g_theoretical(THETA, k), color=c, lw=2,
                label=f"k = {k}")
    ax.set_xlabel(r"$\theta$", fontsize=13)
    ax.set_ylabel(r"$g(\theta, k)$", fontsize=13)
    ax.set_title("Novel Approach: $g(\\theta,k) = \\sin^2(\\arctan(\\tan^2(k\\theta)))$",
                 fontsize=11)
    ax.legend(framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, "02_activation_functions_novel.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ── 3. Resource comparison ────────────────────────────────────────────────────
def plot_resource_comparison():
    k_range = np.arange(1, 5.1, 0.1)
    old_qubits  = [old_approach_resources(int(k))["qubits"]   for k in range(1, 6)]
    old_cx      = [old_approach_resources(int(k))["cx_gates"] for k in range(1, 6)]
    k_int       = list(range(1, 6))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))

    # Qubits
    ax1.plot(k_int, old_qubits, "o-", color="#e63946", lw=2, ms=7,
             label="Old approach ($2^k$ qubits)")
    ax1.axhline(y=2, color="#4361ee", lw=2, ls="--", label="Novel approach (2 qubits, constant)")
    ax1.set_xlabel("k (approximation order)", fontsize=12)
    ax1.set_ylabel("No. of qubits", fontsize=12)
    ax1.set_title("Qubit Scaling", fontsize=12)
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xticks(k_int)

    # CX gates
    ax2.plot(k_int, old_cx, "s-", color="#e63946", lw=2, ms=7,
             label="Old approach ($2k-1$ CX gates)")
    ax2.axhline(y=1, color="#4361ee", lw=2, ls="--", label="Novel approach (1 CX gate, constant)")
    ax2.set_xlabel("k (approximation order)", fontsize=12)
    ax2.set_ylabel("No. of CX gates", fontsize=12)
    ax2.set_title("CX Gate Scaling", fontsize=12)
    ax2.legend(fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xticks(k_int)

    fig.suptitle("Resource Comparison: Old vs Novel Approach", fontsize=13, fontweight="bold")
    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, "03_resource_comparison.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ── 4. Simulation vs theory (novel approach, noisy AerSimulator) ─────────────
def plot_simulation_vs_theory():
    backend = AerSimulator()
    # Use from_noise_model or add depolarizing noise for realism
    try:
        from qiskit_aer.noise import NoiseModel, depolarizing_error
        noise_model = NoiseModel()
        error_1q = depolarizing_error(0.01, 1)
        error_2q = depolarizing_error(0.02, 2)
        noise_model.add_all_qubit_quantum_error(error_1q, ["ry"])
        noise_model.add_all_qubit_quantum_error(error_2q, ["cx"])
        noisy_backend = AerSimulator(noise_model=noise_model)
    except Exception:
        noisy_backend = backend

    theta_sim = np.linspace(0.05, np.pi / 2 - 0.05, 25)
    k_values  = [0.95, 1.0, 1.05, 1.1]
    colors    = ["#4361ee", "#7209b7", "#f72585", "#4cc9f0"]

    fig, ax = plt.subplots(figsize=(8, 5))

    for k, c in zip(k_values, colors):
        theory = g_theoretical(theta_sim, k)
        simulated = np.array([
            simulate_novel(t, k, shots=4096, backend=noisy_backend)
            for t in theta_sim
        ])
        ax.plot(theta_sim, theory,    color=c, lw=2,   ls="--", label=f"Theory k={k}")
        ax.plot(theta_sim, simulated, color=c, lw=1.5, ls="-",  marker="o", ms=4,
                label=f"Simulated k={k}")

    ax.set_xlabel(r"$\theta$", fontsize=13)
    ax.set_ylabel("Measurement Probability", fontsize=13)
    ax.set_title("Novel Approach: Theory (dashed) vs Noisy Simulation (solid)\n"
                 "Reproducing Fig. 9 style from Maheshwari et al. 2023", fontsize=11)
    ax.legend(fontsize=8, ncol=2, framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, np.pi / 2)
    ax.set_ylim(0, 1.05)
    fig.tight_layout()
    path = os.path.join(RESULTS_DIR, "04_simulation_vs_theory.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ── 5. Side-by-side summary panel ────────────────────────────────────────────
def plot_side_by_side():
    fig = plt.figure(figsize=(14, 9))
    gs  = GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

    # — top left: old approach
    ax1 = fig.add_subplot(gs[0, 0])
    for k, c in zip([1, 2, 3, 4, 5], OLD_COLORS):
        ax1.plot(THETA, f_theoretical(THETA, k), color=c, lw=2, label=f"k={k}")
    ax1.set_title("Old: $f(\\theta,k) = \\sin^2(\\arctan(\\tan^{2^k}(\\theta)))$", fontsize=10)
    ax1.set_xlabel(r"$\theta$"); ax1.set_ylabel(r"$f(\theta,k)$")
    ax1.legend(fontsize=8); ax1.grid(True, alpha=0.3); ax1.set_xlim(0, np.pi/2)

    # — top right: novel approach
    ax2 = fig.add_subplot(gs[0, 1])
    for k, c in zip([1.0, 1.25, 1.5, 1.75, 2.0], NOVEL_COLORS):
        ax2.plot(THETA, g_theoretical(THETA, k), color=c, lw=2, label=f"k={k}")
    ax2.set_title("Novel: $g(\\theta,k) = \\sin^2(\\arctan(\\tan^2(k\\theta)))$", fontsize=10)
    ax2.set_xlabel(r"$\theta$"); ax2.set_ylabel(r"$g(\theta,k)$")
    ax2.legend(fontsize=8); ax2.grid(True, alpha=0.3); ax2.set_xlim(0, 1.0)

    # — bottom left: qubit comparison
    ax3 = fig.add_subplot(gs[1, 0])
    k_int = list(range(1, 6))
    ax3.plot(k_int, [2**k for k in k_int], "o-", color="#e63946", lw=2, ms=7,
             label="Old (exponential)")
    ax3.axhline(y=2, color="#4361ee", lw=2, ls="--", label="Novel (constant=2)")
    ax3.set_title("Qubit Scaling", fontsize=10)
    ax3.set_xlabel("k"); ax3.set_ylabel("No. of qubits")
    ax3.legend(fontsize=8); ax3.grid(True, alpha=0.3); ax3.set_xticks(k_int)

    # — bottom right: CX gate comparison
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(k_int, [2*k-1 for k in k_int], "s-", color="#e63946", lw=2, ms=7,
             label="Old (linear)")
    ax4.axhline(y=1, color="#4361ee", lw=2, ls="--", label="Novel (constant=1)")
    ax4.set_title("CX Gate Scaling", fontsize=10)
    ax4.set_xlabel("k"); ax4.set_ylabel("No. of CX gates")
    ax4.legend(fontsize=8); ax4.grid(True, alpha=0.3); ax4.set_xticks(k_int)

    fig.suptitle(
        "Resource-Efficient Quantum Neuron — Old vs Novel Approach\n"
        "Maheshwari et al., IEEE Globecom Workshop 2023",
        fontsize=13, fontweight="bold"
    )
    path = os.path.join(RESULTS_DIR, "05_side_by_side_comparison.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"  Saved {path}")


# ── entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Quantum Neuron Comparison ===\n")

    print("[1/5] Old approach activation functions...")
    plot_old_approach()

    print("[2/5] Novel approach activation functions...")
    plot_novel_approach()

    print("[3/5] Resource comparison...")
    plot_resource_comparison()

    print("[4/5] Noisy simulation vs theory (this may take ~1 min)...")
    plot_simulation_vs_theory()

    print("[5/5] Side-by-side summary panel...")
    plot_side_by_side()

    print("\n✓ All plots saved to results/")
