"""
visualise_circuits.py
=====================
Draws and saves the quantum circuits used in both approaches.
"""

import os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from quantum_neuron import build_rus_block

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.visualization import circuit_drawer

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


def draw_rus_block():
    """Single RUS block (Fig. 3 in the paper)."""
    qr = QuantumRegister(2, "q")
    cr = ClassicalRegister(2, "c")
    qc = QuantumCircuit(qr, cr)

    qc.ry(0.5, 0)          # Ry(θ) on ancilla
    qc.cx(0, 1)            # CX gate
    qc.ry(-0.5, 0)         # Ry(-θ) on ancilla
    qc.barrier()
    qc.measure(qr, cr)

    fig = qc.draw("mpl", style="iqp", filename=None)
    fig.suptitle("Single RUS Block — Novel Approach Circuit (Fig. 3)", fontsize=12)
    path = os.path.join(RESULTS_DIR, "circuit_novel_rus_block.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


def draw_old_approach_k2():
    """Old approach circuit for k=2 (2 RUS blocks, 4 qubits)."""
    # k=2 requires 2^2=4 qubits (ancilla chain) + 1 target = 5 in full form.
    # We show a simplified 2-level version with 3 qubits for clarity.
    qc = QuantumCircuit(3, 3)
    # RUS block 1
    qc.ry(0.5, 0); qc.cx(0, 1); qc.ry(-0.5, 0)
    qc.barrier()
    # RUS block 2 (re-uses ancilla 0 in real circuit; shown separately for clarity)
    qc.ry(0.5, 1); qc.cx(1, 2); qc.ry(-0.5, 1)
    qc.barrier()
    qc.measure([0, 1, 2], [0, 1, 2])

    fig = qc.draw("mpl", style="iqp", filename=None)
    fig.suptitle("Old Approach — k=2 (2 RUS blocks, exponential qubit scaling)", fontsize=11)
    path = os.path.join(RESULTS_DIR, "circuit_old_approach_k2.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved {path}")


if __name__ == "__main__":
    print("=== Drawing Circuits ===\n")
    print("[1/2] Novel approach (single RUS block)...")
    draw_rus_block()
    print("[2/2] Old approach k=2 (2 RUS blocks)...")
    draw_old_approach_k2()
    print("\n✓ Circuits saved to results/")
