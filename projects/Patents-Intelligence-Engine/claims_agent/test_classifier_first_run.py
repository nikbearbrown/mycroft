"""
test_classifier_first_run.py — the first real test of claim_classifier.py,
using a known independent claim (US-11791319-B2 Claim 1) so we can read
the result by hand and judge whether the classification actually makes
sense before trusting this for anything downstream.
"""
from claim_classifier import classify_claim

# Real claim text, pulled and verified earlier today.
claim_1_text = """A semiconductor system, comprising:
at least first and second integrated circuit packages, each of the packages
comprising a substrate assembly having generally planar top and bottom sides
and an edge surface, wherein the edge surface extends between the top and
bottom sides and is oriented substantially orthogonally to planes of the top
and bottom sides, and wherein each of the substrate assemblies comprises edge
contacts disposed on the edge surface of the respective substrate assembly
and facing in a direction substantially orthogonal to the edge surface;
a printed circuit board ("PCB") to which the first and second integrated
circuit packages are coupled; and
package-to-package conductive paths coupling edge contacts of the first
integrated circuit package with edge contacts of at least the second
integrated circuit package, wherein the package-to-package conductive paths
do not include traces on or inside the PCB."""

print("Classifying Claim 1 of US-11791319-B2...\n")
result = classify_claim(claim_number=1, claim_text=claim_1_text)

print(f"Claim {result.claim_number}")
print(f"Breadth: {result.breadth}")
print(f"Posture: {result.posture}")
print(f"Reasoning: {result.reasoning}")
print(f"Confidence caveat: {result.confidence_caveat}")
