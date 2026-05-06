# Resource-Efficient Quantum Neuron

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.x-purple)](https://qiskit.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Qiskit implementation and comparison of the **Old** and **Novel** quantum neuron approaches from:

> **"Resource-efficient Quantum Neuron for Quantum Neural Networks"**  
> Shivam Maheshwari, Shu-Chen Li, Riccardo Bassoli, Frank H. P. Fitzek  
> *IEEE Globecom Workshop on 6G Innovations and Emerging Technologies, 2023*  
> DOI: [10.1109/GCWKSHPS58843.2023.10464884](https://doi.org/10.1109/GCWKSHPS58843.2023.10464884)

---

## Background

Classical Neural Networks (CNNs) rely on **non-linear activation functions** (e.g. sigmoid, ReLU) to model complex patterns. Implementing equivalent non-linearity on quantum computers is non-trivial since quantum circuits are inherently linear (unitary).

This work uses a **Repeat Until Success (RUS)** quantum circuit to produce a non-linear activation function as a conditional measurement probability, inspired by the neuronal *gain control* model from computational neuroscience.

### The two approaches

| | Old Approach | Novel Approach |
|---|---|---|
| **Function** | $f(\theta, k) = \sin^2(\arctan(\tan^{2^k}(\theta)))$ | $g(\theta, k) = \sin^2(\arctan(\tan^2(k\theta)))$ |
| **Qubits required** | $2^k$ (exponential) | **2 (constant)** |
| **CX gates required** | $2k - 1$ (linear) | **1 (constant)** |
| **Enhancement mechanism** | Stack $k$ RUS blocks | Scale angle $\theta \to k\theta$ |

The novel approach achieves **equivalent or better activation enhancement** with **constant quantum resources** — a key advantage on noisy near-term quantum hardware.

---

## Repository structure

```
quantum-neuron/
├── src/
│   └── quantum_neuron.py       # Core: circuits, theoretical functions, resource counts
├── compare_approaches.py       # Main script: generates all comparison plots
├── visualise_circuits.py       # Draws and saves Qiskit circuit diagrams
├── results/                    # Generated figures (created on run)
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/<your-username>/quantum-neuron.git
cd quantum-neuron

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full comparison (generates all figures in results/)
python compare_approaches.py

# 4. Draw the quantum circuits
python visualise_circuits.py
```

---

## Generated figures

| File | Description |
|---|---|
| `results/01_activation_functions_old.png` | $f(\theta, k)$ for $k = 1 \ldots 5$ |
| `results/02_activation_functions_novel.png` | $g(\theta, k)$ for $k = 1.0 \ldots 2.0$ |
| `results/03_resource_comparison.png` | Qubit & CX gate scaling (old vs novel) |
| `results/04_simulation_vs_theory.png` | Noisy simulator vs theoretical curves (Fig. 9 style) |
| `results/05_side_by_side_comparison.png` | Full 4-panel summary |
| `results/circuit_novel_rus_block.png` | Novel approach RUS circuit diagram |
| `results/circuit_old_approach_k2.png` | Old approach k=2 circuit diagram |

---

## Key equations

**Single RUS block action** (Eq. 6 in paper):

$$\text{RUS}(\theta)|0\rangle|\psi\rangle \to \rho(\theta)|0\rangle e^{-i\arctan(\tan^2\theta)X}|\psi\rangle + \sqrt{1-\rho(\theta)^2}|1\rangle e^{-i\frac{\pi}{4}X}|\psi\rangle$$

where $\rho^2(\theta) = \sin^4\theta + \cos^4\theta$ is the success probability.

**Novel activation function** (Eq. 12 in paper):

$$g(\theta, k) = \sin^2\!\left(\arctan\!\left(\tan^2(k\theta)\right)\right)$$

---

## Running on real IBM hardware

To run on a real IBM quantum backend, replace the `AerSimulator` in `compare_approaches.py` with an IBM runtime backend:

```python
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService(channel="ibm_quantum", token="YOUR_TOKEN")
backend = service.backend("ibm_nairobi")  # or any available backend
```

---

## Citation

```bibtex
@inproceedings{maheshwari2023quantum,
  title     = {Resource-efficient Quantum Neuron for Quantum Neural Networks},
  author    = {Maheshwari, Shivam and Li, Shu-Chen and Bassoli, Riccardo and Fitzek, Frank H. P.},
  booktitle = {2023 IEEE Globecom Workshops (GC Wkshps)},
  pages     = {1045--1050},
  year      = {2023},
  doi       = {10.1109/GCWKSHPS58843.2023.10464884}
}
```

---

## License

MIT — see [LICENSE](LICENSE).
